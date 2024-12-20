def get_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    db = PromptManager()
    prompt = db.get_prompt_by_prompt_id(prompt_id)
    return prompt['text']

    


def get_prompt_name(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    db = PromptManager()
    prompt = db.get_prompt_by_prompt_id(prompt_id)
    return prompt['prompt_name']

def get_user_name(user_id):
    from app.database.managers.user_manager import UserManager
    db= UserManager()
    user = db.get_user_by_user_id(user_id)
    return user.username

def get_chat_name(chat_id):
    from app.database.managers.chat_manager import ChatManager
    db=ChatManager()
    chat = db.get_chat_by_id(chat_id)
    return chat.chat_name