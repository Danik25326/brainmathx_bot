import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Бере токен із змінних середовища

bot = Bot(token=TOKEN, parse_mode="Markdown")  # Додаємо Markdown для красивого оформлення
dp = Dispatcher()

x = symbols('x')  # Основна змінна для рівнянь

# 📌 Функція для створення кнопок
def main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")]
    ])
    return keyboard

# 📌 Основна функція обчислень
def solve_math_expression(expression_str):
    try:
        # Перевіряємо, чи це рівняння (містить "=")
        if "=" in expression_str:
            left, right = expression_str.split("=")
            equation = Eq(eval(left.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}),
                          eval(right.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}))
            solution = solve(equation, x)
            return f"✏️ **Розв’язок рівняння:**\n\n*x* = `{solution}` ✅"
        
        # Просто вираз (наприклад, sin(30) + cos(60))
        else:
            result = eval(expression_str, {"x": x, "sin": lambda a: sin(a * pi / 180).evalf(),
                                           "cos": lambda a: cos(a * pi / 180).evalf(),
                                           "tan": lambda a: tan(a * pi / 180).evalf(),
                                           "log": log, "sqrt": sqrt, "pi": pi})
            return f"🔢 **Відповідь:** `{result}` ✅"

    except Exception as e:
        return f"❌ **Помилка:** `{e}`"

# 📌 Обробник команди /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 **Вітаю!** Це математичний бот 2.0! Вибери, що ти хочеш розв’язати:", 
        reply_markup=main_keyboard()
    )

# 📌 Обробник натискання кнопок
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

# 📌 Основний обробник повідомлень
@dp.message()
async def solve_math(message: types.Message):
    result = solve_math_expression(message.text)
    await message.answer(result)

# 📌 Запуск бота
async def main():
    await dp.start_polling(bot, skip_updates=True)  # ✅ Додаємо skip_updates=True для уникнення конфліктів

if __name__ == "__main__":
    asyncio.run(main())
