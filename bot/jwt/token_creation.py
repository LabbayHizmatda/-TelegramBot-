import aiohttp
import aiofiles
import json
import os
from .token_saving import save_to_json

TOKEN_FILE = 'response.json'

async def get_token(user_id, which='both', filename=TOKEN_FILE):
    if os.path.exists(filename):
        try:
            async with aiofiles.open(filename, 'r') as json_file:
                data = json.loads(await json_file.read())
        except json.JSONDecodeError:
            return None
    else:
        return None

    for entry in data:
        if entry['user_id'] == user_id:
            if which == 'access':
                return entry.get('access')
            elif which == 'refresh':
                return entry.get('refresh')
            elif which == 'both':
                return {
                    'access': entry.get('access'),
                    'refresh': entry.get('refresh')
                }
    
    return None

async def save_to_json(user_id, data, filename=TOKEN_FILE):
    result = {
        'user_id': user_id,
        'access': data.get('access'),
        'refresh': data.get('refresh')
    }
    
    if os.path.exists(filename):
        try:
            async with aiofiles.open(filename, 'r') as json_file:
                existing_data = json.loads(await json_file.read())
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []

    updated = False
    for entry in existing_data:
        if entry['user_id'] == user_id:
            entry['access'] = result['access']
            entry['refresh'] = result['refresh']
            updated = True
            break

    if not updated:
        existing_data.append(result)
    
    try:
        async with aiofiles.open(filename, 'w') as json_file:
            await json_file.write(json.dumps(existing_data, indent=4))
    except IOError as e:
        print(f"Ошибка при сохранении файла: {e}")

async def create_jwt_token(user_id, password, filename=TOKEN_FILE):
    url = 'http://localhost:8000/token/'
    payload = {
        'user_id': user_id,
        'password': password
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                await save_to_json(user_id, data, filename)
    except aiohttp.ClientError as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
    except json.JSONDecodeError:
        print("Ошибка при декодировании ответа JSON")

async def update_jwt_token(user_id):
    user_tokens = await get_token(user_id, which='both')
    if not user_tokens:
        raise ValueError("No tokens found for user")

    refresh_token = user_tokens.get('refresh')
    print(f"Отправка запроса на обновление токена с refresh_token: {refresh_token}")

    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:8000/token/refresh/', json={
            'refresh': refresh_token
        }) as response:
            if response.status == 200:
                new_tokens = await response.json()
                new_access_token = new_tokens['access']
                new_refresh_token = new_tokens.get('refresh', refresh_token)

                await save_to_json(user_id, {
                    'access': new_access_token,
                    'refresh': new_refresh_token
                })
                return new_access_token
                
            elif response.status == 401:
                print("Refresh token истек. Попытка создания нового токена...")
                await create_jwt_token(user_id, 'admin')  
                return await update_jwt_token(user_id)  
            
            else:
                print(f"Ошибка при обновлении токена. Код ответа: {response.status}")
                print(f"Ответ сервера: {await response.text()}")
                raise Exception("Failed to refresh token")