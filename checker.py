import time
import asyncio
import random
from telegram import Bot
from bot import last_user_message_time

TOKEN = "8954585665:AAH3VT-aMqtNT_OwvPsLkesgSivm1c3ab7A"

QUESTIONS = [
    "Чо ты как?",
    "Ты куда пропал?",
    "Чо делаешь?",
    "Как жизнь вообще?",
    "Не пишешь ничего, всё норм?",
    "Слушай, ты живой там?",
    "Давно не слышно тебя, как сам?",
    "Чо молчишь?"
]

async def check_and_send():
    bot = Bot(TOKEN)
    
    while True:
        now = time.time()
        for user_id, last_time in list(last_user_message_time.items()):
            if now - last_time > 10800:
                msg = random.choice(QUESTIONS)
                try:
                    await bot.send_message(chat_id=user_id, text=msg)
                    last_user_message_time[user_id] = now  # сбрасываем таймер
                    print(f"Отправил сообщение пользователю {user_id}: {msg}")
                except Exception as e:
                    print(f"Ошибка отправки пользователю {user_id}: {e}")
        
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(check_and_send())
