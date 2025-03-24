from abc import ABC, abstractmethod
from .message_role import MessageRole
from datetime import datetime
from .utils import Utils
from pydantic import BaseModel
import json

class ImportanceMessage(ABC):

    def __init__(self, importance: int, messagerole: MessageRole, message: str | None = None):
        self.importance = importance
        self.messagerole = messagerole
        self.message = message
        self.token_size = None
        self.created_at = datetime.now()

    def __str__(self):
        # returns a json string of only message
        return json.dumps({
            'role': self.messagerole.value,
            'message': self.message
        })

    def __repr__(self):
        return self.__str__()

    def set_token_size(self, token_size: int):
        self.token_size = token_size

    def get_token_size(self) -> int:
        if(self.token_size is None):
            return Utils.get_approximate_tokens_size(self.message)
        return self.token_size
    
class DeveloperMessage(ImportanceMessage):
    def __init__(self, message: str | None = None):
        """
        Initializes the developer message
        @param message: the message of the developer
        """
        super().__init__(importance=Utils.DEVELOPER_MESSAGE_IMPORTANCE, messagerole=MessageRole.DEVELOPER, message=message)


class ImportanceRequest(ImportanceMessage):

    def __init__(self, importance: int = Utils.DEFAULT_USER_MESSAGE_IMPORTANCE, message: str | None = None):
        """ 
        Initializes the importance request
        @param importance: the importance of the request, if it's negative, it will be removed from the chat flow on next interaction
        @param message: the message of the request
        """
        super().__init__(importance, MessageRole.USER, message)

class ImportanceResponse(ImportanceMessage):

    def __init__(self, importance: int = Utils.DEFAULT_RESPONSE_IMPORTANCE, message: str | None = None):
        """
        Initializes the importance response
        @param importance: the importance of the response, if it's negative, it will be removed from the chat flow on next interaction
        @param message: the message of the response
        """
        super().__init__(importance, MessageRole.ASSISTANT, message)