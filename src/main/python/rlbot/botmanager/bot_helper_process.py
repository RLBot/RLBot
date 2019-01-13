from multiprocessing import Event, Queue


class BotHelperProcess:
    """
    This is a base class for a process that can be shared by two or more bots. For example, if those bots are using
    a non-python language like Scratch or Java, the bots will likely want to share a single process that interfaces
    with that other language.
    """

    def __init__(self, metadata_queue: Queue, quit_event: Event, options: dict):
        """
        :param metadata_queue: A multiprocessing queue that receives AgentMetadata objects when
        relevant agents are initialized.
        :param quit_event: A multiprocessing event that will be set when rlbot is trying to quit.
        """
        self.metadata_queue = metadata_queue
        self.quit_event = quit_event
        self.options = options

    def start(self):
        raise NotImplementedError
