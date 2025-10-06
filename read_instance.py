class Instance:
    def __init__(self, filename=None):
        # Initialize all attributes
        self.nb_locations = None
        self.nb_products = None
        self.nb_boxes_trolley = None
        self.nb_dimensions_capacity = None
        self.capa_box = None
        self.mixed_orders_allowed = None
        self.products = []
        self.nb_orders = None
        self.orders = []
        self.nb_vertices_intersections = None
        self.departing_depot = None
        self.arrival_depot = None
        self.arcs = []
        self.shortest_paths = []
        self.location_coordinates = []
        
        if filename:
            self.read_from_file(filename)
    
    def read_from_file(self, filename):
        with open(filename, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
        
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
                    if len(parts) >= 4:  # Idx, Location, Dim1, Dim2, ...
                        product = {
                            'idx': parts[0],
                            'location': parts[1],
                            'dimensions': parts[2:]
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
                            'idx': parts[0],
                            'm': parts[1],
                            'nb_prod_in_order': parts[2],
                            'products': []
                        }
                        # Parse product-quantity pairs
                        for j in range(3, len(parts), 2):
                            if j + 1 < len(parts):
                                order['products'].append({
                                    'product_idx': parts[j],
                                    'quantity': parts[j + 1]
                                })
                        self.orders.append(order)
                    i += 1
                continue
                
            elif line.startswith('//NbVerticesIntersections'):
                i += 1
                self.nb_vertices_intersections = int(lines[i])
                
            elif line.startswith('//DepartingDepot'):
                i += 1
                self.departing_depot = int(lines[i])
                
            elif line.startswith('//ArrivalDepot'):
                i += 1
                self.arrival_depot = int(lines[i])
                
            elif line.startswith('//Arcs'):
                i += 1
                if i < len(lines) and lines[i].startswith('//Start'):
                    i += 1  # Skip header line
                
                # Read all arcs
                while i < len(lines) and not lines[i].startswith('//'):
                    parts = list(map(int, lines[i].split()))
                    if len(parts) >= 3:  # Start, End, Distance
                        arc = {
                            'start': parts[0],
                            'end': parts[1],
                            'distance': parts[2]
                        }
                        self.arcs.append(arc)
                    i += 1
                continue
                
            elif line.startswith('//LocStart LocEnd ShortestPath'):
                i += 1
                # Read shortest paths
                while i < len(lines) and not lines[i].startswith('//'):
                    parts = list(map(int, lines[i].split()))
                    if len(parts) >= 3:  # LocStart, LocEnd, ShortestPath
                        path = {
                            'loc_start': parts[0],
                            'loc_end': parts[1],
                            'shortest_path': parts[2]
                        }
                        self.shortest_paths.append(path)
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
                        self.location_coordinates.append(location)
                    i += 1
                continue
                
            i += 1
    
    # Setter methods
    def set_nb_locations(self, value):
        self.nb_locations = value
    
    def set_nb_products(self, value):
        self.nb_products = value
    
    def set_nb_boxes_trolley(self, value):
        self.nb_boxes_trolley = value
    
    def set_nb_dimensions_capacity(self, value):
        self.nb_dimensions_capacity = value
    
    def set_capa_box(self, value):
        self.capa_box = value
    
    def set_mixed_orders_allowed(self, value):
        self.mixed_orders_allowed = value
    
    def set_nb_orders(self, value):
        self.nb_orders = value
    
    def set_nb_vertices_intersections(self, value):
        self.nb_vertices_intersections = value
    
    def set_departing_depot(self, value):
        self.departing_depot = value
    
    def set_arrival_depot(self, value):
        self.arrival_depot = value
    
    def add_product(self, idx, location, dimensions):
        product = {
            'idx': idx,
            'location': location,
            'dimensions': dimensions
        }
        self.products.append(product)
    
    def add_order(self, idx, m, nb_prod_in_order, products):
        order = {
            'idx': idx,
            'm': m,
            'nb_prod_in_order': nb_prod_in_order,
            'products': products
        }
        self.orders.append(order)
    
    def add_arc(self, start, end, distance):
        arc = {
            'start': start,
            'end': end,
            'distance': distance
        }
        self.arcs.append(arc)
    
    def add_shortest_path(self, loc_start, loc_end, shortest_path):
        path = {
            'loc_start': loc_start,
            'loc_end': loc_end,
            'shortest_path': shortest_path
        }
        self.shortest_paths.append(path)
    
    def add_location_coordinate(self, id, x, y, name):
        location = {
            'id': id,
            'x': x,
            'y': y,
            'name': name
        }
        self.location_coordinates.append(location)
    
    def __str__(self):
        return f"""Instance:
  Locations: {self.nb_locations}
  Products: {self.nb_products}
  Boxes per Trolley: {self.nb_boxes_trolley}
  Capacity Dimensions: {self.nb_dimensions_capacity}
  Box Capacity: {self.capa_box}
  Mixed Orders Allowed: {self.mixed_orders_allowed}
  Products Count: {len(self.products)}
  Orders Count: {len(self.orders)}
  Vertices Intersections: {self.nb_vertices_intersections}
  Departing Depot: {self.departing_depot}
  Arrival Depot: {self.arrival_depot}
  Arcs Count: {len(self.arcs)}
  Shortest Paths Count: {len(self.shortest_paths)}
  Locations Count: {len(self.location_coordinates)}"""

# Usage
if __name__ == "__main__":
    instance = Instance("instances_exemple/instance_0116_131933_Z1.txt")
    print(instance)
    print(f"\nFirst 2 orders: {instance.orders[:2]}")
    print(f"\nFirst 5 arcs: {instance.arcs[:5]}")
    print(f"\nFirst 3 locations: {instance.location_coordinates[:3]}")