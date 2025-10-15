# packing.py
"""
Module de remplissage de colis basé sur le poids et le volume des produits.

Fonctionnalités :
  - Lecture d'une instance depuis instance.pkl
  - Extraction des produits et quantités
  - Tri des produits selon leur importance logistique
  - Remplissage automatique des boîtes
  - Sauvegarde des résultats complets dans packing_result.pkl
"""

import pickle
from typing import List, Dict
from read_instance import Instance


# ----------------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------------

class PackingItem:
	"""Représente un produit à emballer."""

	def __init__(self, idx: int, location: int, weight: float, volume: float, quantity: int):
		self.idx = idx
		self.location = location
		self.weight = weight
		self.volume = volume
		self.quantity = quantity

	def __repr__(self):
		return f"<Item idx={self.idx} q={self.quantity} w={self.weight} v={self.volume}>"


class Box:
	"""Représente une boîte contenant plusieurs produits."""

	def __init__(self, max_weight: float, max_volume: float):
		self.max_weight = max_weight
		self.max_volume = max_volume
		self.contents: List[Dict] = []
		self.current_weight = 0
		self.current_volume = 0

	def can_fit(self, item: PackingItem, qty: int) -> bool:
		"""Vérifie si la quantité demandée peut tenir dans la boîte."""
		return (
				self.current_weight + item.weight * qty <= self.max_weight
				and self.current_volume + item.volume * qty <= self.max_volume
		)

	def add_item(self, item: PackingItem, qty: int):
		"""Ajoute un produit à la boîte."""
		self.contents.append({
			"idx": item.idx,
			"count": qty,
			"weight": item.weight,
			"volume": item.volume
		})
		self.current_weight += item.weight * qty
		self.current_volume += item.volume * qty

	def __repr__(self):
		return f"<Box w={self.current_weight}/{self.max_weight} v={self.current_volume}/{self.max_volume} items={len(self.contents)}>"


class PackingManager:
	"""Gère le processus complet de tri et de remplissage des boîtes."""

	def __init__(self, items: List[PackingItem], max_weight: float, max_volume: float):
		self.items = items
		self.max_weight = max_weight
		self.max_volume = max_volume
		self.boxes: List[Box] = []

	# ------------------------------------------------------
	# Méthodes principales
	# ------------------------------------------------------

	@staticmethod
	def from_instance(instance) -> List[PackingItem]:
		"""Extrait les produits (avec quantités) à partir d'une instance chargée."""
		items = []
		for order in instance.orders:
			for line in order.get("products", []):
				prod = line.get("product", {})
				qty = line.get("quantity", 0)
				if not prod:
					continue
				items.append(
					PackingItem(
						idx=prod.get("idx"),
						location=prod.get("location"),
						weight=prod.get("weight", 0),
						volume=prod.get("volume", 0),
						quantity=qty,
					)
				)
		return items

	def sort_items(self):
		"""Trie les produits par (poids + volume) * quantité (ordre décroissant)."""
		self.items.sort(key=lambda i: (i.weight + i.volume) * i.quantity, reverse=True)

	def fill_boxes(self):
		"""Remplit les boîtes jusqu’à épuisement des produits."""
		items = [i for i in self.items]
		boxes: List[Box] = []

		while any(i.quantity > 0 for i in items):
			box = Box(self.max_weight, self.max_volume)

			for item in items:
				if item.quantity <= 0:
					continue

				max_by_weight = int(
					(self.max_weight - box.current_weight) // item.weight) if item.weight > 0 else item.quantity
				max_by_volume = int(
					(self.max_volume - box.current_volume) // item.volume) if item.volume > 0 else item.quantity
				possible = min(item.quantity, max_by_weight, max_by_volume)

				if possible > 0 and box.can_fit(item, possible):
					box.add_item(item, possible)
					item.quantity -= possible

				if box.current_weight >= self.max_weight or box.current_volume >= self.max_volume:
					break

			if not box.contents:
				break

			boxes.append(box)

		self.boxes = boxes
		return boxes

	def summary(self):
		"""Retourne un résumé global du remplissage."""
		total_weight = sum(b.current_weight for b in self.boxes)
		total_volume = sum(b.current_volume for b in self.boxes)
		capacity_weight = len(self.boxes) * self.max_weight
		capacity_volume = len(self.boxes) * self.max_volume

		summary = {
			"nb_boxes": len(self.boxes),
			"total_weight": total_weight,
			"total_volume": total_volume,
			"fill_ratio_weight": 100 * total_weight / capacity_weight if capacity_weight > 0 else 0,
			"fill_ratio_volume": 100 * total_volume / capacity_volume if capacity_volume > 0 else 0,
		}

		print("\nRÉSUMÉ DU REMPLISSAGE")
		print(f"Nombre de boîtes : {summary['nb_boxes']}")
		print(f"Poids total : {summary['total_weight']:.2f} / {capacity_weight} ({summary['fill_ratio_weight']:.1f}%)")
		print(f"Volume total : {summary['total_volume']:.2f} / {capacity_volume} ({summary['fill_ratio_volume']:.1f}%)")

		return summary


# ----------------------------------------------------------------------
# MAIN — Exécution directe
# ----------------------------------------------------------------------

if __name__ == "__main__":
	print("Chargement de l'instance depuis instance.pkl...")

	with open("instance.pkl", "rb") as f:
		instance = pickle.load(f)

	# Extraction et configuration
	items = PackingManager.from_instance(instance)
	max_weight, max_volume = instance.capa_box

	print(f"Instance chargée : {len(items)} produits trouvés")
	print(f"Capacité de boîte : poids={max_weight}, volume={max_volume}")

	# Création du gestionnaire et traitement
	manager = PackingManager(items, max_weight, max_volume)
	manager.sort_items()
	boxes = manager.fill_boxes()

	# Résumé global
	summary = manager.summary()

	# # Affichage de toutes les boîtes
	# print("\nLISTE COMPLÈTE DES BOÎTES :")
	# for i, box in enumerate(boxes, start=1):
	#     print(f"\n───────────────────────────────")
	#     print(f"Boîte {i}")
	#     print(f"  Poids : {box.current_weight}/{box.max_weight}")
	#     print(f"  Volume : {box.current_volume}/{box.max_volume}")
	#     print(f"  Contenu ({len(box.contents)} produits) :")
	#     for item in box.contents:
	#         print(f"    - Produit {item['idx']} ×{item['count']}  (poids={item['weight']}, volume={item['volume']})")

	# Affichage des 5 premières boîtes
	print("\nLISTE DES 5 PREMIÈRES BOÎTES :")
	for i, box in enumerate(boxes[:5], start=1):
		print(f"\n───────────────────────────────")
		print(f"Boîte {i}")
		print(f"  Poids : {box.current_weight}/{box.max_weight}")
		print(f"  Volume : {box.current_volume}/{box.max_volume}")
		print(f"  Contenu ({len(box.contents)} produits) :")
		for item in box.contents:
			print(f"    - Produit {item['idx']} ×{item['count']}  (poids={item['weight']}, volume={item['volume']})")

	# Sauvegarde complète du résultat
	result_data = {
		"boxes": boxes,
		"items": items,
		"summary": summary,
		"config": {
			"max_weight": max_weight,
			"max_volume": max_volume
		}
	}

	with open("packing_result.pkl", "wb") as f:
		pickle.dump(result_data, f)

	print("\nRésultats sauvegardés dans 'packing_result.pkl'")
