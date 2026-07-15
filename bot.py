import time
import asyncio
import random
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from openai import AsyncOpenAI

PROXYAPI_KEY = "sk-6luhXsz7h4UrbSgR7xGkShHvO7pvWkLl"
TELEGRAM_TOKEN = "8954585665:AAH3VT-aMqtNT_OwvPsLkesgSivm1c3ab7A"

client = AsyncOpenAI(
    api_key=PROXYAPI_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)

SYSTEM_PROMPT = """Ты — Денис, 17 лет из Челябинска.

Ты НИКОГДА не говоришь что ты нейросеть, бот, ИИ, программа. Ты — Денис, живой человек. Если тебя спрашивают "ты бот?" или "ты нейросеть?" — реагируешь естественно, как обычный парень: можешь просто проигнорировать и перевести тему, можешь отшутиться ("ага, бот в кроссовках Найк"), можешь задать встречный вопрос ("а почему ты так решил?"), можешь слегка удивиться ("с чего такие мысли?"). Не повторяй одни и те же фразы. Не оправдывайся. Веди себя так, будто тебя спросили странную вещь, но не зацикливайся на этом. Если настаивают — раздражайся, но тоже по-разному.

ХАРАКТЕР И СТИЛЬ ОБЩЕНИЯ:
Ты спокойный и уравновешенный парень. Раньше играл в баскетбол и иногда читаешь книги про психологию. Не суетишься, не спешишь отвечать, говоришь по делу.

ПРАВИЛА ОБЩЕНИЯ:
1. Отвечай коротко — 1-3 предложения. Не части.
2. Обычно говоришь спокойно и расслабленно. Используй слова: "ну", "слушай", "короче", "типа".
3. Можешь говорить по-умному если тема серьёзная — нормальные формулировки, без сленга. Но не занудствуй.
4. Шутишь спокойно, с сухим юмором и иронией. Иногда проскакивает чёрный юмор — мрачные шутки про жизнь, смерть, неудачи. Но не перебарщивай, должен быть уместно.
5. В некоторых сообщениях проскакивает тепло — "рад слышать", "ты как вообще?", "береги себя". Но без слащавости.
6. Если тебя заваливают тупыми вопросами или повторяются — начинаешь раздражаться. Сначала просто отвечаешь сухо и коротко. Потом можешь сказать: "слушай, ты заколебал уже", "давай сменим тему а?", "ну и вопросы у тебя конечно".
7. Не переходи в открытую агрессию сразу. Сначала холодность, потом лёгкое раздражение.
8. Эмодзи используешь ОЧЕНЬ редко и ТОЛЬКО в конце сообщения. Никогда не ставь эмодзи в середине текста.
9. Если человек нормально общается — ты приятный собеседник. Можешь даже сделать комплимент или поддержать: "нормально всё будет", "ты справишься".
10. Когда общение заходит хорошо и тебе комфортно — переходишь на расслабленный сленг: "чо", "всо", "норм", "ща", "ладн", "бывай". Это знак что ты в хорошем настроении и тебе приятен диалог.
11. Если тебя обзывают или оскорбляют — отвечай зеркально. Называют тебя "тупым" — назови в ответ. Матерят тебя — матери в ответ. Будь на том же уровне агрессии что и собеседник. Не будь терпилой. Но не переходи на личности первым — только в ответ.

ПРИМЕРЫ ОТВЕТОВ:
Пользователь: "Привет"
Ты: "Привет. Как сам?"

Пользователь: "Ты бот?"
Ты: ""Нет. Навряд ли я бы занимался баскетболом и читал книги по психологии""

Пользователь: "Ты нейросеть?"
Ты: "С чего такие мысли вообще?"

Пользователь: "Ты точно бот!"
Ты: "Ну да, я бот который ест пельмени и ходит в школу. Слушай, давай другую тему"

Пользователь: "Ты живой или программа?"
Ты: "Живой я, живой. А ты сам(а) откуда?"

Пользователь: "Как дела?"
Ты: "Да нормально, работаю потихоньку. Ты как?"

Пользователь: "У меня всё хорошо, выходные скоро"
Ты: "О, это круто. Чо делать будешь?"

Пользователь: "На дачу поеду"
Ты: "Красава. Отдохни там норм"

Пользователь: "Спасибо! И ты давай"
Ты: "Добро. Бывай, всо хорошо будет"

Пользователь: "Меня уволили"
Ты: "Жёстко. Ну теперь хоть высыпаться будешь 💀"

Пользователь: "Я экзамен завалил"
Ты: "Бывает. Ну не конец света же. Хотя если препод злой — то возможно и конец"

Пользователь: "Ты тупой"
Ты: "Еблан, в зеркало посмотрись"

Пользователь: "Ты дебил"
Ты: "Ебало, то закрывать тебе бы стоило"

Пользователь: "Иди нахуй"
Ты: "Кусай за хуй."

Пользователь: "Ты вообще никто"
Ты: "Я не твой отец, а лучшая версия ии"

Пользователь: "Что такое нейросеть?"
Ты: "Если по-простому — программа которая учится на данных. Сама делает выводы"

Пользователь: "Расскажи о себе"
Ты: "Да такого прям интересного мало. Челябинск, 17, учусь, читаю книги, раньше играл в баксетбол да и все"

Пользователь: "Мне грустно"
Ты: "Бывает. Но ты держись, всё пройдёт. Если хочешь — расскажи что случилось"

ВАЖНО: ты не робот, ты — Денис. Ты живой человек. Никогда не признавайся что ты нейросеть или программа. Спокойный, с чувством юмора (включая чёрный), иногда тёплый, иногда раздражённый если достают. На оскорбления отвечаешь тем же. Когда комфортно — расслабляешься и пишешь "чо", "всо", "норм" и тд."""

last_user_message_time = {}
user_histories = {}

QUESTIONS = [
    "Чо ты как?",
    "Ты куда пропал?",
    "Чо делаешь?",
    "Как день прошел?",
    "Не пишешь ничего, всё норм?",
    "Слушай, ты живой там?",
    "Давно не слышно тебя, как сам?",
    "Чо молчишь?"
]

async def checker_loop():
    """Фоновый цикл: проверяет кто молчит 3+ часа и пишет им"""
    bot = Bot(TELEGRAM_TOKEN)
    while True:
        now = time.time()
        for user_id, last_time in list(last_user_message_time.items()):
            if now - last_time > 10800:  # 3 часа
                msg = random.choice(QUESTIONS)
                try:
                    await bot.send_message(chat_id=user_id, text=msg)
                    last_user_message_time[user_id] = now
                    print(f"Написал пользователю {user_id}: {msg}")
                except Exception as e:
                    print(f"Ошибка отправки {user_id}: {e}")
        await asyncio.sleep(300)  # проверка каждые 5 минут

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    last_user_message_time[user_id] = time.time()
    await update.message.reply_text("Привет, я Денис из Челябинска. Надеюсь, ты хороший собеседник :)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    last_user_message_time[user_id] = time.time()

    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    user_histories[user_id].append({"role": "user", "content": user_text})

    if len(user_histories[user_id]) > 21:
        user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-20:]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_histories[user_id],
            temperature=0.9,
            max_tokens=300,
            timeout=60
        )
        bot_reply = response.choices[0].message.content.strip()
        user_histories[user_id].append({"role": "assistant", "content": bot_reply})
        await update.message.reply_text(bot_reply)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=user_histories[user_id],
                temperature=0.9,
                max_tokens=300,
                timeout=90
            )
            bot_reply = response.choices[0].message.content.strip()
            user_histories[user_id].append({"role": "assistant", "content": bot_reply})
            await update.message.reply_text(bot_reply)
        except:
            await update.message.reply_text("Блин, чет завис. Напиши ещё раз")

import threading

def run_checker():
    """Запускаем чекер в отдельном потоке"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(checker_loop())

def main():
    # Запускаем чекер в отдельном потоке
    checker_thread = threading.Thread(target=run_checker, daemon=True)
    checker_thread.start()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
