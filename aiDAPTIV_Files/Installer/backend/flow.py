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

from form_data import (
    prepare_create_new_chat_payload,
    prepare_chat_payload_for_update_message,
    prepare_form_data_for_chat_completions,
    prepare_form_data_for_completed_chat,
)
from config import OPENAI_API_BASE_URL, ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD, HOST, PORT, EXAMPLE_CHAT_TITLE


class KVCacheGenerationException(Exception):
    """Raised when encountering 400-500 status code when calling open-webui APIs"""


class APINotFoundException(Exception):
    """Raised when the API cannot be connected"""


class InitializeKVCacheService:
    def __init__(self, openwebui_base_url: str):
        self.client = httpx.AsyncClient(
            base_url=openwebui_base_url,
        )
        self.access_token = None
            

    async def healthcheck(
        self, 
        retry_limit: int = 5, 
        retry_interval: int = 15,
        current_retry_count: int = 0,
    ) -> bool:
        """Ping the API to see whether it can be connected successfully using the given base url"""
        try:
            _ = await self.client.get('/health')
            
            return True
    
        except httpx.ConnectError:
            # retry for N times while waiting for M seconds each time
            if current_retry_count < retry_limit:
                print(f"API healthcheck ping failed, retrying in {retry_interval} seconds")
                time.sleep(retry_interval)
                await self.healthcheck(current_retry_count=current_retry_count + 1)
            else:
                print(f"The Open-WebUI backend cannot be connected. Installation is failed. Terminating re-trying...\nConnected URL: http://{HOST}:{PORT}/api/")
                return False
            
        
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
            raise KVCacheGenerationException(f"Something went wrong when calling `/auths/signin`\nPayload: {payload}\nStatus:{response.status_code}")
                    
    async def get_model(self, openai_base_url: str):
        """Get the model information from the OpenAI"""
        try:
            response = httpx.get(f'{openai_base_url}/models')
            response.raise_for_status()
            data = response.json()['data']
            model = data[0] # get first model always

            return model
        
        except httpx.ConnectError:
            raise KVCacheGenerationException(f"Please ensure that the aiDAPTIV server is up! URL: <{openai_base_url}> is not found!")
            
        except httpx.HTTPStatusError:
            raise KVCacheGenerationException(f"Something went wrong when calling getting model information from OpenAI API after calling {openai_base_url}/models.\nStatus: {response.status_code}")

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
            raise KVCacheGenerationException(f"Something went wrong when creating a new chat.\nPayload: {form_data}\nStatus: {response.status_code}")
    
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
            raise KVCacheGenerationException(f"Something went wrong when updating chat.\nPayload: {chat_payload}\nStatus: {response.status_code}")
    
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
                timeout=600,
            )
            response.raise_for_status()
            data = response.json()
            
            return data
        
        except httpx.HTTPStatusError:
            raise KVCacheGenerationException(f"Something went wrong when inferencing with LLM.\nPayload: {form_data}\nStatus: {response.status_code}")
        
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
            raise KVCacheGenerationException(f"Something went wrong when calling completed chat.\nPayload: {form_data}\nStatus: {response.status_code}")
            
    async def _get_all_chats(self):
        """Get all chats from open-webui"""
        try:
            response = await self.client.get('/v1/chats/?page=1')
            response.raise_for_status()
            data = response.json()
            
            return data
            
        except httpx.HTTPStatusError:
            raise KVCacheGenerationException(f"Something went wrong when retrieving all the chats.\nStatus: {response.status_code}")
    
    async def kv_cache_is_initialized(self) -> bool:
        """
            Check whether the KV Cache is initialized. Here, we assume that if we have the chat title in the chats retrieved. 
            Then, it means that the KV Cache is initialize
        """
        chats = await self._get_all_chats()
        for chat in chats:
            if chat['title'] == EXAMPLE_CHAT_TITLE:
                return True 
            
        return False
    
async def generate_kv_cache():
    """Main entrypoint to initialize the KV Cache"""    
    kvcache_service = InitializeKVCacheService(openwebui_base_url=f"http://{HOST}:{PORT}/api/")
    api_is_connected = await kvcache_service.healthcheck()
    if api_is_connected:
        await kvcache_service.login(ADMIN_USER_EMAIL, ADMIN_USER_PASSWORD) 
        if await kvcache_service.kv_cache_is_initialized():
            print(f"The KV Cache is already initialized, aborting...")
            return
        
        start_time = time.perf_counter()
        user_question = "Please remember that you have access to github-mcp-server and should always use the tool to achieve my requirements.\n\nNow, use tool_search_repositories_post of github-mcp-server to search adn describe the linkedin/liger_kernel repostiory in github."
        
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
        _ = await kvcache_service.chat_completed(
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
        _ = await kvcache_service.update_chat(
            user_message['id'],
            assistant_message_placeholder,
        )
        end_time = time.perf_counter()

        print(f"KV Cache Generated Successfully! Total time taken: {end_time - start_time} seconds")
        
    

if __name__ == '__main__':

    asyncio.run(generate_kv_cache())

    pass 
