import os
from FlowAgents.conversation_flow.importance_message import ImportanceMessage
from FlowAgents.conversation_flow.message_role import MessageRole

KNOWLEDGE_IMPORTANCE = 999

class Knowledge(ImportanceMessage):
    def __init__(self, content: str, importance: int = KNOWLEDGE_IMPORTANCE):
        super().__init__(importance, MessageRole.DEVELOPER, content)

    def __str__(self):
        return self.content

class AgentsKnowledge:
    def __init__(self, files_folder_path: str = "files"):
        self.files_folder_path = files_folder_path

    def _get_files(self, path: str):
        return os.listdir(path)

    def _get_file_content(self, file_name: str):
        with open(os.path.join(self.files_folder_path, file_name), "r") as file:
            return file.read()
        
    def get_knowledge(self, path: str) -> list[Knowledge]:
        """
        Get the knowledge from the path
        @param path: the path to get the knowledge from
        @return: a list of Knowledge objects
        """
        if(os.path.isfile(path)):
            return [Knowledge(self._get_file_content(path))] # if the path is a file, return a list with the file content
        files = self._get_files(path)
        return [Knowledge(self._get_file_content(file)) for file in files] # if the path is a folder, return a list with the file contents