import os
import asyncio
import re
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi, diff, integrate, sympify, factorial

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

x = symbols('x')

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 10000)))
    await site.start()
    print("\U0001F30D Бот працює!")

async def set_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="help", description="Як користуватися ботом?")
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\U0001F4CF Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="\U0001F4CA Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="\U0001F4D0 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="\U0001F4DA Логарифми", callback_data="logarithm")],
        [InlineKeyboardButton(text="\U0001F4C8 Похідна", callback_data="derivative"),
         InlineKeyboardButton(text="\U0001F4C9 Інтеграл", callback_data="integral")]
    ])
    await message.answer("\U0001F44B <b>Вітаю!</b> Це BrainMathX – бот для розв’язання математичних виразів!\n\n"
                         "\U0001F4CC <b>Що я вмію?</b>\n"
                         "- Розв’язувати рівняння (наприклад, <code>2x + 3 = 7</code>)\n"
                         "- Працювати з логарифмами (<code>log_2(8) = x</code>)\n"
                         "- Виконувати тригонометричні обчислення (<code>sin(30) + cos(60)</code>)\n"
                         "- Обчислювати похідні та інтеграли!\n\n"
                         "\U0001F539 Обери, що хочеш розв’язати:", reply_markup=keyboard)

@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data == "derivative":
        await callback_query.message.answer("\U0001F4C8 <b>Введи функцію для похідної</b> (наприклад, <code>x**3 + 2*x</code>):")
    elif data == "integral":
        await callback_query.message.answer("\U0001F4C9 <b>Введи функцію для інтеграла</b> (наприклад, <code>x**3 + 2*x</code>):")
    await callback_query.answer()

def fix_equation(equation_str):
    equation_str = equation_str.replace("^", "**")
    equation_str = equation_str.replace("√(", "sqrt(").replace("Sqrt", "sqrt")
    equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)
    equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)
    equation_str = re.sub(r'(\d)!', r'factorial(\1)', equation_str)
    return equation_str

@dp.message()
async def solve_math(message: types.Message):
    user_input = message.text.strip()
    
    if user_input.startswith("/"):
        return
    
    try:
        expression = fix_equation(user_input)
        parsed_expr = sympify(expression, locals={"x": x, "sin": sin, "cos": cos, "tan": tan, "log": log, "sqrt": sqrt, "pi": pi, "factorial": factorial})
        
        if message.text.startswith("diff "):
            result = diff(parsed_expr, x)
            await message.answer(f"\U0001F4CC <b>Похідна</b> <code>{user_input}</code>: <code>{result}</code>")
        elif message.text.startswith("integrate "):
            result = integrate(parsed_expr, x)
            await message.answer(f"\U0001F4CC <b>Інтеграл</b> <code>{user_input}</code>: <code>{result} + C</code>")
        else:
            result = parsed_expr.evalf()
            await message.answer(f"\U0001F522 <b>Відповідь:</b> <code>{result}</code> ✅")
    except Exception as e:
        await message.answer(f"❌ <b>Помилка:</b> {e}")

async def main():
    await set_menu()
    server_task = asyncio.create_task(start_server())
    bot_task = asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    await asyncio.gather(server_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())
