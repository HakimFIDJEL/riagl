import os

# Produit dans un carton
class BoxeProduct:
    def __init__(self, product_id: int, quantity: int) -> None:
        # (integer) Identifiant du produit
        self.product_id : int = product_id
        # (integer) Quantité de produit mis dans le carton
        self.quantity : int = quantity

# Carton
class Boxe:
    def __init__(self, id: int, order_id: int, weight: int, volume: int, boxe_products: list[BoxeProduct]) -> None:
        # (integer) Identifiant unique du carton
        self.id : int = id
        # (integer) Identifiant de la commande
        self.order_id : int = order_id
        # (integer) Poids du carton
        self.weight : int = weight
        # (integer) Volume du carton
        self.volume : int = volume
        # (BoxeProduct) Information sur les produits dans un carton
        self.boxe_products : list[BoxeProduct] = boxe_products

# Commande  
class Order:
    def __init__(self, id: int, nbr_boxes: int) -> None:
        # (integer) Identifiant de la commande
        self.id : int = id
        # (integer) Nombre de cartons associés
        self.nbr_boxes : int = nbr_boxes

# Tournée
class Tour:
    def __init__(self, id: int, boxes: list[Boxe]) -> None:
        # (integer) Identifiant de la tournée
        self.id: int = id
        # (Boxes) Information sur les colis
        self.boxes : list[Boxe] = boxes

# Variable de sortie
class Output:
    def __init__(self, filename: str, travelled_distance: int, crossed_locations: int, avg_weight: int, avg_volume: int, tours: list[Tour], orders: list[Order]) -> None:
        # (integer) Distance parcourue au total par le picker
        self.travelled_distance : int = travelled_distance
        # (integer) Nombre de points où le picker s’est arrêté / a traversé
        self.crossed_locations : int = crossed_locations
        # (integer) Pourcentage de poids des colis par rapport au max
        self.avg_weight : int = avg_weight
        # (integer) Pourcentage de volume des colis par rapport au max
        self.avg_volume : int = avg_volume
        # (Tours) Informations sur les tournées
        self.tours : list[Tour] = tours
        # (Orders) Information sur les commandes
        self.orders : list[Order] = orders
        # (str) Nom du fichier d'instance
        self.filename = filename

    def __str__(self) -> str:
        return f"Output(distance={self.travelled_distance}, stops={self.crossed_locations}, orders={len(self.orders)}, tournées={len(self.tours)})"
    
    def _solution_path(self) -> str:
        # nomInstance.txt -> solutions/nomInstance_sol.txt
        base = os.path.basename(self.filename)
        root, _ = os.path.splitext(base)
        return os.path.join("solutions", f"{root}_sol.txt")
    
    def write_solution_file(self) -> str:
        """
        Écrit le fichier solution au format exigé dans solutions/<filename>_sol.txt.
        Format:
        //NbTournees
        <nbTours>
        //IdTournes NbColis
        <tourId> <nbColis>
        //IdColis IdCommandeInColis NbProducts IdProd1 QtyProd1 ...
        <boxId> <orderId> <nbProducts> <prod1> <qty1> <prod2> <qty2> ...
        (répété pour chaque carton de chaque tournée)
        """
        if not self.tours:
            raise ValueError("Aucune tournée (tours) à exporter.")

        os.makedirs("solutions", exist_ok=True)
        path = self._solution_path()

        lines: list[str] = []
        lines.append("//NbTournees")
        lines.append(str(len(self.tours)))

        for tour in self.tours:
            lines.append("//IdTournes NbColis")
            lines.append(f"{tour.id} {len(tour.boxes)}")
            lines.append("//IdColis IdCommandeInColis NbProducts IdProd1 QtyProd1 IdProd2 QtyProd2 ...")

            for box in tour.boxes:
                nb_products = len(box.boxe_products)
                parts = [str(box.id), str(box.order_id), str(nb_products)]
                for bp in box.boxe_products:
                    parts.extend([str(bp.product_id), str(bp.quantity)])
                # l’exemple a un espace final, on le reproduit
                lines.append(" ".join(parts) + " ")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return path