import os
import asyncio
import re
import nest_asyncio
from aiohttp import web  # Фейковий веб-сервер
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, MenuButtonCommands
from aiogram.fsm.storage.memory import MemoryStorage  # Додаємо storage для Dispatcher
from sympy import (
    symbols, Eq, solve, sin, cos, tan, log, sqrt, pi,
    solve_univariate_inequality
)

# --- Налаштування ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Отримуємо токен
bot = Bot(token=TOKEN, parse_mode="Markdown")
dp = Dispatcher(storage=MemoryStorage())  # Додаємо storage
x = symbols('x')  # Основна змінна

# --- Фейковий веб-сервер для пінгу (UptimeRobot / Replit preview) ---
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

# --- Меню команд ---
async def set_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="help", description="Як користуватися ботом?")
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

# --- Команда /start ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
         InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")],
        [InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
         InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")]
    ])
    await message.answer(
        "👋 **Вітаю!** Це BrainMathX – бот для розв’язання математичних виразів!\n\n"
        "📌 **Що я вмію?**\n"
        "- Розв’язувати рівняння (наприклад, `2x + 3 = 7`)\n"
        "- Працювати з логарифмами (`log_2(8) = x`)\n"
        "- Виконувати тригонометричні обчислення (`sin(30) + cos(60)`) \n"
        "- Обчислювати корені (`sqrt(25) = 5`)\n\n"
        "🔹 Вибери, що хочеш розв’язати:", reply_markup=keyboard)

# --- Команда /help ---
@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.answer(
        "📌 **Як користуватися ботом?**\n"
        "- Введи рівняння, наприклад `2x + 3 = 7`\n"
        "- Використовуй `sqrt(x)` для коренів\n"
        "- Використовуй `log_2(x)` для логарифмів\n"
        "- Використовуй `sin(x)`, `cos(x)`, `tan(x)` для тригонометрії"
    )

# --- Обробка кнопок ---
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

# --- Виправлення синтаксису (корисні заміни) ---
def fix_equation(equation_str: str) -> str:
    # заміни типу ^ -> **, √( -> sqrt(
    s = equation_str.replace("^", "**")
    s = s.replace("√(", "sqrt(")
    s = s.replace("Sqrt", "sqrt")
    # log_2(x) -> log(x, 2)
    s = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', s)
    # 2x -> 2*x ; 3sin -> 3*sin
    s = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', s)
    # видалимо подвійні пробіли
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# --- Допоміжні контексти для eval ---
SAFE_GLOBALS = {"__builtins__": None}
SAFE_LOCALS = {
    "x": x,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "log": log,
    "sqrt": sqrt,
    "pi": pi
}

# --- Основна функція обробки вхідних повідомлень ---
@dp.message()
async def solve_math(message: types.Message):
    user_input = message.text.strip()
    if not user_input:
        return
    if user_input.startswith("/"):
        return

    try:
        expr = fix_equation(user_input)

        # 1) Рівняння з "="
        if "=" in expr:
            left, _, right = expr.partition("=")
            left_val = eval(left.strip(), SAFE_GLOBALS, SAFE_LOCALS)
            right_val = eval(right.strip(), SAFE_GLOBALS, SAFE_LOCALS)
            equation = Eq(left_val, right_val)
            solution = solve(equation, x)
            await message.answer(f"✏️ **Розв’язок:** `x = {solution}` ✅")
            return

        # 2) Нерівності (перевіряємо наявність знаків порівняння)
        if any(op in expr for op in [">=", "<=", ">", "<"]):
            # Якщо є змінна 'x' у виразі -> режим розв'язування нерівності
            if re.search(r'\bx\b', expr):  # перевіряємо присутність 'x' як окремого символа або у вигляді 2*x після fix
                try:
                    inequality = eval(expr, SAFE_GLOBALS, SAFE_LOCALS)
                    sol = solve_univariate_inequality(inequality, x, relational=False)
                    await message.answer(f"📊 **Розв’язок нерівності:** `{sol}` ✅")
                except Exception as e:
                    await message.answer(f"❌ **Помилка при розв'язанні нерівності:** {e}")
                return
            else:
                # Немає 'x' — просто обчислюємо істинність (True/False)
                try:
                    # Для числових виразів даємо доступ до математичних функцій теж
                    numeric_locals = {"sin": lambda a: float(sin(a * pi / 180).evalf()),
                                      "cos": lambda a: float(cos(a * pi / 180).evalf()),
                                      "tan": lambda a: float(tan(a * pi / 180).evalf()),
                                      "log": lambda a, b=None: float(log(a, b).evalf()) if b else float(log(a).evalf()),
                                      "sqrt": lambda a: float(sqrt(a).evalf())}
                    result = eval(expr, {"__builtins__": None}, numeric_locals)
                    symbol = "✅" if result else "❌"
                    text_result = "True (вірно)" if result else "False (невірно)"
                    await message.answer(f"🔢 **Відповідь:** `{text_result}` {symbol}")
                except Exception as e:
                    await message.answer(f"❌ **Помилка при обчисленні логічного виразу:** {e}")
                return

        # 3) Просто вираз (обчислюємо чисельно або тригонометрично)
        try:
            result = eval(expr, SAFE_GLOBALS, SAFE_LOCALS)
            # Якщо повернувся sympy-об'єкт, привести до строкового вигляду
            await message.answer(f"🔢 **Відповідь:** `{result}` ✅")
        except Exception as e:
            await message.answer(f"❌ **Помилка при обчисленні виразу:** {e}")

    except Exception as e:
        await message.answer(f"❌ **Невідома помилка:** {e}")

# --- Запуск бота + фейкового сервера ---
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
