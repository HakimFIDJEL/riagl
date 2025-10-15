import os

# Produit dans un carton
class BoxeProduct:
    def __init__(self, productId: int, quantity: int) -> None:
        # (integer) Identifiant du produit
        self.productId : int = productId
        # (integer) Quantité de produit mis dans le carton
        self.quantity : int = quantity

# Carton
class Boxe:
    def __init__(self, id: int, orderId: int, weight: int, volume: int, boxeProducts: list[BoxeProduct]) -> None:
        # (integer) Identifiant unique du carton
        self.id : int = id
        # (integer) Identifiant de la commande
        self.orderId : int = orderId
        # (integer) Poids du carton
        self.weight : int = weight
        # (integer) Volume du carton
        self.volume : int = volume
        # (BoxeProduct) Information sur les produits dans un carton
        self.boxeProducts : list[BoxeProduct] = boxeProducts

# Commande  
class Order:
    def __init__(self, id: int, nbrBoxes: int) -> None:
        # (integer) Identifiant de la commande
        self.id : int = id
        # (integer) Nombre de cartons associés
        self.nbrBoxes : int = nbrBoxes
        
# Tournée
class Tour:
    def __init__(self, id: int, boxes: list[Boxe]) -> None:
        # (integer) Identifiant de la tournée
        self.id: int = id
        # (Boxes) Information sur les colis
        self.boxes : list[Boxe] = boxes

# Variable de sortie
class Output:
    def __init__(self, filename: str, travelledDistance: int, crossedLocations: int, avgWeight: int, avgVolume: int, tours: list[Tour], orders: list[Order]) -> None:
        # (integer) Distance parcourue au total par le picker
        self.travelledDistance : int = travelledDistance
        # (integer) Nombre de points où le picker s’est arrêté / a traversé
        self.crossedLocations : int = crossedLocations
        # (integer) Pourcentage de poids des colis par rapport au max
        self.avgWeight : int = avgWeight
        # (integer) Pourcentage de volume des colis par rapport au max
        self.avgVolume : int = avgVolume
        # (Tours) Informations sur les tournées
        self.tours : list[Tour] = tours
        # (Orders) Information sur les commandes
        self.orders : list[Order] = orders
        # (str) Nom du fichier d'instance
        self.filename = filename

    def __str__(self) -> str:
        return f"Output(distance={self.travelledDistance}, stops={self.crossedLocations}, boxes={len(self.boxes)}, tournées={len(self.tours)})"
    
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
                nb_products = len(box.boxeProducts)
                parts = [str(box.id), str(box.orderId), str(nb_products)]
                for bp in box.boxeProducts:
                    parts.extend([str(bp.productId), str(bp.quantity)])
                # l’exemple a un espace final, on le reproduit
                lines.append(" ".join(parts) + " ")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return path