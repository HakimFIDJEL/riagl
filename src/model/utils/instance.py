class Instance:
    def __init__(self, nb_locations, nb_products, nb_boxes_trolley,
                 nb_dimensions_capacity, capa_box, mixed_orders_allowed,
                 products, nb_orders, orders, graph):
        self.nb_locations = nb_locations
        self.nb_products = nb_products
        self.nb_boxes_trolley = nb_boxes_trolley
        self.nb_dimensions_capacity = nb_dimensions_capacity
        self.capa_box = capa_box
        self.mixed_orders_allowed = mixed_orders_allowed
        self.products = products
        self.nb_orders = nb_orders
        self.orders = orders
        self.graph = graph