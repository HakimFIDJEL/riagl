from blackboard.blackboard import Blackboard
from controller.controller import Controller
from knowledge_sources.read_instance import ReadInstance
from knowledge_sources.algoV1 import AlgoV1
from model.knowledge_sources.write_output import WriteOutput

def main():
    instance_file = "src/instances_exemple/instance_0116_131933_Z2.txt"

    # Initialize blackboard and controller
    blackboard = Blackboard()
    controller = Controller(blackboard)

    # Load path of instance
    blackboard.set_instance_path(instance_file)

    # Add knowledge sources
    blackboard.add_knowledge_source(ReadInstance(blackboard))
    #blackboard.add_knowledge_source(AlgoV1(blackboard))
    blackboard.add_knowledge_source(WriteOutput(blackboard))

    # Process and get results
    controller.run_knowledge_sources()

if __name__ == "__main__":
    main()