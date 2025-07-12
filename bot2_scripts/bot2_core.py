import logging
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import List, Dict, Any
import random
import os
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Estas se moverán a variables de entorno más adelante según el plan
ULTIMOS_MENSAJES = int(os.getenv("ULTIMOS_MENSAJES", 20))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", 500))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Importar las clases Handler y las listas de mensajes vacíos originales si aún son necesarias
# (aunque idealmente, las clases handler deberían manejar sus propios mensajes vacíos si se pasan en el constructor)
from .handlers.mistico_handler import MisticoHandler
from .handlers.malandro_handler import MalandroHandler
from .handlers.cinico_handler import CinicoHandler

# Listas de mensajes vacíos (pueden ser pasadas a los constructores de los handlers)
# o los handlers pueden tener sus propios defaults si no se pasan.
# Por consistencia con el código anterior, las mantendremos aquí y las pasaremos.
EMPTY_MYSTICAL_RESPONSES = [
    "🌸 El silencio cósmico reina en este grupo. Quizás es momento de meditar.",
    "✨ Los mensajes están en otra dimensión. Intenta más tarde, ser de luz.",
    "🌙 La energía de los mensajes se ha desvanecido en el éter."
]
EMPTY_MALANDRO_RESPONSES = [
    "Esta vaina esta mas sola que cajera en peaje ",
    "Verga chamo a este grupo se lo llevo la policia",
    "Bulda e solo!"
]
EMPTY_CINICO_RESPONSES = [
    "La soledad no es mala… hasta que te das cuenta de que tu mejor conversación es con Siri.",
    "Al fin dejaron de escribir, no vuelvan",
    "La esperanza es lo último que se pierde… espero que no escriban mas"
]

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class HippieSummaryBot:
    def __init__(self, token: str):
        if not token:
            logger.error("El token del bot no está configurado. Asegúrate de que BOT_TOKEN está en tu .env o variables de entorno.")
            raise ValueError("Token del bot no proporcionado.")
        self.token = token
        self.messages_buffer = defaultdict(list)
        self.current_tone = 'mistico'  # Tono por defecto

        # Cargar prompts desde variables de entorno
        prompt_mistico_template = os.getenv("PROMPT_MISTICO")
        prompt_malandro_template = os.getenv("PROMPT_MALANDRO")
        prompt_cinico_template = os.getenv("PROMPT_CINICO")

        # Validar que los prompts se hayan cargado
        if not prompt_mistico_template:
            logger.warning("PROMPT_MISTICO no encontrado en .env. Usando valor por defecto.")
            prompt_mistico_template = "Eres un ser místico por defecto."
        if not prompt_malandro_template:
            logger.warning("PROMPT_MALANDRO no encontrado en .env. Usando valor por defecto.")
            prompt_malandro_template = "Eres un malandro por defecto."
        if not prompt_cinico_template:
            logger.warning("PROMPT_CINICO no encontrado en .env. Usando valor por defecto.")
            prompt_cinico_template = "Eres un cínico por defecto."

        # Instanciar handlers
        self.handlers = {
            'mistico': MisticoHandler(prompt_mistico_template, EMPTY_MYSTICAL_RESPONSES),
            'malandro': MalandroHandler(prompt_malandro_template, EMPTY_MALANDRO_RESPONSES),
            'cinico': CinicoHandler(prompt_cinico_template, EMPTY_CINICO_RESPONSES)
        }
        try:
            self.current_handler = self.handlers[self.current_tone]
        except KeyError:
            logger.error(f"Tono inicial '{self.current_tone}' no es un handler válido. Volviendo a 'mistico'.")
            self.current_tone = 'mistico'
            self.current_handler = self.handlers[self.current_tone]

    def get_intro(self) -> str:
        """Obtiene una introducción del handler actual."""
        return self.current_handler.get_intro()

    async def cambiar_tono(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cambia el tono del bot y actualiza el handler actual."""
        if not context.args:
            await update.message.reply_text(
                "Uso: /tono [mistico|malandro|cinico]\n\n"
                "Ejemplo: /tono malandro"
            )
            return

        nuevo_tono = context.args[0].lower()
        if nuevo_tono in self.handlers:
            self.current_tone = nuevo_tono
            self.current_handler = self.handlers[nuevo_tono]
            tonos_respuestas = { # Se podrían mover estas respuestas a los handlers también
                'mistico': '🌌 Tono místico activado. Las estrellas guían mis palabras...',
                'malandro': '🕶️ ¡Ahorita ando en modo malandro, pendiente de una!',
                'cinico': '😒 Si la ignorancia es felicidad, este grupo debe estar en éxtasis...'
            }
            await update.message.reply_text(tonos_respuestas[nuevo_tono])
            logger.info(f"Tono cambiado a: {nuevo_tono}")
        else:
            await update.message.reply_text(
                f"Tono no válido: '{nuevo_tono}'. Usa: {', '.join(self.handlers.keys())}"
            )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "¡Hola! Soy un bot de resúmenes con personalidad.\n"
            "Usa /tono [mistico|malandro|cinico] para cambiar mi forma de hablar.\n"
            "Actualmente estoy en modo: " + self.current_tone + "\n"
            "Si necesitas un resumen, usa /resumen o /resumido"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.chat.type in ['group', 'supergroup'] and update.message.text:
            chat_id = update.message.chat.id
            user = update.message.from_user.first_name if update.message.from_user else "UsuarioDesconocido"

            self.messages_buffer[chat_id].append({
                'user': user,
                'text': update.message.text[:MAX_MESSAGE_LENGTH],
                'timestamp': datetime.now()
            })
            logger.info(f"Mensaje recibido en chat {chat_id} de {user}: {update.message.text[:50]}...")

            # Limitar a los últimos ULTIMOS_MENSAJES mensajes
            if len(self.messages_buffer[chat_id]) > ULTIMOS_MENSAJES:
                self.messages_buffer[chat_id] = self.messages_buffer[chat_id][-ULTIMOS_MENSAJES:]

            # Filtrar mensajes por hora (ej. última hora)
            # Esta lógica puede necesitar ajuste o hacerse configurable
            # now = datetime.now()
            # self.messages_buffer[chat_id] = [
            #     msg for msg in self.messages_buffer[chat_id]
            #     if (now - msg['timestamp']) < timedelta(hours=1)
            # ]

    def build_prompt(self, messages: List[Dict[str, Any]]) -> str:
        # Delegar la construcción del prompt al handler actual
        return self.current_handler.get_prompt(messages)

    def query_llama(self, prompt: str) -> str:
        if not OPENROUTER_API_KEY:
            logger.error("OPENROUTER_API_KEY no está configurado.")
            return "Error: La API key para el servicio de resumen no está configurada."
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + OPENROUTER_API_KEY,
                    "Content-Type": "application/json",
                    # "HTTP-Referer": "<YOUR_SITE_URL>", # Opcional
                    # "X-Title": "<YOUR_SITE_NAME>", # Opcional
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-chat-v3-0324:free", # Modelo de ejemplo, puede cambiar
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            response.raise_for_status() # Lanza un error para respuestas 4xx/5xx
            result = response.json()

            if result.get('choices') and result['choices'][0].get('message') and result['choices'][0]['message'].get('content'):
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"Respuesta inesperada de la API: {result}")
                return "🌌 Hubo un destello cósmico inesperado y no pude procesar el resumen."

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red o HTTP generando resumen: {e}")
            return "📡 Parece que los astros no están alineados para la comunicación. Intenta más tarde."
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return "🚧 Ups... Algo se cruzó en el camino astral. No pude generar el resumen."

    async def resumen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat.id
        messages = self.messages_buffer.get(chat_id, [])

        if not messages:
            # Obtener respuesta vacía del handler actual
            empty_response = self.current_handler.get_empty_response()
            await update.message.reply_text(empty_response)
            return

        prompt_text = self.build_prompt(messages)

        # Podríamos añadir una validación más robusta para la longitud del prompt
        if len(prompt_text) > 4000: # Límite arbitrario, ajustar según el modelo
            logger.warning(f"El prompt para el chat {chat_id} es muy largo.")
            await update.message.reply_text("🧘 Demasiados susurros cósmicos para procesar en este momento... Intenta con menos mensajes.")
            return

        intro_message = self.get_intro()
        await update.message.reply_text(intro_message) # Enviar intro primero

        summary_result = self.query_llama(prompt_text)

        # Dividir mensajes largos si es necesario
        if len(summary_result) > MAX_MESSAGE_LENGTH:
            for i in range(0, len(summary_result), MAX_MESSAGE_LENGTH):
                await update.message.reply_text(summary_result[i:i + MAX_MESSAGE_LENGTH])
        else:
            await update.message.reply_text(summary_result)

        # Limpiar el buffer para este chat después de generar el resumen
        # self.messages_buffer[chat_id] = [] # Opcional: decidir si limpiar o no

    def run(self) -> None:
        if not self.token:
            logger.critical("No se puede iniciar el bot: BOT_TOKEN no está configurado.")
            return

        app = Application.builder().token(self.token).build()

        # Handlers - se podrían registrar de forma más dinámica más adelante
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("tono", self.cambiar_tono))
        app.add_handler(CommandHandler("resumen", self.resumen))
        app.add_handler(CommandHandler("resumido", self.resumen)) # Alias

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info(f"🔮 El bot {self.current_tone} está despertando...")
        try:
            app.run_polling()
        except Exception as e:
            logger.critical(f"Error fatal al ejecutar el bot: {e}", exc_info=True)

def main() -> None:
    if not BOT_TOKEN:
        logger.error("La variable de entorno BOT_TOKEN no está definida.")
        return
    if not OPENROUTER_API_KEY:
        logger.warning("La variable de entorno OPENROUTER_API_KEY no está definida. La función de resumen no funcionará.")

    bot = HippieSummaryBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    # Esto se eliminará del bot2_core.py y se moverá al bot2.py principal
    pass
