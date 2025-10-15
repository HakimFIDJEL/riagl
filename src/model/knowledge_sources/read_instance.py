from knowledge_sources.abstract_knowledge_source import AbstractKnowledgeSource

class ReadInstance(AbstractKnowledgeSource):
    """
    Reads an instance file, and stores it in Blackboard.

    Input: Path to instance file (csv)
    Output: blackboard.instance
    """

    def verify(self):
        # No process, so no verification yet.
        return True

    def process(self):
        # Does nothing for the moment.
        return self.blackboard