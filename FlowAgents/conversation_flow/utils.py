class Utils:
    
    TOKEN_TO_TEXT_RATIO = 0.75 # 1 token = 0.75 words
    TEXT_TO_TOKEN_RATIO = 1 / TOKEN_TO_TEXT_RATIO

    MAX_IMPORTANCE = 2147483647
    DEVELOPER_MESSAGE_IMPORTANCE = MAX_IMPORTANCE

    DEFAULT_RESPONSE_IMPORTANCE = 100
    DEFAULT_USER_MESSAGE_IMPORTANCE = 20
    
    @staticmethod
    def get_approximate_tokens_size(text: str) -> int:
        return int(len(text) * Utils.TEXT_TO_TOKEN_RATIO)
