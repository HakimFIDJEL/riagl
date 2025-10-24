from knowledge_sources.abstract_knowledge_source import AbstractKnowledgeSource
from utils.solution import *

class WriteOutput(AbstractKnowledgeSource):
    """
    Formats output for the checker and writes it in solutions.
    Écrit le fichier solution au format exigé dans solutions/<filename>_sol.txt.
    Format:
    //NbTournees
    <nbTours>
    //IdTournes NbColis
    <tourId> <nbColis>
    //IdColis IdCommandeInColis NbProducts IdProd1 QtyProd1 ...
    <boxId> <orderId> <nbProducts> <prod1> <qty1> <prod2> <qty2> ...
    (répété pour chaque carton de chaque tournée)

    Input: blackboard.output
    Output: blackboard.formatted_output
    """

    def verify(self):
        # Verify that output exists
        if not hasattr(self.blackboard, "output"):
            print("No output found in blackboard.")
            return False

        # Verify that there are tours to export
        if not self.blackboard.output.tours:
            print("No tours found in blackboard.output.tours.")
            return False

        return True

    def process(self):
        # Create solutions directory and path
        os.makedirs("solutions", exist_ok=True)
        path = self.blackboard.instance_path.replace(
            "instances", "solutions"
        ).replace(".txt", "_sol.txt")

        # Generate solution lines
        lines: list[str] = []
        lines.append("//NbTournees")
        lines.append(str(len(self.blackboard.output.tours)))

        for tour in self.blackboard.output.tours:
            lines.append("//IdTournes NbColis")
            lines.append(f"{tour.id} {len(tour.boxes)}")
            lines.append("//IdColis IdCommandeInColis NbProducts IdProd1" \
                "QtyProd1 IdProd2 QtyProd2 ...")

            for box in tour.boxes:
                nb_products = len(box.boxe_products)
                parts = [str(box.id), str(box.order_id), str(nb_products)]
                for bp in box.boxe_products:
                    parts.extend([str(bp.product_id), str(bp.quantity)])
                # l’exemple a un espace final, on le reproduit
                lines.append(" ".join(parts) + " ")

        # Writing in Blackboard
        self.blackboard.formatted_output = {
            "solution_path": path,
            "solution_lines": lines
        }

        # Writing to file
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        
        return self.blackboard