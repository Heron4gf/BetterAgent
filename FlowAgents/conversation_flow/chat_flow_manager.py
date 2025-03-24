from .importance_message import ImportanceMessage

class ChatFlowManager:

    MAX_CONTEXT_SIZE = 128000 # max context for the model
    CLEAN_THRESHOLD = 0.8 # 80% of the max token size
    MAX_TOKEN_SIZE_THRESHOLD = MAX_CONTEXT_SIZE * CLEAN_THRESHOLD

    # anything with importance == MAX_IMPORTANCE is a developer message and won't be cleaned
    MAX_IMPORTANCE = 2147483647 # max importance for the model

    def __init__(self):
        """
        Initializes the chat flow manager
        """
        self.chat_flow = [] # list of ImportanceMessage objects

    def add_message(self, message: ImportanceMessage):
        """
        Removes all messages with importance < 0, then adds the new message to the chat flow, then triggers cleaning if necessary
        @param message: the message to add
        """
        self.decrement_all_importance_messages()
        self.remove_negative_importance_messages()
        self.chat_flow.append(message)
        self.trigger_cleaning()

    def decrement_all_importance_messages(self):
        """
        Decrements the importance of all messages by 1
        """
        for message in self.chat_flow:
            message.importance -= 1

    def remove_negative_importance_messages(self):
        """
        Removes all messages with importance < 0
        """
        self.chat_flow = [response for response in self.chat_flow if response.importance >= 0]

    def get_total_token_size(self) -> int:
        """
        @return: the total token size of the chat flow
        """
        return sum([response.get_token_size() for response in self.chat_flow])

    def trigger_cleaning(self, threshold: float = CLEAN_THRESHOLD):
        """
        Automatically cleans the chat flow until we are under the threesold
        @param threshold: the threshold to clean the chat flow to
        @return: the total token size of the chat flow
        @return: the total importance of the chat flow
        """

        # automatically cleans the chat flow until we are under the threesold
        if self.get_total_token_size() < self.MAX_TOKEN_SIZE_THRESHOLD:
            return

        cloned_chat_flow = self.chat_flow.copy()
        # sorts the chat flow by importance (least important first) if importance is the same, then by created_at (oldest first)
        cloned_chat_flow.sort(key=lambda message: (message.importance, message.created_at))
        
        cloned_chat_flow = [message for message in cloned_chat_flow if message.importance != self.MAX_IMPORTANCE] # exclude developer messages

        # removes the oldest responses until the total size is less than the threshold
        while self.get_total_token_size() > self.MAX_TOKEN_SIZE_THRESHOLD:
            cloned_chat_flow.pop(0)

        # order again the list by timestamp
        cloned_chat_flow.sort(key=lambda message: message.created_at)
        self.chat_flow = cloned_chat_flow
        


    def serialize(self) -> str:
        """
        Serializes the chat flow to a string
        @return: the serialized chat flow
        """
        return "\n".join(self.to_json_list())
    
    def to_json_list(self) -> list[dict]:
        """
        Converts the chat flow to a list of dictionaries
        @return: the list of dictionaries
        """
        return [message.__str__() for message in self.chat_flow]