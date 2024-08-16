import aiofiles
import json
import os

TOKEN_FILE = 'response.json'

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