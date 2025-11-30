import os
import asyncio
import re
import logging
from typing import Any, Dict  # Додаємо Dict для type hints
import nest_asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
    MenuButtonCommands
)
from aiogram.fsm.storage.memory import MemoryStorage
from sympy import symbols, Eq, solve, sin, cos, tan, log, sqrt, pi, sympify, SympifyError

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не встановлено!")

bot = Bot(token=TOKEN, parse_mode="Markdown")
dp = Dispatcher(storage=MemoryStorage())

x = symbols('x')

# Безпечний словник символів з явними типами
SAFE_SYMBOLS: Dict[str, Any] = {
    'x': x,
    'sin': sin,
    'cos': cos,
    'tan': tan,
    'log': log,
    'sqrt': sqrt,
    'pi': pi,
    'abs': abs
}

class MathProcessor:
    @staticmethod
    def fix_equation(equation_str: str) -> str:
        """Безпечне перетворення математичних виразів"""
        replacements = [
            ("^", "**"),
            ("√(", "sqrt("),
            ("Sqrt", "sqrt"),
            ("×", "*"),
            ("÷", "/")
        ]

        for old, new in replacements:
            equation_str = equation_str.replace(old, new)

        equation_str = re.sub(r'log_(\d+)\((.*?)\)', r'log(\2, \1)', equation_str)
        equation_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation_str)

        return equation_str.strip()

    @staticmethod
    def safe_parse(expression: str) -> Any:
        """Безпечне парсингу математичних виразів"""
        try:
            # 🔴 ВИПРАВЛЕННЯ: Використовуємо eval для сумісності з lambda
            # Спочатку перетворюємо градуси в радіани для тригонометрії
            expression = MathProcessor._convert_degrees_to_radians(expression)
            return eval(expression, {"__builtins__": {}}, SAFE_SYMBOLS)
        except Exception as e:
            raise ValueError(f"Невірний математичний вираз: {e}")

    @staticmethod
    def _convert_degrees_to_radians(expression: str) -> str:
        """Конвертує градуси в радіани для тригонометричних функцій"""
        # Простий спосіб обробки градусів
        expression = re.sub(r'sin\((\d+)\)', r'sin(\1*pi/180)', expression)
        expression = re.sub(r'cos\((\d+)\)', r'cos(\1*pi/180)', expression)
        expression = re.sub(r'tan\((\d+)\)', r'tan(\1*pi/180)', expression)
        return expression

# Ініціалізація процесора
math_processor = MathProcessor()

# Веб-сервер
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port_str = os.getenv("PORT", "8080")
    port = int(port_str.strip()) if port_str else 8080
    
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("🌍 Сервер запущений")

# Команди меню
async def set_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="help", description="Як користуватися ботом?")
    ])
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

# Обробники
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📏 Рівняння", callback_data="equation"),
            InlineKeyboardButton(text="📊 Нерівності", callback_data="inequality")
        ],
        [
            InlineKeyboardButton(text="📐 Тригонометрія", callback_data="trigonometry"),
            InlineKeyboardButton(text="📚 Логарифми", callback_data="logarithm")
        ]
    ])
    await message.answer(
        "👋 **Вітаю!** Це BrainMathX – бот для розв'язання математичних виразів!\n\n"
        "📌 **Що я вмію?**\n"
        "- Розв'язувати рівняння (наприклад, `2x + 3 = 7`)\n"
        "- Працювати з логарифмами (`log_2(8) = x`)\n"
        "- Виконувати тригонометричні обчислення (`sin(30) + cos(60)`)\n"
        "- Обчислювати корені (`sqrt(25) = 5`)\n\n"
        "🔹 Вибери, що хочеш розв'язати:",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.answer(
        "📌 **Як користуватися ботом?**\n"
        "- Введи рівняння, наприклад `2x + 3 = 7`\n"
        "- Використовуй `sqrt(x)` для коренів\n"
        "- Використовуй `log_2(x)` для логарифмів\n"
        "- Використовуй `sin(x)`, `cos(x)`, `tan(x)` для тригонометрії"
    )

@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data

    # 🔴 ВИПРАВЛЕННЯ: Перевірка на наявність message
    if not callback_query.message:
        return

    if data == "equation":
        await callback_query.message.answer("📏 **Введи рівняння (наприклад, `2x + 3 = 7`)**")
    elif data == "inequality":
        await callback_query.message.answer("📊 **Введи нерівність (наприклад, `x^2 > 4`)**")
    elif data == "trigonometry":
        await callback_query.message.answer("📐 **Введи тригонометричний вираз (наприклад, `sin(30) + cos(60)`)**")
    elif data == "logarithm":
        await callback_query.message.answer("📚 **Введи логарифм (наприклад, `log_2(8)`)**")

    await callback_query.answer()

@dp.message()
async def solve_math(message: types.Message):
    if not message.text:
        return
        
    user_input = message.text.strip()

    if user_input.startswith("/"):
        return

    try:
        expression = math_processor.fix_equation(user_input)

        if "=" in expression:
            left, right = expression.split("=", 1)
            
            left = left.strip() if left else "0"
            right = right.strip() if right else "0"
            
            left_expr = math_processor.safe_parse(left)
            right_expr = math_processor.safe_parse(right)

            equation = Eq(left_expr, right_expr)
            solution = solve(equation, x)

            if solution:
                await message.answer(f"✏️ **Розв'язок:** `x = {solution}` ✅")
            else:
                await message.answer("❌ Рівняння не має розв'язків")

        elif any(sign in expression for sign in [">", "<", ">=", "<="]):
            result = math_processor.safe_parse(expression)
            text_result = "True (вірно)" if result else "False (невірно)"
            symbol = "✅" if result else "❌"
            await message.answer(f"🔢 **Відповідь:** `{text_result}` {symbol}")

        else:
            result = math_processor.safe_parse(expression)
            await message.answer(f"🔢 **Відповідь:** `{result}` ✅")

    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception as e:
        logger.error(f"Помилка обробки повідомлення: {e}")
        await message.answer("❌ Сталася внутрішня помилка. Спробуйте інший вираз.")

async def main():
    try:
        await set_menu()
        await asyncio.gather(
            start_server(),
            dp.start_polling(bot, skip_updates=True)
        )
    except Exception as e:
        logger.error(f"🚨 Помилка запуску бота: {e}")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
