import sys
import os

# --- PATH FIX: Force Python to see the current directory ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
# -----------------------------------------------------------
import httpx
import asyncio
import time

from uuid import uuid4

from form_data import (
    prepare_create_new_chat_payload,
    prepare_chat_payload_for_update_message,
    prepare_form_data_for_chat_completions,
    prepare_form_data_for_completed_chat,
)

from config import OPENAI_API_BASE_URL, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, HOST, PORT
# ... your imports start here ...
# from form_data import ...

class InitializeKVCacheService:
    def __init__(self, openwebui_base_url: str):
        self.client = httpx.AsyncClient(
            base_url=openwebui_base_url,
        )
        self.access_token = None
        
    async def login(self, email: str, password: str):
        """Login to get access token"""
        try:
            payload = {
                "email": email,
                "password": password,
            }
            response = await self.client.post('/v1/auths/signin', json=payload)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data['token']
            self.client.headers.update({
                'Authorization': f"Bearer {self.access_token}"
            })

        except httpx.HTTPStatusError:
            print(f"Something went wrong when calling `/auths/signin`\n"
            f"Payload: {payload}\n"
            f"Status: {response.status_code}")
            # print(f"Something went wrong when calling `/auths/signin`\nPayload: {payload}\Status: {response.status_code}")
        
    async def get_model(self, openai_base_url: str):
        """Get the model information from the OpenAI"""
        try:
            response = httpx.get(f'{openai_base_url}/models')
            response.raise_for_status()
            data = response.json()['data']
            model = data[0] # get first model always

            return model
            
        except httpx.HTTPStatusError:
            print(f"Something went wrong when calling getting model information from OpenAI API after calling {openai_base_url}/models.\nStatus: {response.status_code}")

    async def create_new_chat(self, selected_model_id: str, user_question: str) -> dict:
        """Create a new chat with the model and user question (without inference)"""
        try:
            form_data = prepare_create_new_chat_payload(
                selected_model_id,
                user_question,
            )
            
            response = await self.client.post('/v1/chats/new', json=form_data)
            response.raise_for_status()
            data = response.json()
            
            return data
            
        except httpx.HTTPStatusError:
            print(f"Something went wrong when creating a new chat.\nPayload: {form_data}\nStatus: {response.status_code}")
    
    async def update_chat(self, chat_id: str, chat_payload: dict):
        """Update the chat""" 
        try:
            response = await self.client.post(
                f'/v1/chats/{chat_id}',
                json=chat_payload,
            )
            response.raise_for_status()
            data = response.json()
            
            return data
            
        except httpx.HTTPStatusError:
            print(f"Something went wrong when updating chat.\nPayload: {chat_payload}\nStatus: {response.status_code}")
    
    async def chat_completions(
        self, 
        username: str,
        model_config: dict,
        user_question: str,
        chat_id: str,
        assistant_message_id: str,
    ) -> dict:
        """Inference with the LLM"""
        try:
            form_data = prepare_form_data_for_chat_completions(
                username,
                model_config,
                user_question, 
                chat_id,
                assistant_message_id,
            )
            
            response = await self.client.post(
                '/chat/completions',
                json=form_data,
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()
            
            return data
        
        except httpx.HTTPStatusError:
            print(f"Something went wrong when inferencing with LLM.\nPayload: {form_data}\nStatus: {response.status_code}")

    
        
    async def chat_completed(
        self, 
        assistant_message_placeholder: dict, 
        model_response_dict: dict, 
        model_config: dict
    ) -> dict:
        """Calling completed chat"""
        try:
            form_data = prepare_form_data_for_completed_chat(
                assistant_message_placeholder,
                model_response_dict,
                model_config,
            )
            
            response = await self.client.post(
                '/chat/completed',
                json=form_data,
            )
            response.raise_for_status()
            data = response.json()
            
            return data
            
        except httpx.HTTPStatusError:
            print(f"Something went wrong when calling completed chat.\nPayload: {form_data}\nStatus: {response.status_code}")
            
    
async def main():

    kvcache_service = InitializeKVCacheService(openwebui_base_url=f"http://{HOST}:{PORT}/api/")
    user_question = "Please remember that you have access to github-mcp-server and should always use the tool to achieve my requirements.\n\nNow, use tool_search_repositories_post of github-mcp-server to search adn describe the linkedin/liger_kernel repostiory in github."
    
    await kvcache_service.login(ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD) 
    model_config = await kvcache_service.get_model(OPENAI_API_BASE_URL)
    
    user_message = await kvcache_service.create_new_chat(model_config['id'], user_question)

    # create an assistant skeleton
    assistant_placeholder_form_data = prepare_chat_payload_for_update_message(
        user_message
    )
    
    assistant_message_placeholder = await kvcache_service.update_chat(
        chat_id=user_message['id'],
        chat_payload=assistant_placeholder_form_data,
    )
    
    # chat completions inference
    chat_completion_response = await kvcache_service.chat_completions(
        ADMIN_USER_EMAIL.split('@')[0] if ADMIN_USER_EMAIL != "" else "admin",
        model_config,
        user_question,
        user_message['id'],
        assistant_message_id=assistant_message_placeholder['chat']['history']['currentId'],
    )
    model_response_dict = chat_completion_response['choices'][0]['message']
    
    # call completed
    chat_completed_response = await kvcache_service.chat_completed(
        assistant_message_placeholder,
        model_response_dict,
        model_config,
    )
    
    # update again the chat with the generated content
    assistant_message_id = assistant_message_placeholder['chat']['history']['currentId']

    latest_assistant_message = assistant_message_placeholder['chat']['history']['messages'][assistant_message_id]
    latest_assistant_message['content'] = model_response_dict['content']
    last_sentence = model_response_dict['content'].split('\n')[-1]
    latest_assistant_message['done'] = True
    latest_assistant_message['lastSentence'] = last_sentence
    
    assistant_message_placeholder['chat']['history']['messages'][assistant_message_id] = latest_assistant_message
    updated_assistant_message = await kvcache_service.update_chat(
        user_message['id'],
        assistant_message_placeholder,
    )

    print("KV Cache Generated Successfully!")


if __name__ == '__main__':

    asyncio.run(main())

    pass 
