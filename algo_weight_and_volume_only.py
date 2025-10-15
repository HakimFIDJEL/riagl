# algo_weight_and_volume_only.py
import pickle
from read_instance import Instance  # Import the Instance class

with open("instance.pkl", "rb") as f:
	instance = pickle.load(f)

print(instance)
print(f"\nFirst 2 orders: {instance.orders[:2]}")
print(f"\nFirst 5 arcs: {instance.arcs[:5]}")
print(f"\nFirst 3 locations: {instance.location_coordinates[:3]}")


# TODO

# Trier une liste de produits par poids et volume additionnés en prenant en compte les quantités

# Remplir une liste de colis avec pour chaque colis le maximum de produits possibles sans dépasser poids et volume en
# vidant la liste de produits initiale

def sort_products_by_weight_and_volume_and_quantity(products):
	return sorted(products, key=lambda p: (p['weight'] + p['volume']) * p['quantity'], reverse=True)


def fill_boxes_with_products(products, max_weight, max_volume):
	boxes = []
	while products:
		box = []
		current_weight = 0
		current_volume = 0
		for product in products[:]:  # Iterate over a copy of the list
			if current_weight + product['weight'] <= max_weight and current_volume + product['volume'] <= max_volume:
				box.append(product)
				current_weight += product['weight']
				current_volume += product['volume']
				products.remove(product)
		boxes.append(box)
	return boxes

# Example usage
sorted_products = sort_products_by_weight_and_volume_and_quantity(instance.products)
boxes = fill_boxes_with_products(sorted_products, max_weight=50, max_volume=100)
print(f"\nNumber of boxes filled: {len(boxes)}")
for i, box in enumerate(boxes):
	print(f"Box {i+1}: {box}")