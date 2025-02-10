import os
import re
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt
from sympy.parsing.sympy_parser import transformations, standard_transformations
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters.command import Command
import asyncio

# 🔹 Отримуємо токен з Environment Variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔹 Оголошуємо змінну x (основну змінну для рівнянь)
x = symbols('x')

def fix_equation(equation_str):
    """Автоматично виправляє введення користувача"""
    equation_str = equation_str.replace("^", "**")  # 2^x → 2**x
    equation_str = equation_str.replace("√(", "sqrt(")  # √(x) → sqrt(x)
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)  # log_2(8) → log(8,2)
    return equation_str

def solve_math_expression(expression_str):
    """Розпізнає і розв’язує рівняння, нерівності або вирази"""
    try:
        expression_str = fix_equation(expression_str)
        
        # Перевіряємо, чи це рівняння (містить "=")
        if "=" in expression_str:
            left, right = expression_str.split("=")
            equation = Eq(eval(left.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}),
                          eval(right.strip(), {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi}))
            solution = solve(equation, x)
            return f"✏️ **Розв’язок рівняння:** x = {solution}"
        
        # Якщо це просто вираз (наприклад, sin(30) + cos(60))
        else:
            result = eval(expression_str, {"x": x, "sin": lambda a: sin(a * pi / 180).evalf(),
                                           "cos": lambda a: cos(a * pi / 180).evalf(),
                                           "tan": lambda a: tan(a * pi / 180).evalf(),
                                           "log": log, "sqrt": sqrt, "pi": pi})
            return f"🔢 **Відповідь:** {result}"

    except Exception as e:
        return f"❌ **Помилка:** {e}"
        
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("👋 **Вітаю!** Надішли мені рівняння чи вираз, і я його розв’яжу! \n\n"
                         "📌 **Як вводити:**\n"
                         "- `2^x = 8` (степінь)\n"
                         "- `sqrt(x) = 4` (корінь)\n"
                         "- `log_2(8) = x` (логарифм)\n"
                         "- `sin(x) + cos(x) = 1` (тригонометрія)")

@dp.message()
async def solve_math(message: Message):
    result = solve_math_expression(message.text)
    await message.answer(result)

async def main():
    await dp.start_polling(bot, skip_updates=True)  # ✅ Додаємо skip_updates=True

if __name__ == "__main__":
    asyncio.run(main())

