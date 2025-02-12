import os
import asyncio
import re
from aiohttp import web  # Фейковий веб-сервер
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi, diff, integrate

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Отримуємо токен

bot = Bot(token=TOKEN, parse_mode="Markdown")
dp = Dispatcher()

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

# 📌 Головне меню
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")],
        [InlineKeyboardButton(text="📈 Похідна", callback_data="derivative"),
         InlineKeyboardButton(text="📉 Інтеграл", callback_data="integral")]
    ])
    await message.answer("👋 **Вітаю!** Це BrainMathX – бот для розв’язання математичних виразів!\n\n"
                         "📌 **Що я вмію?**\n"
                         "- Розв’язувати рівняння (наприклад, `2x + 3 = 7`)\n"
                         "- Працювати з логарифмами (`log_2(8) = x`)\n"
                         "- Виконувати тригонометричні обчислення (`sin(30) + cos(60)`) \n"
                         "- Обчислювати корені (`sqrt(25) = 5`)\n"
                         "- Знаходити похідні та інтеграли!\n\n"
                         "🔹 Вибери, що хочеш розв’язати:", reply_markup=keyboard)

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
    elif data == "derivative":
        await callback_query.message.answer("📈 **Введи функцію для похідної (наприклад, `x**3 + 2x`)**")
    elif data == "integral":
        await callback_query.message.answer("📉 **Введи функцію для інтеграла (наприклад, `x**3 + 2x`)**")
    await callback_query.answer()

# 📌 Виправлення синтаксису
def fix_equation(equation_str):
    equation_str = equation_str.replace("^", "**")  
    equation_str = equation_str.replace("√(", "sqrt(")  
    equation_str = equation_str.replace("Sqrt", "sqrt")  
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)  
    equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)  
    return equation_str

# 📌 Обробка виразів
@dp.message()
async def solve_math(message: types.Message):
    user_input = message.text.strip()

    if user_input.startswith("/"):
        return

    try:
        expression = fix_equation(user_input)

        if "=" in expression:
            left, right = expression.split("=")
            equation = Eq(eval(left.strip(), {"x": x}), eval(right.strip(), {"x": x}))
            solution = solve(equation, x)
            await message.answer(f"✏️ **Розв’язок:** `x = {solution}` ✅")

        elif ">" in expression or "<" in expression:
            result = eval(expression, {"x": x})
            symbol = "✅" if result else "❌"
            text_result = "True (вірно)" if result else "False (невірно)"
            await message.answer(f"🔢 **Відповідь:** `{text_result}` {symbol}")

        elif "diff" in expression or "**" in expression:
            result = diff(eval(expression, {"x": x}), x)
            explanation = f"📌 Похідна `{user_input}`:\n\n"
            explanation += "1️⃣ Використовуємо правило степеня: d/dx [xⁿ] = n * x^(n-1)\n"
            explanation += f"🎯 Відповідь: `{result}`"
            await message.answer(explanation)

        elif "integrate" in expression or "**" in expression:
            result = integrate(eval(expression, {"x": x}), x)
            explanation = f"📌 Інтеграл `{user_input}`:\n\n"
            explanation += "1️⃣ Використовуємо основні правила інтеграції.\n"
            explanation += f"🎯 Відповідь: `{result} + C`"
            await message.answer(explanation)

        else:
            result = eval(expression, {"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi})
            await message.answer(f"🔢 **Відповідь:** `{result}` ✅")

    except Exception as e:
        await message.answer(f"❌ **Помилка:** {e}")

# 📌 Запуск бота + сервера
async def main():
    await set_menu()
    await asyncio.gather(
        start_server(),
        dp.start_polling(bot, skip_updates=True)
    )

if __name__ == "__main__":
    asyncio.run(main())
