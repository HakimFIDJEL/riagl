import os
from blackboard.blackboard import Blackboard
from controller.controller import Controller
from knowledge_sources.read_instance import ReadInstance
from knowledge_sources.algoV1 import AlgoV1

def main():
    # Build absolute path to instance: src/instances_exemple/<file>
    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    instance_file = os.path.join(src_root, "instances_exemple", "instance_0116_131933_Z2.txt")

    # Initialize blackboard and controller
    blackboard = Blackboard()
    controller = Controller(blackboard)

    # Load path of instance
    blackboard.set_instance_path(instance_file)

    # Add knowledge sources
    blackboard.add_knowledge_source(ReadInstance(blackboard))
    blackboard.add_knowledge_source(AlgoV1(blackboard))

    # Process and get results
    controller.run_knowledge_sources()
    # Optional: print a small summary from algorithm output
    if getattr(blackboard, "output", None):
        out = blackboard.output
        print(f"AlgoV1 produced {len(out.get('tours', []))} tours; distance={out.get('travelled_distance', 0)}; stops={out.get('crossed_locations', 0)}")

if __name__ == "__main__":
    main()