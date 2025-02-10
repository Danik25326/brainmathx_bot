import os
import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Отримуємо токен

bot = Bot(token=TOKEN, parse_mode="Markdown")  # Markdown для красивого оформлення
dp = Dispatcher()

x = symbols('x')  # Основна змінна

# 📌 Функція для встановлення кнопки меню
async def set_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="help", description="Як користуватися ботом?"),
        BotCommand(command="equation", description="Розв’язати рівняння"),
        BotCommand(command="inequality", description="Розв’язати нерівність"),
        BotCommand(command="trigonometry", description="Обчислити тригонометрію"),
        BotCommand(command="logarithm", description="Обчислити логарифм"),
        BotCommand(command="donate", description="Підтримати розробника 💰")
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())  # Встановлюємо меню кнопок

# 📌 Обробка команд
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("👋 **Вітаю!** Це математичний бот 2.0! Вибери, що ти хочеш розв’язати:", 
                         reply_markup=main_keyboard())

@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.answer("📌 **Як використовувати бота?**\n"
                         "- Введи рівняння, наприклад `2x + 3 = 7`\n"
                         "- Використовуй `sqrt(x)` для коренів\n"
                         "- Використовуй `log_2(x)` для логарифмів\n"
                         "- Використовуй `sin(x)`, `cos(x)`, `tan(x)` для тригонометрії")

@dp.message(Command("equation"))
async def equation_info(message: types.Message):
    await message.answer("📏 **Введи рівняння (наприклад, `2x + 3 = 7`)**")

@dp.message(Command("inequality"))
async def inequality_info(message: types.Message):
    await message.answer("📊 **Введи нерівність (наприклад, `x^2 > 4`)**")

@dp.message(Command("trigonometry"))
async def trigonometry_info(message: types.Message):
    await message.answer("📐 **Введи тригонометричний вираз (наприклад, `sin(30) + cos(60)`)**")

@dp.message(Command("logarithm"))
async def logarithm_info(message: types.Message):
    await message.answer("📚 **Введи логарифм (наприклад, `log_2(8)`)**")

@dp.message(Command("donate"))
async def donate_info(message: types.Message):
    await message.answer("💰 **Хочеш підтримати проект?**\n"
                         "🔹 Monobank: `https://send.monobank.ua/jar/ТВОЄ_ПОСИЛАННЯ`\n"
                         "🔹 PayPal: `ТВОЄ_ПОСИЛАННЯ`\n"
                         "Дякую за підтримку! 🙌")

# 📌 Функція для створення кнопок
def main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")]
    ])
    return keyboard

# 📌 Основний обробник повідомлень (математика)
@dp.message()
async def solve_math(message: types.Message):
    try:
        result = solve_math_expression(message.text)
        await message.answer(result)
    except Exception as e:
        await message.answer(f"❌ **Помилка:** {e}")

# 📌 Автоматична обробка записів користувача
def fix_equation(equation_str):
    equation_str = equation_str.replace("^", "**")  # 2^x → 2**x
    equation_str = equation_str.replace("√(", "sqrt(")  # √(x) → sqrt(x)
    equation_str = equation_str.replace("Sqrt", "sqrt")  # Sqrt(x) → sqrt(x)
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)  # log_2(x) → log(x, 2)
    return equation_str

# 📌 Функція для розрахунків
def solve_math_expression(expression_str):
    expression_str = fix_equation(expression_str)  # Виправляємо введення

    # Перевіряємо, чи це рівняння
    if "=" in expression_str:
        left, right = expression_str.split("=")
        equation = Eq(eval(left.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}),
                      eval(right.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}))
        solution = solve(equation, x)
        return f"✏️ **Розв’язок рівняння:**\n\n*x* = `{solution}` ✅"
    
    # Обчислення виразу (наприклад, sin(30) + cos(60))
    else:
        result = eval(expression_str, {"x": x, "sin": lambda a: sin(a * pi / 180).evalf(),
                                       "cos": lambda a: cos(a * pi / 180).evalf(),
                                       "tan": lambda a: tan(a * pi / 180).evalf(),
                                       "log": log, "sqrt": sqrt, "pi": pi})
        return f"🔢 **Відповідь:** `{result}` ✅"

# 📌 Запуск бота
async def main():
    await set_menu()  # Встановлюємо меню
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
