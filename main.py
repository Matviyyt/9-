from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
import matplotlib.pyplot as plt
import io  # для роботи з байтовим потоком зображення

# Токен вашого бота з Telegram BotFather
TOKEN = "7626170602:AAG0C4sjxgKoLgkk-cJLBbSqTm8LXeT8RHs"  # Замініть на свій токен

# Стани розмови
START, AGE, GENDER, EXERCISE, PULSE_BEFORE, PULSE_DURING, PULSE_AFTER, PULSE_2MIN, ANALYSIS, MATH, END = range(11)

# Мотиваційні фрази за результатами
MOTIVATION_PHRASES = {
    "Чудово": [
        "Ти ж майже супергерой! Пульс стабільний, дух бойовий!",
        "З таким результатом можна хоч зараз рятувати світ — або принаймні прибігти до буфету першим!",
        "Фітнес-тренери вже нервово шукають твоє резюме!"
    ],
    "Добре": [
        "Ти не Iron Man, але вже точно Титан на мінімалках!",
        "Організм каже \"дякую\", а математик — \"чудова робота!\"",
        "До спортивного олімпу ще крок-другий, але ти вже на правильному маршруті!"
    ],
    "Задовільно": [
        "Ну, шкарпетки не злетіли — вже перемога!",
        "Пульс ще живий, як і надія! Продовжуй рухатись!",
        "Тіло трохи пручається, але мозок уже рахує калорії — значить, працює!"
    ],
    "Погано": [
        "А пульс точно вимірював, а не слухав, як чайник закипає?",
        "Не біда! Велика форма починається з маленького кряхтіння!",
        "Організм в шоці, але ми з ним поговоримо. Завтра буде краще (може)!"
    ]
}

# Поради за результатами
ADVICE = {
    "Чудово": [
        "Продовжуй у тому ж дусі! Але не забувай про відпочинок — супергероям теж потрібні вихідні.",
        "Спробуй ускладнити вправи або додати нові (наприклад, планку або біг на місці).",
        "Слідкуй за пульсом не лише після вправ, а й у спокої — щоб бачити загальну динаміку."
    ],
    "Добре": [
        "Ти молодець! Ще трішки регулярності — і буде «чудово».",
        "Роби вправи 3–4 рази на тиждень, поступово збільшуючи час або кількість повторів.",
        "Перевір, чи правильно дихаєш під час виконання — це сильно впливає на пульс!"
    ],
    "Задовільно": [
        "Це вже щось! Не зупиняйся — регулярність перемагає силу.",
        "Спробуй розминку щоранку: 5–10 хвилин активного руху.",
        "Можливо, варто зменшити інтенсивність і поступово її підвищувати. Повільно — не значить погано."
    ],
    "Погано": [
        "Не переживай! Це лише старт. Головне — ти вже щось зробив.",
        "Починай із легких вправ: ходьба, повороти корпусу, присідання без навантаження.",
        "Порадься з учителем фізкультури або батьками, якщо після вправ відчуваєш дискомфорт.",
        "І пам'ятай: найгірше — нічого не робити. Крок за кроком — і буде прогрес!"
    ]
}

# Функція для початку розмови
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Початок розмови та виведення кнопок 'Так' і 'Ні'."""
    reply_keyboard = [["Так", "Ні"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Привіт! Я — бот проєкту «Математика в Русі». Ми досліджуємо, як змінюється пульс під час фізичних вправ і як це пов'язано з математикою. Давай почнемо?",
        reply_markup=markup,
    )

    return START  # Перехід у стан START

# Обробка вибору "Так" чи "Ні" на старті
async def start_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробка вибору користувача на початку розмови."""
    user_choice = update.message.text

    if user_choice == "Так":
        await update.message.reply_text("Чудово! Скажи, будь ласка, скільки тобі років?", reply_markup=ReplyKeyboardRemove())
        return AGE  # Перехід у стан AGE

    elif user_choice == "Ні":
        await update.message.reply_text("Добре, звертайся, якщо надумаєш!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END  # Завершення розмови

    else:
        await update.message.reply_text("Будь ласка, виберіть 'Так' або 'Ні'.")
        return START  # Залишитись у стані START

# Отримання віку користувача
async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отримання віку користувача."""
    try:
        user_age = int(update.message.text)
        if user_age <= 0:
            await update.message.reply_text("Будь ласка, введіть коректний вік.")
            return AGE
        context.user_data["age"] = user_age
        reply_keyboard = [["Хлопець", "Дівчина"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Твоя стать?", reply_markup=markup)
        return GENDER  # Перехід у стан GENDER
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть вік числом.")
        return AGE  # Залишитись у стані AGE

# Отримання статі користувача
async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отримання статі користувача."""
    user_gender = update.message.text
    if user_gender not in ("Хлопець", "Дівчина"):
        await update.message.reply_text("Будь ласка, виберіть стать з клавіатури.")
        return GENDER
    context.user_data["gender"] = user_gender
    reply_keyboard = [["Присідання", "Згинання"], ["Інша"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Яку вправу ти виконував(-ла)?", reply_markup=markup)
    return EXERCISE  # Перехід у стан EXERCISE

# Отримання типу вправи
async def exercise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отримання типу вправи."""
    exercise_type = update.message.text
    context.user_data["exercise"] = exercise_type
    await update.message.reply_text("Введи, будь ласка, свій пульс у такі моменти:\n\nДо вправи:",
                                    reply_markup=ReplyKeyboardRemove())
    return PULSE_BEFORE  # Перехід у стан PULSE_BEFORE

# Отримання даних про пульс
async def pulse_before(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отримання пульсу до вправи."""
    try:
        pulse = int(update.message.text)
        context.user_data["pulse_before"] = pulse
        await update.message.reply_text("Під час вправи:")
        return PULSE_DURING
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть пульс числом.")
        return PULSE_BEFORE

async def pulse_during(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отримання пульсу під час вправи."""
    try:
        pulse = int(update.message.text)
        context.user_data["pulse_during"] = pulse
        await update.message.reply_text("Одразу після вправи:")
        return PULSE_AFTER
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть пульс числом.")
        return PULSE_DURING

async def pulse_after(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отримання пульсу одразу після вправи."""
    try:
        pulse = int(update.message.text)
        context.user_data["pulse_after"] = pulse
        await update.message.reply_text("Через 2 хвилини після вправи:")
        return PULSE_2MIN
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть пульс числом.")
        return PULSE_AFTER

async def pulse_2min(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отримання пульсу через 2 хвилини після вправи та проведення аналізу."""
    try:
        pulse_2min = int(update.message.text)
        context.user_data["pulse_2min"] = pulse_2min

        # Отримання даних з context
        pulse_before = context.user_data["pulse_before"]
        pulse_during = context.user_data["pulse_during"]
        pulse_after = context.user_data["pulse_after"]

        # Аналіз
        increase = pulse_during - pulse_before
        recovery = pulse_after - pulse_2min
        average = (pulse_before + pulse_during + pulse_after + pulse_2min) / 4

        # Індекс Руф'є
        ruffier_index = ((pulse_before + pulse_during + pulse_2min) * 4 - 200) / 10

        # Визначення результату на основі індексу Руф'є
        if 0 <= ruffier_index <= 5:
            result = "Чудово"
            fitness_video = "https://youtu.be/RYJCdDZKPMU?si=A5s8CekrLMCaz-VG"  # Замініть на реальне посилання
        elif 5.1 <= ruffier_index <= 10:
            result = "Добре"
            fitness_video = "https://youtu.be/RYJCdDZKPMU?si=A5s8CekrLMCaz-VG"  # Замініть на реальне посилання
        elif 10.1 <= ruffier_index <= 15:
            result = "Задовільно"
            fitness_video = "https://youtu.be/RYJCdDZKPMU?si=A5s8CekrLMCaz-VG"  # Замініть на реальне посилання
        else:
            result = "Погано"
            fitness_video = "https://youtu.be/RYJCdDZKPMU?si=A5s8CekrLMCaz-VG"  # Замініть на реальне посилання

        # Вибір випадкової мотиваційної фрази для даного результату
        import random
        motivation = random.choice(MOTIVATION_PHRASES[result])

        # Формування тексту аналізу
        analysis_text = (
            "Дякую! Ось твій короткий аналіз:\n\n"
            f"Збільшення пульсу під час вправи: {increase} ударів\n"
            f"Відновлення через 2 хвилини: {recovery} ударів\n"
            f"Середнє значення: {average:.2f} ударів\n"
            f"Індекс Руф'є: {ruffier_index:.2f}\n\n"
            f"Результат: {result}\n"
            f"{motivation}\n\n"
            f"Корисні вправи для твого рівня: [Відео]({fitness_video})\n\n"
            f"Чи потрібен тобі графік твого пульсу?"
        )

        # Збереження результату для подальшого використання
        context.user_data["result"] = result
        context.user_data["increase"] = increase

        reply_keyboard = [["Так", "Ні"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(analysis_text, reply_markup=markup, parse_mode="Markdown")

        return ANALYSIS  # Перехід у стан ANALYSIS

    except ValueError:
        await update.message.reply_text("Будь ласка, введіть пульс числом.")
        return PULSE_2MIN

# Обробка питання про графік та надання порад
async def analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробка рішення користувача щодо графіку та надання порад."""
    choice = update.message.text
    if choice == "Так":
        # Отримання даних для графіку
        pulse_before = context.user_data["pulse_before"]
        pulse_during = context.user_data["pulse_during"]
        pulse_after = context.user_data["pulse_after"]
        pulse_2min = context.user_data["pulse_2min"]

        # Побудова графіка
        x = ["До", "Під час", "Після", "Через 2 хв"]
        y = [pulse_before, pulse_during, pulse_after, pulse_2min]
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, marker='o', linewidth=2, markersize=10)
        plt.xlabel("Момент часу", fontsize=12)
        plt.ylabel("Пульс (ударів/хв)", fontsize=12)
        plt.title("Зміна пульсу під час вправи", fontsize=14)
        plt.grid(True)

        # Збереження графіка у байтовий потік
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        await update.message.reply_photo(photo=buf, caption="Графік зміни пульсу")

    # Надання порад відповідно до результату
    result = context.user_data.get("result", "Задовільно")
    advice_text = "\n\nПоради для покращення:\n"
    for advice in ADVICE[result]:
        advice_text += f"• {advice}\n"

    reply_keyboard = [["Хочу ще математики", "Знову"], ["Завершити"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(advice_text + "\n\nЩо бажаєш далі?", reply_markup=markup)
    return MATH

# Додати математичні завдання
async def math_problems(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Надання математичних завдань користувачу."""
    choice = update.message.text
    
    if choice == "Хочу ще математики":
        # Отримання даних для математичних задач
        pulse_before = context.user_data.get("pulse_before", 70)
        pulse_during = context.user_data.get("pulse_during", 120)
        pulse_after = context.user_data.get("pulse_after", 100)
        pulse_2min = context.user_data.get("pulse_2min", 80)
        increase = context.user_data.get("increase", 50)
        
        # Формування декількох математичних завдань на основі отриманих даних
        math_text = (
            "Ось декілька математичних задач на основі твоїх даних:\n\n"
            f"1. Твій пульс збільшився на {increase} ударів під час вправи. "
            f"На скільки відсотків це більше від початкового стану?\n\n"
            f"2. Якщо пульс після відновлення становить {pulse_2min} ударів за хвилину, "
            f"скільки разів серце б'ється за 10 хвилин?\n\n"
            f"3. Якщо середній пульс у спокої становить 70 ударів за хвилину, "
            f"а під час вправи — {pulse_during} ударів, то яке середнє навантаження на серце?\n\n"
            "Спробуй розв'язати ці задачі самостійно! Відповіді можна перевірити за допомогою калькулятора."
        )
        
        reply_keyboard = [["Знову", "Завершити"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(math_text, reply_markup=markup)
        return END
    
    elif choice == "Знову":
        await update.message.reply_text("Добре, почнемо знову!", reply_markup=ReplyKeyboardRemove())
        return await start(update, context)
    
    elif choice == "Завершити":
        await update.message.reply_text("Дякую за участь! До побачення!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    else:
        await update.message.reply_text("Будь ласка, виберіть опцію з клавіатури.")
        return MATH

# Функція завершення розмови
async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершення розмови."""
    choice = update.message.text

    if choice == "Знову":
        await update.message.reply_text("Добре, почнемо знову.", reply_markup=ReplyKeyboardRemove())
        return await start(update, context)  # Повертаємось до початку розмови
    elif choice == "Завершити":
        await update.message.reply_text("Дякую за участь! До побачення!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END  # Завершення розмови
    else:
        await update.message.reply_text("Будь ласка, виберіть опцію з клавіатури.")
        return END

# Обробник невідомих команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вибачте, я не розумію цю команду.")

# Обробник помилок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

# Основна функція
def main() -> None:
    """Запуск бота."""
    # Створення application
    application = Application.builder().token(TOKEN).build()

    # Створення обробника розмов
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  # Точка входу: команда /start
        states={
            START: [MessageHandler(filters.Text(["Так", "Ні"]), start_choice)],  # Обробка вибору "Так" чи "Ні"
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],  # Отримання віку
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],  # Отримання статі
            EXERCISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, exercise)],  # Отримання типу вправи
            PULSE_BEFORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pulse_before)],  # Отримання пульсу до вправи
            PULSE_DURING: [MessageHandler(filters.TEXT & ~filters.COMMAND, pulse_during)],  # Отримання пульсу під час вправи
            PULSE_AFTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, pulse_after)],  # Отримання пульсу одразу після вправи
            PULSE_2MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, pulse_2min)],  # Отримання пульсу через 2 хвилини після вправи
            ANALYSIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, analysis)],  # Обробка аналізу та вибір графіку
            MATH: [MessageHandler(filters.TEXT & ~filters.COMMAND, math_problems)],  # Математичні завдання
            END: [MessageHandler(filters.TEXT & ~filters.COMMAND, end)]  # Завершення розмови
        },
        fallbacks=[CommandHandler("cancel", end)],  # Обробник команди /cancel для завершення розмови
    )

    # Додавання обробника розмов
    application.add_handler(conv_handler)

    # Додавання обробника невідомих команд
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Додавання обробника помилок
    application.add_error_handler(error)

    # Запуск бота
    print("Бот запущений!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
