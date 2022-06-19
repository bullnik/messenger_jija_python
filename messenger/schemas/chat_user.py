class ChatUser:
    user_id: int
    chat_id: int

    def __init__(self, user_id: int, chat_id: int):
        self.user_id = user_id
        self.chat_id = chat_id
