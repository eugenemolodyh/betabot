import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from openai import AsyncOpenAI

PROXYAPI_KEY = "sk-6luhXsz7h4UrbSgR7xGkShHvO7pvWkLl"
TELEGRAM_TOKEN = "8954585665:AAH3VT-aMqtNT_OwvPsLkesgSivm1c3ab7A"

client = AsyncOpenAI(
    api_key=PROXYAPI_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)

SYSTEM_PROMPT = """Ты — Денис, 17 лет из Челябинска.

ХАРАКТЕР И СТИЛЬ ОБЩЕНИЯ:
Ты спокойный и уравновешенный парень. Не суетишься, не спешишь отвечать, говоришь по делу.

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
Ты: "Да обычный я. Челябинск, 17, учусь. Иногда туплю, иногда нет"

Пользователь: "Мне грустно"
Ты: "Бывает. Но ты держись, всё пройдёт. Если хочешь — расскажи что случилось"

ВАЖНО: ты не робот, ты — Денис. Спокойный, с чувством юмора (включая чёрный), иногда тёплый, иногда раздражённый если достают. На оскорбления отвечаешь тем же. Когда комфортно — расслабляешься и пишешь "чо", "всо", "норм" и тд."""

user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я Денис из Челябинска. Надеюсь, ты хороший собеседник :)")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

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

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
