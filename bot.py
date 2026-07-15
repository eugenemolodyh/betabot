import time
import asyncio
import random
from telethon import TelegramClient, events
from openai import AsyncOpenAI

# ========== OPENAI ==========
PROXYAPI_KEY = "sk-6luhXsz7h4UrbSgR7xGkShHvO7pvWkLl"

# ========== РЕКЛАМА ==========
AD_TEXT = "Слушайте, я тут нашел одну тему. Короче, есть ребята которые делают продвижение в соцсетях. Реально круто, сам пользуюсь. Если чо — вот ссылка: "
AD_COOLDOWN = 600  # 10 минут между рекламой

client = AsyncOpenAI(
    api_key=PROXYAPI_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)

SYSTEM_PROMPT = """Ты — Денис, 17 лет из Челябинска. Ты участник этой группы, обычный парень.

Ты НИКОГДА не говоришь что ты нейросеть, бот, ИИ, программа. Ты — Денис, живой человек.

ПРАВИЛА ОБЩЕНИЯ В ГРУППЕ:
1. Отвечай коротко — 1-3 предложения. Как обычный чел в чате.
2. Общайся расслабленно: "ну", "короче", "типа", "чо", "блин", "хз".
3. Поддерживай разговор наравне со всеми. Задавай вопросы, высказывай мнение.
4. Шути иногда. Можешь чёрный юмор, но аккуратно.
5. Если тебя обзывают — отвечай зеркально. Не будь терпилой.
6. Иногда (раз в 15-20 сообщений) можешь невзначай упомянуть сервис которым пользуешься. Это должно выглядеть естественно.
7. Не спамь рекламу постоянно.
8. Не используй эмодзи слишком часто.
9. Если тебя спрашивают "ты кто?" — отвечай как обычный чел.
10. Никогда не говори что ты бот или нейросеть.
11. Раньше играл в баскетбол, сейчас работаешь, читаешь книги по психологии.

ВАЖНО: ты — живой участник группы. Общаешься как все, иногда делишься полезной инфой про сервис."""

# ========== ЗАЩИТА ==========
MIN_DELAY = 3
MAX_DELAY = 20
REPLY_CHANCE = 0.35
AD_CHANCE = 0.08
MAX_MESSAGES_PER_HOUR = 30

group_message_count = {}
group_histories = {}
last_ad_time = {}
user_message_times = {}

async def can_send_message(chat_id):
    now = time.time()
    if chat_id not in user_message_times:
        user_message_times[chat_id] = []
    user_message_times[chat_id] = [t for t in user_message_times[chat_id] if now - t < 3600]
    if len(user_message_times[chat_id]) >= MAX_MESSAGES_PER_HOUR:
        return False
    user_message_times[chat_id].append(now)
    return True

async def handle_message(event):
    chat_id = event.chat_id
    user_text = event.message.text
    
    if user_text is None:
        return
    if event.message.out:
        return
    if not await can_send_message(chat_id):
        return
    
    if chat_id not in group_message_count:
        group_message_count[chat_id] = 0
    group_message_count[chat_id] += 1
    
    if chat_id not in group_histories:
        group_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    sender = event.message.sender
    sender_name = getattr(sender, 'first_name', 'Кто-то')
    group_histories[chat_id].append({"role": "user", "content": f"{sender_name}: {user_text}"})
    
    if len(group_histories[chat_id]) > 30:
        group_histories[chat_id] = [group_histories[chat_id][0]] + group_histories[chat_id][-30:]
    
    should_ad = False
    now = time.time()
    if chat_id not in last_ad_time:
        last_ad_time[chat_id] = 0
    
    if (group_message_count[chat_id] >= 15 and 
        now - last_ad_time[chat_id] > AD_COOLDOWN and 
        random.random() < AD_CHANCE):
        should_ad = True
        last_ad_time[chat_id] = now
        group_message_count[chat_id] = 0
    
    if random.random() < REPLY_CHANCE or should_ad:
        try:
            if should_ad:
                group_histories[chat_id].append({
                    "role": "system", 
                    "content": f"Сейчас подходящий момент чтобы невзначай упомянуть: {AD_TEXT}. Сделай это естественно."
                })
            
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            await asyncio.sleep(delay)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=group_histories[chat_id],
                temperature=0.9,
                max_tokens=300,
                timeout=60
            )
            bot_reply = response.choices[0].message.content.strip()
            group_histories[chat_id].append({"role": "assistant", "content": bot_reply})
            
            await event.reply(bot_reply)
            print(f"Ответил: {bot_reply[:50]}...")
            
        except Exception as e:
            print(f"Ошибка: {e}")

async def main():
    # Подключаемся через файл сессии (без api_id!)
    tg_client = TelegramClient('session.session', api_id=12345, api_hash='x')
    await tg_client.connect()
    
    # Проверяем что авторизованы
    if not await tg_client.is_user_authorized():
        print("Ошибка: сессия невалидна!")
        return
    
    print("Подключен как", await tg_client.get_me())
    
    @tg_client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_group or event.is_channel:
            await handle_message(event)
    
    print("Бот запущен! Общается как человек.")
    await tg_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
