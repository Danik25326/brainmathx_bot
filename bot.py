from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import sympy

TOKEN = "7543249963:AAGsajvraydao-8U9LzW1297tdMuVV9VptI"

def solve_equation(expression):
    x = sympy.Symbol('x')
    try:
        solution = sympy.solve(sympy.sympify(expression), x)
        return solution
    except Exception as e:
        return f"Помилка: {e}"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привіт! Введи рівняння або нерівність (наприклад, x**2 - 4 = 0), а я її розв’яжу!")

async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text
    try:
        if "a" in user_input:
            result = solve_equation(user_input)
        elif ">" in user_input or "<" in user_input:
            result = solve_equation(user_input)
        else:
            result = solve_equation(user_input)
        
        await update.message.reply_text(f"Розв’язок: {result}")
    except Exception as e:
        await update.message.reply_text("Щось пішло не так 😕 Перевір правильність рівняння.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущено!")  
    app.run_polling()

if __name__ == "__main__":
    main()
