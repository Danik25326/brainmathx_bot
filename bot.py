import os
import re
from sympy import symbols, Eq, solve, sympify
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# 🔹 Отримуємо токен з Environment Variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 🔹 Оголошуємо змінну x
x = symbols('x')

def fix_equation(equation_str):
    """Автоматично виправляє введення користувача"""
    equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)  # 5x → 5*x
    equation_str = equation_str.replace("^", "**")  # x^2 → x**2
    return equation_str

def solve_equation(equation_str):
    """Розв’язує рівняння безпечно"""
    try:
        equation_str = fix_equation(equation_str)
        left, right = equation_str.split("=")
        equation = Eq(sympify(left.strip()), sympify(right.strip()))  # Без eval()
        solution = solve(equation, x)
        return solution
    except Exception as e:
        return f"Помилка: {e}"

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer("👋 Вітаю! Надішли мені рівняння, і я його розв’яжу! (Наприклад: `2x + 3 = 7`)")

@dp.message_handler()
async def solve_math(message: types.Message):
    result = solve_equation(message.text)
    await message.answer(f"✏️ Розв’язок: {result}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
