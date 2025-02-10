pip install aiogram sympy

import re
import os
from sympy import symbols, Eq, solve
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# 🔹 Введи токен твого Telegram-бота
TOKEN = "7543249963:AAFA34wKoAbPBLnYhCYLIPEiA1qy-6tGpFk"

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
    """Розв’язує рівняння"""
    try:
        equation_str = fix_equation(equation_str)  # Форматуємо рівняння
        left, right = equation_str.split("=")  # Розбиваємо рівняння на частини
        equation = Eq(eval(left.strip()), eval(right.strip()))  # Створюємо рівняння
        solution = solve(equation, x)  # Розв’язуємо
        return solution
    except Exception as e:
        return f"Помилка: {e}"

@dp.message_handler()
async def solve_math(message: types.Message):
    result = solve_equation(message.text)
    await message.answer(f"✏️ Розв’язок: {result}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
