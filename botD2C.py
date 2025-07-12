import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Cargar variables de entorno
import os
from dotenv import load_dotenv  

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Configuración del bot
D2C_BOT_TOKEN = os.getenv('D2C_BOT_TOKEN')
D2C_API_KEY = os.getenv('D2C_API_KEY')
D2C_API_URL = os.getenv('D2C_API_URL')

intro_text = (
    "🩺 *Welcome to D2CMedBot!* 🤖\n\n"
    "I’m your virtual assistant for the *D2C Provider App*. "
    "I can answer questions about how the platform works, guide you through features, "
    "or help resolve technical issues.\n\n"
    "🔹 *Available Commands:*\n"
    "/start - Launch the bot\n"
    "/help - Show this guide\n"
    "/question - Ask about the system (e.g., 'How to book an appointment?')\n\n"
    "💡 *Tip:* Try asking me things like:\n"
    "- *'How do I reset my password?'*\n"
    "- *'Where I can request shift?'*"
)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(intro_text)

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "I'm D2CMedBot, your personal assistant, I can help you with any question you have related to D2C Provider App.\n\n"
        "You can use the following commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/question or /q - Ask a question"
    )
    await update.message.reply_text(help_text)

# Comando /question
async def question_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Please, write your question. You will be asked to rate the answer after receiving it.')
    context.user_data['awaiting_question'] = True

# Manejador de mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_question'):
        user_question = update.message.text
        await process_question(update, context, user_question)
        context.user_data['awaiting_question'] = False
        context.user_data['awaiting_rating'] = True
        context.user_data['last_question'] = user_question  # Guardamos la pregunta para referencia
        await update.message.reply_text('Please rate the answer from 1 to 10:')
    elif context.user_data.get('awaiting_rating'):
        await handle_rating(update, context)

# Función para procesar la pregunta
async def process_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question: str):
    headers = {
        'Authorization': f'{D2C_API_KEY}'
    }
    data = {
        'question': question
    }

    try:
        response = requests.post(D2C_API_URL, headers=headers, json=data)
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 200

        result = response.json()
        answer = result.get('answer')
        filter_threshold = result.get('filter_threshold')
        total_tokens = result.get('total_tokens')
        tokens_per_second = result.get('tokens_per_second')

        response_text = (
            f"🩺 *Response:*\n"
            f"```\n"
            f"{answer}\n"
            f"```\n\n"
            f"📈 *System Statistics*\n"
            f"┣ 🔎 Filter Threshold: {filter_threshold}\n"
            f"┣ 🧠 Total Tokens: {total_tokens}\n"
            f"┗ ⚡ Speed: {tokens_per_second} tokens/sec"
        )
        await update.message.reply_text(response_text)

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        await update.message.reply_text(f"Error HTTP: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        await update.message.reply_text(f"Error de solicitud: {req_err}")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
        await update.message.reply_text(f"Error inesperado: {err}")

# Función para manejar la calificación
async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_rating'):
        try:
            rating = int(update.message.text)
            if 1 <= rating <= 10:
                await update.message.reply_text(f'Thank you for your rating: {rating}')
                context.user_data['awaiting_rating'] = False
            else:
                await update.message.reply_text('Please enter a rating between 1 and 10.')
        except ValueError:
            await update.message.reply_text('Invalid input. Please enter a number between 1 and 10.')

def main():
    application = ApplicationBuilder().token(D2C_BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_command)
    question_handler = CommandHandler('question', question_command)
    question_handler = CommandHandler('q', question_command)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    rating_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_rating)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(question_handler)
    application.add_handler(message_handler)
    application.add_handler(rating_handler)

    application.run_polling()

if __name__ == '__main__':
    main()