import asyncio
import telebot
from jwt.token_creation import create_jwt_token, update_jwt_token

TOKEN_FILE = 'response.json'
BOT_TOKEN = '7301562528:AAHeyY6HbDva-B9_mIMGhJizortAgAqNYbc'
bot = telebot.TeleBot(BOT_TOKEN)



@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "Привет! Используйте команды для работы с токенами.")

@bot.message_handler(commands=['create_token'])
def handle_create_token(message):
    user_id = '1234567890' 
    password = 'admin' 

    async def async_create_token():
        await create_jwt_token(user_id, password)
        bot.reply_to(message, "Токен создан и сохранен.")

    asyncio.run(async_create_token())

@bot.message_handler(commands=['refresh_token'])
def handle_refresh_token(message):
    user_id = '1234567890' 

    async def async_refresh_token():
        new_access_token = await update_jwt_token(user_id)
        result = f"Новый Access Token: {new_access_token}"
        bot.reply_to(message, result)

    asyncio.run(async_refresh_token())

if __name__ == '__main__':
    bot.polling(none_stop=True)
