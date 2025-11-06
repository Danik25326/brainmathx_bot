import os
import asyncio
import re
import nest_asyncio
from aiohttp import web  # Фейковий веб-сервер
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from aiogram.fsm.storage.memory import MemoryStorage  # Додаємо storage для Dispatcher
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi, solve_univariate_inequality

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Отримуємо токен

bot = Bot(token=TOKEN, parse_mode="Markdown")
dp = Dispatcher(storage=MemoryStorage())  # Додаємо storage

x = symbols('x')  # Основна змінна

# 📌 Фейковий веб-сервер для Render
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()

    print("🌍 Фейковий сервер запущений, бот активний!")

# 📌 Налаштування команд меню
async def set_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="help", description="Як користуватися ботом?")
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

# 📌 Обробник команди /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")]
    ])
    await message.answer("👋 **Вітаю!** Це BrainMathX – бот для розв’язання математичних виразів!\n\n"
                         "📌 **Що я вмію?**\n"
                         "- Розв’язувати рівняння (наприклад, `2x + 3 = 7`)\n"
                         "- Працювати з логарифмами (`log_2(8) = x`)\n"
                         "- Виконувати тригонометричні обчислення (`sin(30) + cos(60)`) \n"
                         "- Обчислювати корені (`sqrt(25) = 5`)\n\n"
                         "🔹 Вибери, що хочеш розв’язати:", reply_markup=keyboard)

# 📌 Обробник команди /help
@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.answer("📌 **Як користуватися ботом?**\n"
                         "- Введи рівняння, наприклад `2x + 3 = 7`\n"
                         "- Використовуй `sqrt(x)` для коренів\n"
                         "- Використовуй `log_2(x)` для логарифмів\n"
                         "- Використовуй `sin(x)`, `cos(x)`, `tan(x)` для тригонометрії")

# 📌 Обробка кнопок
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data == "equation":
        await callback_query.message.answer("📏 **Введи рівняння (наприклад, `2x + 3 = 7`)**")
    elif data == "inequality":
        await callback_query.message.answer("📊 **Введи нерівність (наприклад, `x^2 > 4`)**")
    elif data == "trigonometry":
        await callback_query.message.answer("📐 **Введи тригонометричний вираз (наприклад, `sin(30) + cos(60)`)**")
    elif data == "logarithm":
        await callback_query.message.answer("📚 **Введи логарифм (наприклад, `log_2(8)`)**")
    await callback_query.answer()

# 📌 Функція для виправлення синтаксису виразів
def fix_equation(equation_str):
    equation_str = equation_str.replace("^", "**")
    equation_str = equation_str.replace("√(", "sqrt(")
    equation_str = equation_str.replace("Sqrt", "sqrt")
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)
    equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)
    return equation_str

# 📌 Основна функція розрахунків
@dp.message()
async def solve_math(message: types.Message):
    user_input = message.text.strip()

    if user_input.startswith("/"):
        return

    try:
        expression = fix_equation(user_input)

        # ✅ Рівняння (з "=")
        if "=" in expression:
            left, right = expression.split("=")
            equation = Eq(eval(left.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}),
                          eval(right.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}))
            solution = solve(equation, x)
            await message.answer(f"✏️ **Розв’язок:** `x = {solution}` ✅")

        # ✅ Нерівності (розв’язання через Sympy)
        elif any(sign in expression for sign in [">", "<", ">=", "<="]):
            inequality = eval(expression, {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi})
            solution = solve_univariate_inequality(inequality, x, relational=False)
            await message.answer(f"📊 **Розв’язок нерівності:** `{solution}` ✅")

        # ✅ Просто вираз (тригонометрія, логарифми, корені)
        else:
            result = eval(expression, {
                "x": x,
                "sin": lambda a: sin(a * pi / 180).evalf(),
                "cos": lambda a: cos(a * pi / 180).evalf(),
                "tan": lambda a: tan(a * pi / 180).evalf(),
                "log": log, "sqrt": sqrt, "pi": pi
            })
            await message.answer(f"🔢 **Відповідь:** `{result}` ✅")

    except Exception as e:
        await message.answer(f"❌ **Помилка:** {e}")

# 📌 Запуск бота + фейкового сервера
async def main():
    try:
        await set_menu()
        await asyncio.gather(
            start_server(),
            dp.start_polling(bot, skip_updates=True)
        )
    except Exception as e:
        print(f"🚨 Помилка в роботі бота: {e}")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
