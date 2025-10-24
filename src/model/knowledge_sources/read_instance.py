from knowledge_sources.abstract_knowledge_source import AbstractKnowledgeSource
from utils.instance import Instance
import os

class ReadInstance(AbstractKnowledgeSource):
    """
    Reads an instance file, and stores it in Blackboard.

    Input: blackboard.instance_path
    Output: blackboard.instance
    """

    def verify(self):
        # Attributes existence
        if not hasattr(self.blackboard, 'instance_path'):
            print("Blackboard does not have attribute 'instance_path'")
            return False
        
        # if var is empty
        if not self.blackboard.instance_path:
            print("Blackboard attribute 'instance_path' is empty")
            return False
        
        # if not a file
        if not os.path.isfile(self.blackboard.instance_path):
            print(f"File '{self.blackboard.instance_path}' does not exist")
            return False

        return True

    def process(self):
        # Variables
        self.nb_locations = None
        self.nb_products = None
        self.nb_boxes_trolley = None
        self.nb_dimensions_capacity = None
        self.capa_box = None
        self.mixed_orders_allowed = None
        self.products = []
        self.nb_orders = None
        self.orders = []
        self.graph = {}
        self.graph["nb_vertices_intersections"] = None
        self.graph["departing_depot"] = None
        self.graph["arrival_depot"] = None
        self.graph["arcs"] = []
        self.graph["shortest_distances"] = []
        self.graph["locations"] = []

        # Read file
        with open(self.blackboard.instance_path, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
           
        # Parse
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.startswith('//NbLocations'):
                i += 1
                self.nb_locations = int(lines[i])
                
            elif line.startswith('//NbProducts'):
                i += 1
                self.nb_products = int(lines[i])
                
            elif line.startswith('//K: NbBoxesTrolley'):
                i += 1
                self.nb_boxes_trolley = int(lines[i])
                
            elif line.startswith('//NbDimensionsCapacity'):
                i += 1
                self.nb_dimensions_capacity = int(lines[i])
                
            elif line.startswith('//B: CapaBox'):
                i += 1
                self.capa_box = list(map(int, lines[i].split()))
                
            elif line.startswith('//A box can accept mixed orders'):
                i += 1
                self.mixed_orders_allowed = bool(int(lines[i]))
                
            elif line.startswith('//Products'):
                i += 1  # Skip comment line
                if i < len(lines) and lines[i].startswith('//Idx'):
                    i += 1  # Skip header line
                
                # Read all products
                while i < len(lines) and not lines[i].startswith('//'):
                    parts = list(map(int, lines[i].split()))
                    if len(parts) >= 4:  # Idx, Location, Weight, Volume, ...
                        product = {
                            'id': parts[0],
                            'id_loc': parts[1],
                            'w': parts[2],
                            'v': parts[3]
                        }
                        self.products.append(product)
                    i += 1
                continue  # Skip the i += 1 at the end of the loop
                
            elif line.startswith('//NbOrders'):
                i += 1
                self.nb_orders = int(lines[i])
                i += 1
                if i < len(lines) and lines[i].startswith('//Idx'):
                    i += 1  # Skip header line
                
                # Read all orders
                while i < len(lines) and not lines[i].startswith('//'):
                    parts = list(map(int, lines[i].split()))
                    if len(parts) >= 3:  # Idx, M, NbProdInOrder, ...
                        order = {
                            'id': parts[0],
                            'mc': parts[1],
                            'nb_prod_in_order': parts[2],
                            'products': []
                        }
                        # Parse product-quantity pairs
                        for j in range(3, len(parts), 2):
                            if j + 1 < len(parts):
                                prod_idx = parts[j]
                                quantity = parts[j + 1]
                                # Trouver le produit correspondant
                                # dans self.products
                                product_info = next((p for p in self.products \
                                                     if p['id'] == prod_idx),
                                                     None)
                                if product_info:
                                    order['products'].append({
                                        'quantity': quantity,
                                        'product': product_info
                                    })
                                else:
                                    # En cas d’erreur (produit non trouvé)
                                    order['products'].append({
                                        'quantity': quantity,
                                        'product': {
                                            'idx': prod_idx,
                                            'error': 'Product not found'
                                        }
                                    })
                        self.orders.append(order)
                    i += 1
                continue

            elif line.startswith('//NbVerticesIntersections'):
                i += 1
                self.graph["nb_vertices_intersections"] = int(lines[i])
                
            elif line.startswith('//DepartingDepot'):
                i += 1
                self.graph["departing_depot"] = int(lines[i])
                
            elif line.startswith('//ArrivalDepot'):
                i += 1
                self.graph["arrival_depot"] = int(lines[i])
                
            elif line.startswith('//Arcs'):
                i += 1
                if i < len(lines) and lines[i].startswith('//Start'):
                    i += 1  # Skip header line
                
                # Read all arcs
                while i < len(lines) and not lines[i].startswith('//'):
                    parts = list(map(int, lines[i].split()))
                    if len(parts) >= 3:  # Start, End, Distance
                        arc = {
                            'idDeparture': parts[0],
                            'idArrival': parts[1],
                            'distance': parts[2]
                        }
                        self.graph["arcs"].append(arc)
                    i += 1
                continue
                
            elif line.startswith('//LocStart LocEnd ShortestPath'):
                i += 1
                # Read shortest paths
                while i < len(lines) and not lines[i].startswith('//'):
                    parts = list(map(int, lines[i].split()))
                    if len(parts) >= 3:  # LocStart, LocEnd, ShortestPath
                        path = {
                            'idDeparture': parts[0],
                            'idArrival': parts[1],
                            'distance': parts[2]
                        }
                        self.graph["shortest_distances"].append(path)
                    i += 1
                continue
                
            elif line.startswith('//Location coordinates LocationName'):
                i += 1
                if i < len(lines) and lines[i].startswith('//Loc'):
                    i += 1  # Skip header line
                
                # Read location coordinates
                while i < len(lines) and not lines[i].startswith('//'):
                    # Handle format: loc_id x y "name"
                    parts = lines[i].split()
                    if len(parts) >= 4:
                        location = {
                            'id': int(parts[0]),
                            'x': int(parts[1]),
                            'y': int(parts[2]),
                            'name': ' '.join(parts[3:]).strip('"')
                        }
                        self.graph["locations"].append(location)
                    i += 1
                continue
                
            i += 1

        # Create an instance object
        instance = Instance(
            self.nb_locations,
            self.nb_products,
            self.nb_boxes_trolley,
            self.nb_dimensions_capacity,
            self.capa_box,
            self.mixed_orders_allowed,
            self.products,
            self.nb_orders,
            self.orders,
            self.graph
        )

        # Store it in Blackboard
        self.blackboard.instance = instance

        return self.blackboard