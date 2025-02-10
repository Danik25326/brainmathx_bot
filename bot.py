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

# 📌 Автоматична обробка введення користувача
def fix_equation(equation_str):
    """Автоматично виправляє введення користувача"""
    equation_str = equation_str.replace("^", "**")  
    equation_str = equation_str.replace("√(", "sqrt(")  
    equation_str = equation_str.replace("Sqrt", "sqrt")  
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)  

    # ✅ Додаємо пробіли перед змінними (щоб не було "2x", а було "2*x")
    equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)

    return equation_str

# 📌 Функція для розрахунків
@dp.message()
async def handle_messages(message: types.Message):
    """Перевіряємо, чи це команда чи математичний вираз"""
    if message.text.startswith("/"):
        return  # ✅ Ігноруємо всі команди, щоб бот їх не рахував
    
    try:
        expression = fix_equation(message.text)

        # ✅ Якщо це рівняння (містить "=")
        if "=" in expression:
            left, right = expression.split("=")
            equation = Eq(eval(left.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}),
                          eval(right.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}))
            solution = solve(equation, x)
            await message.answer(f"✏️ **Розв’язок:** `x = {solution}` ✅")
        else:
            result = eval(expression, {"x": x, "sin": lambda a: sin(a * pi / 180).evalf(),
                                       "cos": lambda a: cos(a * pi / 180).evalf(),
                                       "tan": lambda a: tan(a * pi / 180).evalf(),
                                       "log": log, "sqrt": sqrt, "pi": pi})
            await message.answer(f"🔢 **Відповідь:** `{result}` ✅")
    
    except Exception as e:
        await message.answer(f"❌ **Помилка:** {e}")

# 📌 Обробка натискання кнопок (багаторазова)
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
    
    await callback_query.answer()  # ✅ Це потрібно, щоб кнопки працювали багаторазово!

# 📌 Обробка команди /start (перезапускає кнопки)
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")]
    ])
    
    await message.answer("👋 **Вітаю!** Це математичний бот 2.0! Вибери, що ти хочеш розв’язати:", 
                         reply_markup=keyboard)

# 📌 Запуск бота
async def main():
    await set_menu()  # Встановлюємо меню
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
