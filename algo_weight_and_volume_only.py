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
from typing import List, Dict, Tuple
from read_instance import Instance


# ----------------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------------

class PackingItem:
	"""Représente un produit à emballer."""

	def __init__(self, idx: int, order_id: int, location: int, weight: float, volume: float, quantity: int):
		self.idx = idx
		self.order_id = order_id
		self.location = location
		self.weight = weight
		self.volume = volume
		self.quantity = quantity

	def __repr__(self):
		return f"<Item idx={self.idx} order={self.order_id} q={self.quantity} w={self.weight} v={self.volume} loc={self.location}>"


class Box:
	"""Représente une boîte contenant plusieurs produits."""

	def __init__(self, max_weight: float, max_volume: float, order_id: int):
		self.max_weight = max_weight
		self.max_volume = max_volume
		self.order_id = order_id
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
			"volume": item.volume,
			"location": item.location
		})
		self.current_weight += item.weight * qty
		self.current_volume += item.volume * qty

	def __repr__(self):
		return f"<Box order={self.order_id} w={self.current_weight}/{self.max_weight} v={self.current_volume}/{self.max_volume} items={len(self.contents)}>"


class PackingManager:
	"""Gère le processus complet de tri et de remplissage des boîtes, par commande."""

	def __init__(self, max_weight: float, max_volume: float):
		self.max_weight = max_weight
		self.max_volume = max_volume

	@staticmethod
	def from_instance(instance) -> Dict[int, dict]:
		"""Extrait les produits (avec quantités) à partir d'une instance chargée, groupés par commande."""
		items_by_order = {}
		for order in instance.orders:
			order_id = order['idx']  # Utilise 'idx' pour l'identifiant de la commande
			max_boxes = order['m']  # Utilise 'm' pour le nombre maximal de colis
			items_by_order[order_id] = {
				"max_boxes": max_boxes,
				"items": []
			}
			for line in order.get("products", []):
				prod = line.get("product", {})
				qty = line.get("quantity", 0)
				if not prod:
					continue
				items_by_order[order_id]["items"].append(
					PackingItem(
						idx=prod.get("idx"),
						order_id=order_id,
						location=prod.get("location"),
						weight=prod.get("weight", 0),
						volume=prod.get("volume", 0),
						quantity=qty,
					)
				)
		return items_by_order

	@staticmethod
	def sort_items(items: List[PackingItem]):
		"""Trie les produits par (poids + volume) * quantité (ordre décroissant)."""
		items.sort(key=lambda i: (i.weight + i.volume) * i.quantity, reverse=True)

	def fill_boxes_for_order(self, order_id: int, items: List[PackingItem], max_boxes: int) -> List[Box]:
		"""Remplit les boîtes pour une commande donnée, en respectant M_c."""
		boxes: List[Box] = []
		remaining_items = [i for i in items]
		while any(i.quantity > 0 for i in remaining_items) and len(boxes) < max_boxes:
			box = Box(self.max_weight, self.max_volume, order_id)
			for item in remaining_items:
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
			if box.contents:
				boxes.append(box)
		return boxes

	def fill_boxes(self, items_by_order: Dict[int, dict]) -> List[Box]:
		"""Remplit les boîtes pour toutes les commandes."""
		all_boxes = []
		for order_id, data in items_by_order.items():
			self.sort_items(data["items"])
			boxes = self.fill_boxes_for_order(order_id, data["items"], data["max_boxes"])
			all_boxes.extend(boxes)
		return all_boxes

	@staticmethod
	def summary(boxes: List[Box], max_weight: float, max_volume: float):
		"""Retourne un résumé global du remplissage."""
		total_weight = sum(b.current_weight for b in boxes)
		total_volume = sum(b.current_volume for b in boxes)
		capacity_weight = len(boxes) * max_weight
		capacity_volume = len(boxes) * max_volume
		summary = {
			"nb_boxes": len(boxes),
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


class Trolley:
	"""Représente un chariot contenant plusieurs boîtes."""

	def __init__(self, max_boxes: int):
		self.max_boxes = max_boxes
		self.boxes: List[Box] = []
		self.total_distance = 0.0

	def can_add_box(self) -> bool:
		"""Vérifie si on peut ajouter une boîte au chariot."""
		return len(self.boxes) < self.max_boxes

	def add_box(self, box: Box):
		"""Ajoute une boîte au chariot."""
		if self.can_add_box():
			self.boxes.append(box)

	def calculate_tour_distance(self, shortest_paths: Dict[tuple, int], s: int, t: int) -> float:
		"""Calcule la distance de la tournée pour ce chariot."""
		# Collecter toutes les localisations uniques des produits dans les boîtes
		locations = set()
		for box in self.boxes:
			for item in box.contents:
				locations.add(item["location"])

		# Ordonner les localisations selon le sens de parcours imposé
		sorted_locations = sorted(locations)

		# Calculer la distance de la tournée
		distance = 0.0
		if sorted_locations:
			# Distance de s à la première localisation
			distance += shortest_paths.get((s, sorted_locations[0]), float('inf'))
			# Distance entre les localisations consécutives
			for i in range(len(sorted_locations) - 1):
				distance += shortest_paths.get((sorted_locations[i], sorted_locations[i + 1]), float('inf'))
			# Distance de la dernière localisation à t
			distance += shortest_paths.get((sorted_locations[-1], t), float('inf'))

		self.total_distance = distance
		return distance


def batch_boxes(boxes: List[Box], K: int, shortest_paths: Dict[Tuple[int, int], int], s: int, t: int) -> List[Trolley]:
    trolleys = []
    remaining_boxes = boxes.copy()
    print(f"Début du batching avec {len(remaining_boxes)} boîtes et K={K}")

    while remaining_boxes:
        trolley = Trolley(K)
        print(f"\nNouveau chariot (reste {len(remaining_boxes)} boîtes)")

        # Ajouter la première boîte
        if remaining_boxes:
            trolley.add_box(remaining_boxes.pop(0))
            print(f"  Ajoutée boîte 1, reste {len(remaining_boxes)} boîtes")

        # Trouver les K-1 boîtes les plus proches
        while trolley.can_add_box() and remaining_boxes:
            best_box = None
            best_distance = float('inf')

            for i, box in enumerate(remaining_boxes):
                current_locations = set()
                for b in trolley.boxes:
                    for item in b.contents:
                        current_locations.add(item["location"])

                box_locations = {item["location"] for item in box.contents}

                # Calcul simplifié pour éviter les blocages
                total_distance = 0.0
                count = 0
                for loc1 in current_locations:
                    for loc2 in box_locations:
                        distance = shortest_paths.get((loc1, loc2), float('inf'))
                        if distance == float('inf'):
                            distance = 1e6  # Valeur par défaut si chemin inconnu
                        total_distance += distance
                        count += 1

                avg_distance = total_distance / count if count > 0 else float('inf')

                if avg_distance < best_distance:
                    best_distance = avg_distance
                    best_box = i

            if best_box is not None:
                trolley.add_box(remaining_boxes.pop(best_box))
                print(f"  Ajoutée boîte {len(trolley.boxes)}, reste {len(remaining_boxes)} boîtes")

        trolley.calculate_tour_distance(shortest_paths, s, t)
        trolleys.append(trolley)
        print(f"Chariot terminé avec {len(trolley.boxes)} boîtes")

    print(f"Batching terminé : {len(trolleys)} chariots créés")
    return trolleys

def calculate_total_distance(trolleys: List[Trolley]) -> float:
    """Calcule la distance totale parcourue par tous les chariots."""
    return sum(trolley.total_distance for trolley in trolleys)


# ----------------------------------------------------------------------
# MAIN — Exécution directe
# ----------------------------------------------------------------------
if __name__ == "__main__":
	print("Chargement de l'instance depuis instance.pkl...")
	with open("instance.pkl", "rb") as f:
		instance = pickle.load(f)

	max_weight, max_volume = instance.capa_box
	print(f"Capacité de boîte : poids={max_weight}, volume={max_volume}")

	# Extraction et configuration
	items_by_order = PackingManager.from_instance(instance)
	print(f"Instance chargée : {sum(len(data['items']) for data in items_by_order.values())} produits trouvés")

	# Création du gestionnaire et traitement
	manager = PackingManager(max_weight, max_volume)
	boxes = manager.fill_boxes(items_by_order)

	# Résumé global
	summary = PackingManager.summary(boxes, max_weight, max_volume)

	# Affichage des 5 premières boîtes
	print("\nLISTE DES 5 PREMIÈRES BOÎTES :")
	for i, box in enumerate(boxes[:5], start=1):
		print(f"\n───────────────────────────────")
		print(f"Boîte {i} (Commande {box.order_id})")
		print(f"  Poids : {box.current_weight}/{box.max_weight}")
		print(f"  Volume : {box.current_volume}/{box.max_volume}")
		print(f"  Contenu ({len(box.contents)} produits) :")
		for item in box.contents:
			print(f"    - Produit {item['idx']} ×{item['count']}  (poids={item['weight']}, volume={item['volume']})")

	# Regrouper les boîtes en chariots
	shortest_paths = {(path['loc_start'], path['loc_end']): path['shortest_path'] for path in instance.shortest_paths}
	s = instance.departing_depot
	t = instance.arrival_depot
	K = instance.nb_boxes_trolley

	trolleys = batch_boxes(boxes, K, shortest_paths, s, t)

	# Afficher les chariots et leur distance
	print("\nDÉTAILS DES CHARIOTS :")
	for i, trolley in enumerate(trolleys, start=1):
		print(f"\n───────────────────────────────")
		print(f"Chariot {i} (Distance totale: {trolley.total_distance:.2f} mètres)")

		# Afficher les boîtes et leurs contenus
		print(f"  Boîtes ({len(trolley.boxes)}/{K}) :")
		for box in trolley.boxes:
			print(f"    - Boîte pour Commande {box.order_id} :")
			for item in box.contents:
				print(f"      - Produit {item['idx']} (×{item['count']}) @Localisation {item['location']}")

		# Afficher la tournée et les distances entre étapes
		locations = set()
		for box in trolley.boxes:
			for item in box.contents:
				locations.add(item["location"])
		sorted_locations = sorted(locations)
		print(f"  Tournée : {' -> '.join(map(str, [s] + sorted_locations + [t]))}")

		if sorted_locations:
			print("  Distances entre étapes :")
			previous_loc = s
			for loc in sorted_locations + [t]:
				distance = shortest_paths.get((previous_loc, loc), float('inf'))
				print(f"    - {previous_loc} → {loc} : {distance:.2f} mètres")
				previous_loc = loc

	# Distance totale
	total_distance = calculate_total_distance(trolleys)
	print(f"\nDistance totale parcourue par tous les chariots : {total_distance:.2f} m")

	# Sauvegarder les résultats
	result_data = {
		"boxes": boxes,
		"trolleys": trolleys,
		"summary": summary,
		"config": {
			"max_weight": max_weight,
			"max_volume": max_volume,
			"K": K
		}
	}
	with open("batching_result.pkl", "wb") as f:
		pickle.dump(result_data, f)
	print("\nRésultats de batching sauvegardés dans 'batching_result.pkl'")
