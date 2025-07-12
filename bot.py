import logging
from datetime import datetime
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ctransformers import AutoModelForCausalLM
from datetime import timedelta
from dotenv import load_dotenv
import torch
import random
import os

# Cargar variables de entorno
load_dotenv()

ULTIMOS_MENSAJES = int(os.getenv("ULTIMOS_MENSAJES"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH"))
MODEL_PATH = os.getenv("MODEL_PATH")

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HippieSummaryBot:
    def __init__(self, token: str):
        self.token = token
        self.messages_buffer = defaultdict(list)
        #Path del modelo usando path general
        
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            model_file=MODEL_PATH,
            model_type="llama",          # "mistral", "gptj", etc.
            gpu_layers=15,     
            temperature=0.6, 
            context_length=2048,  # Reduce if memory problems
            batch_size=32,  # Small batch size
            threads=6,  # CPU cores for non-accelerated parts
            stream=False,  
           
        )

    def generate_mystical_intro(self) -> str:
        """Genera una introducción mística para el resumen"""
        intros = [
            "🔮 Las energías cósmicas han convergido para traerte este resumen sagrado:",
            "✨ Los vientos del universo susurran los secretos de tu grupo:",
            "🌙 La luna llena ilumina los mensajes más importantes:",
            "🧿 El ojo divino ha observado y resume para ti:",
            "🦋 Las mariposas del conocimiento han recolectado estos mensajes:",
            "💫 El cosmos conspira para ofrecerte esta sabiduría destilada:"
        ]
        return random.choice(intros)    
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(self.generate_mystical_intro())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.chat.type in ['group', 'supergroup']:
            chat_id = update.message.chat.id
            user = update.message.from_user.first_name
            self.messages_buffer[chat_id].append({
                'user': user,
                'text': update.message.text[:MAX_MESSAGE_LENGTH],
                'timestamp': datetime.now()
            })
            print("Mensaje:", update.message.text)
            # Limitar a los últimos 20 mensajes
            if len(self.messages_buffer[chat_id]) > ULTIMOS_MENSAJES:
                self.messages_buffer[chat_id] = self.messages_buffer[chat_id][-ULTIMOS_MENSAJES:]

            # Filtrar mensajes por hora
            now = datetime.now()
            self.messages_buffer[chat_id] = [
                msg for msg in self.messages_buffer[chat_id]
                if (now - msg['timestamp']) < timedelta(hours=1)
            ]

    def build_prompt(self, messages):
        # Crear un prompt con los últimos mensajes del grupo
        joined = "\n".join([f"{m['user']}: {m['text']}" for m in messages])
        return f"""Eres un gurú espiritual de feria, un farsante que mezcla frases de sabiduría cósmica inventada, astrología barata, pseudociencia y mucho humor.
Lee el chat de Telegram y haz un resumen iluminado por usuario, como si se lo explicaras a tus discípulos en una fogata.
Sé gracioso, usa frases ridículas El resumen debe sonar a mezcla de consejo, reflexión y tontería, Y termina siempre con una frase absurda.
Chat:
{joined} 

Resumen Cosmico:"""

    def query_llama(self, prompt: str) -> str:
        try:
            result = self.model(prompt)
            return result.strip()
        except Exception as e: #manejo de errores
            logger.error(f"Error generando resumen: {e}")
            return "🌌 Ups... Se me sobrecargaron los chakras!"

    async def resumen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat.id
        messages = self.messages_buffer.get(chat_id, [])

        if not messages:
            mystical_empty = [
                "🌸 El silencio cósmico reina en este grupo. Quizás es momento de meditar.",
                "✨ Los mensajes están en otra dimensión. Intenta más tarde, ser de luz.",
                "🌙 La energía de los mensajes se ha desvanecido en el éter."
            ]
            await update.message.reply_text(random.choice(mystical_empty))
            return
        prompt = self.build_prompt(messages)
        if len(prompt.split()) > 500:  # Aproximación simple
            await update.message.reply_text("Demasiados chakras para procesar... ¡Namaste!")
            return

        result = self.query_llama(prompt)
        await update.message.reply_text(result)

    def run(self):
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("resumen", self.resumen))
        app.add_handler(CommandHandler("resumido", self.resumen))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        print("🔮 El bot místico está despertando...")
        app.run_polling()

if __name__ == "__main__":
    # Sustituye por tu token
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = HippieSummaryBot(BOT_TOKEN)
    bot.run()
