import time 

from datetime import datetime 
from uuid import uuid4 

from config import EXAMPLE_CHAT_TITLE


def prepare_create_new_chat_payload(
    selected_model_id: str,
    user_question: str
) -> dict:
    new_message_id = str(uuid4())
    timestamp = int(time.time())

    form_data = {
        "chat": {
            "id": "",
            "title": EXAMPLE_CHAT_TITLE,
            "models": [
                selected_model_id,
            ],
            "params": {},
            "history": {
                "messages": {
                    new_message_id: {
                        "id": new_message_id,
                        "parentId": None,
                        "childrenIds": [],
                        "role": "user",
                        "content": user_question,
                        "timestamp": timestamp,
                        "models": [
                            selected_model_id,
                        ]
                    }
                },
                "currentId": new_message_id
            },
            "messages": [
                {
                    "id": new_message_id,
                    "parentId": None,
                    "childrenIds": [],
                    "role": "user",
                    "content": user_question,
                    "timestamp": timestamp,
                    "models": [
                        selected_model_id,
                    ]
                }
            ],
            "tags": [],
            "timestamp": timestamp
        },
        "folder_id": None
    }
    
    return form_data


def prepare_chat_payload_for_update_message(
    user_message: dict, # the response returned after creating a new chat
):
    """Called when creating a placeholder for the assistant message (before inference)"""
    timestamp = int(time.time())
    new_message_id = str(uuid4())
    last_message_id = user_message['chat']['history']['currentId']
    selected_model_id = user_message['chat']['models'][0]

    assistant_message_body = {
        "id": new_message_id,
        "parentId": last_message_id,
        "childrenIds": [],
        "role": "assistant",
        "content": "",
        "timestamp": timestamp,
        "model": selected_model_id,
        "modelName": selected_model_id,
        "modelIdx": 0,
    }
    
    user_message['chat']['history']['messages'][last_message_id]['childrenIds'] \
        .append(new_message_id)
        
    form_data = {
        "chat": {
            "models": [
                selected_model_id,
            ],
            "history": {
                "messages": {
                    last_message_id: {
                        **user_message['chat']['history']['messages'][last_message_id],
                    },
                    new_message_id: assistant_message_body,
                },
                "currentId": new_message_id,
            },
            "messages": [
                {
                    # user message
                    **user_message['chat']['history']['messages'][last_message_id],
                },
                assistant_message_body,
            ]
        }
    }
    
    return form_data
    
def prepare_form_data_for_chat_completions(
    username: str,
    model_config: dict,
    user_question: str,
    chat_id: str,
    assistant_message_id: str,
) -> dict:
    """Prepare form data payload to call /chat/completions endpoint"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    weekday_name = now.strftime('%A')

    model_item = {
        **model_config,
        "openai": { **model_config },
        "urlIdx": 0,
        "actions": [],
        "filters": [],
        "tags": []
    }
    
    form_data = {
        "stream": False,
        "model": model_config['id'],
        "messages": [
            {
                "role": "user",
                "content": user_question,
            }
        ],
        "params": {},
        "tool_ids": [
            "server:0"
        ],
        "tool_servers": [],
        "features": {
            "image_generation": False,
            "code_interpreter": False,
            "web_search": False
        },
        "variables": {
            "{{USER_NAME}}": username,
            "{{USER_LOCATION}}": "Unknown",
            "{{CURRENT_DATETIME}}": f"{date_str} {time_str}",
            "{{CURRENT_DATE}}": date_str,
            "{{CURRENT_TIME}}": time_str,
            "{{CURRENT_WEEKDAY}}": weekday_name,
            "{{CURRENT_TIMEZONE}}": "Asia/Kuala_Lumpur",
            "{{USER_LANGUAGE}}": "en-US"
        },
        "model_item": model_item,
        "session_id": None,
        # "chat_id": None,
        # "session_id": "YhxSF_I9W-Ewi6GuAAAB",
        # "chat_id": "d4727188-a62a-4cc7-9eae-21abbde0b2c7",
        # "id": "ebb71399-f04a-4394-81b1-b2f2d43f3371",
        "chat_id": chat_id, # chat session id
        "id": assistant_message_id, # assistant message id
        "background_tasks": {
            "title_generation": True,
            "tags_generation": True,
            "follow_up_generation": True
        }
    }

    return form_data

def format_chat_messages_to_list(messages: dict) -> list:
    root_message_id = None
    message_list = []

    for message_id in messages.keys():
        if messages[message_id]['parentId'] is None:
            # it is the parent 
            root_message_id = message_id
            break

    current_message = messages[root_message_id]

    
    while True:
        message_dict = {
            "id": current_message['id'],
            "role": current_message['role'],
            "content": current_message['content'],
            "timestamp": current_message['timestamp'],
        }
        
        message_list.append(message_dict)
        
        if len(current_message['childrenIds']) > 0:
            next_message_id = current_message['childrenIds'][0]
            current_message = messages[next_message_id]
        else:
            break
        
    return message_list

def prepare_form_data_for_completed_chat(
    assistant_chat: dict,
    model_response_content: dict, 
    model_config: dict,
):
    chat_dict = assistant_chat['chat']
    model_item = {
        "connection_type": "external",
        "name": model_config['id'],
        "urlIdx": 0,
        "actions": [],
        "filters": [],
        "tags": [],
        **model_config,
        "openai": { **model_config },
    }
    
    assistant_message_id = assistant_chat['chat']['history']['currentId']
    assistant_chat['chat']['history']['messages'][assistant_message_id]['content'] = model_response_content['content']
    sorted_messages_dict = format_chat_messages_to_list(
        assistant_chat['chat']['history']['messages']
    )
    
    completed_payload = {
        "model": chat_dict['models'][0],
        "model_item": model_item,
        "session_id": None,
        "chat_id": assistant_chat['id'],
        "id": chat_dict['history']['currentId'], # the latest message id
        "messages": sorted_messages_dict,
    }

    return completed_payload
