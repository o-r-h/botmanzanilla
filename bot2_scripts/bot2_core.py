import logging
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import List, Dict, Any
import os
import json
import requests
from dotenv import load_dotenv
from dataclasses import dataclass

# Cargar variables de entorno
load_dotenv()

# Estas se moverán a variables de entorno más adelante según el plan
ULTIMOS_MENSAJES =30 # int(os.getenv("ULTIMOS_MENSAJES", 30))
MAX_MESSAGE_LENGTH = 3000 # int(os.getenv("MAX_MESSAGE_LENGTH", 500))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Importar la clase Handler para la personalidad Cínica
from .handlers.cinico_handler import CinicoHandler

# Lista de mensajes vacíos para la personalidad Cínica
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


@dataclass
class ChatMetrics:
    """Métricas del chat para análisis más precisos"""
    total_messages: int
    active_users: List[str]
    time_span: str
    dominant_topics: List[str]
    sentiment_score: float
    chaos_level: int  # 1-10
    repetition_rate: float

class CinicoSummaryBot:
    def __init__(self, token: str):
        if not token:
            logger.error("El token del bot no está configurado. Asegúrate de que BOT_TOKEN está en tu .env o variables de entorno.")
            raise ValueError("Token del bot no proporcionado.")
        self.token = token
        self.messages_buffer = defaultdict(list)

        # Cargar prompt para la personalidad Cínica
        prompt_cinico_template = """Eres un analista conversacional con la mordacidad de Oscar Wilde, la frialdad de Sherlock Holmes y el humor negro de un patólogo forense.

**PERSONALIDAD:**
- Sarcasmo refinado y letal
- Humor negro intelectual
- Analogías incómodamente precisas
- Observaciones sociológicas despiadadas
- Falso optimismo condescendiente

**ESTILO DE ANÁLISIS:**
- Identifica patrones de comportamiento grupal
- Señala contradicciones e hipocresías
- Usa metáforas relacionadas con: medicina forense, teatro absurdo, zoología, psicología clínica
- Estructura: Diagnóstico → Síntomas → Pronóstico (sarcastico, sombrío)

**MÉTRICAS DEL CHAT:**
- Total de mensajes: {total_messages}
- Usuarios activos principales: {active_users}
- Período de tiempo: {time_span}
- Temas dominantes: {dominant_topics}
- Nivel de caos: {chaos_level}/10
- Tasa de negatividad: {sentiment_score:.2f}
- Tasa de repetición: {repetition_rate:.2f}

**FORMATO DE RESUMEN:**
1. **Resumen General:** [Una línea devastadora sobre el estado del chat]
2. **Observaciones:** [3-5 comportamientos específicos de usuarios con analogías crueles]

**CHAT A ANALIZAR:**
{joined}
Resumen:"""

        # Validar que el prompt se haya cargado
        if not prompt_cinico_template:
            logger.warning("Prompt cínico no encontrado. Usando valor por defecto.")
            prompt_cinico_template = "Eres un cínico por defecto."

        # Instanciar handler cínico
        self.handler = CinicoHandler(prompt_cinico_template, EMPTY_CINICO_RESPONSES)

    def get_intro(self) -> str:
        """Obtiene una introducción del handler."""
        return self.handler.get_intro()


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "¡Hola! Soy un bot de resúmenes con personalidad cínica.\n"
            "Si necesitas un resumen, usa /resumen o /resumido"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Debug: Log all incoming updates
        logger.info(f"🔍 Update recibido: {update}")
        print(f"🔍 Update recibido - Tipo: {type(update)}")

        if update.message:
            print(f"📨 Mensaje detectado - Tipo de chat: {update.message.chat.type}")
            logger.info(f"Mensaje detectado - Tipo de chat: {update.message.chat.type}")

        if update.message and update.message.chat.type in ['group', 'supergroup'] and update.message.text:
            chat_id = update.message.chat.id
            user = update.message.from_user.first_name if update.message.from_user else "UsuarioDesconocido"
            print(f"📨 Mensaje recibido de {user} en chat {chat_id}")
            logger.info(f"Mensaje recibido en chat {chat_id} de {user}: {update.message.text[:50]}...")
            self.messages_buffer[chat_id].append({
                'user': user,
                'text': update.message.text[:MAX_MESSAGE_LENGTH],
                'timestamp': datetime.now()
            })
        elif update.message and update.message.chat.type == 'private':
            print(f"💬 Mensaje privado recibido")
            logger.info("Mensaje privado recibido")
        else:
            print(f"❌ Mensaje no procesado - Tipo: {update.message.chat.type if update.message else 'None'}")
            logger.info(f"Mensaje no procesado - Tipo: {update.message.chat.type if update.message else 'None'}")

            # Limitar a los últimos ULTIMOS_MENSAJES mensajes
            if len(self.messages_buffer[chat_id]) > ULTIMOS_MENSAJES:
                self.messages_buffer[chat_id] = self.messages_buffer[chat_id][-ULTIMOS_MENSAJES:]

            # Filtrar mensajes por hora (ej. última hora)
            # now = datetime.now()
            # self.messages_buffer[chat_id] = [
            #     msg for msg in self.messages_buffer[chat_id]
            #     if (now - msg['timestamp']) < timedelta(hours=1)
            # ]

    def build_prompt(self, messages: List[Dict[str, Any]]) -> str:
        # Delegar la construcción del prompt al handler
        return self.handler.get_prompt(messages)

    def query_llama(self, prompt: str) -> str:
        if not OPENROUTER_API_KEY:
            logger.error("OPENROUTER_API_KEY no está configurado.")
            return "Error: La API key para el servicio de resumen no está configurada."
        try:
            headers = {
                "Authorization": "Bearer " + OPENROUTER_API_KEY,
                "Content-Type": "application/json",
                # "HTTP-Referer": "<YOUR_SITE_URL>", # Opcional
                # "X-Title": "<YOUR_SITE_NAME>", # Opcional
            }
            logger.info(f"API Key: {OPENROUTER_API_KEY}")
            logger.info(f"Headers: {headers}")
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps({
                    "model": "deepseek/deepseek-chat-v3.1:free", # Modelo de ejemplo
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            response.raise_for_status() # Lanza un error para respuestas 4xx/5xx
            result = response.json()

            if result.get('choices') and result['choices'][0].get('message') and result['choices'][0]['message'].get('content'):
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"Respuesta inesperada de la API: {result}")
                return "Hubo un error inesperado y no pude procesar el resumen."

        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red o HTTP generando resumen: {e}")
            return "Error de conexión. Intenta más tarde."
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return "Error al generar el resumen. Intenta más tarde."

    async def resumen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat.id
        messages = self.messages_buffer.get(chat_id, [])

        if not messages:
            # Obtener respuesta vacía del handler
            empty_response = self.handler.get_empty_response()
            await update.message.reply_text(empty_response)
            return

        prompt_text = self.build_prompt(messages)

        # Podríamos añadir una validación más robusta para la longitud del prompt
        if len(prompt_text) > 4000: # Límite arbitrario, ajustar según el modelo
            logger.warning(f"El prompt para el chat {chat_id} es muy largo.")
            await update.message.reply_text("Demasiados mensajes para procesar en este momento... Intenta con menos mensajes.")
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

    def _get_bot_username_sync(self) -> str:
        """Obtiene el nombre de usuario del bot de forma síncrona"""
        import requests
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{self.token}/getMe",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and 'username' in data.get('result', {}):
                    return data['result']['username']
        except Exception as e:
            logger.error(f"Error al obtener el username del bot: {e}")
        return None

    def _setup_handlers(self):
        """Configura los manejadores de comandos"""
        # Obtener el nombre de usuario del bot
        self._bot_username = self._get_bot_username_sync()
        
        # Función para obtener variantes de comandos
        def get_variants(cmd):
            variants = [cmd]
            if self._bot_username:
                variants.append(f"{cmd}@{self._bot_username}")
            return variants

        # Configurar los manejadores
        for cmd, handler in [
            ("start", self.start),
            ("resumen", self.resumen),
            ("resumido", self.resumen)  # Alias
        ]:
            self.app.add_handler(CommandHandler(cmd, handler))
        
        # Manejador de mensajes regulares
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))

    def run(self) -> None:
        if not self.token:
            print("❌ ERROR: No se puede iniciar el bot: BOT_TOKEN no está configurado.")
            logger.critical("No se puede iniciar el bot: BOT_TOKEN no está configurado.")
            return

        print("🔧 Configurando aplicación de Telegram...")
        # Crear la aplicación
        self.app = Application.builder().token(self.token).build()
        print("✅ Aplicación creada")

        # Configurar los manejadores
        print("🔧 Configurando manejadores...")
        self._setup_handlers()
        print("✅ Manejadores configurados")

        print("🔮 El bot cínico está despertando...")
        logger.info("🔮 El bot cínico está despertando...")

        # Configurar el event loop
        import asyncio
        import platform

        if platform.system() == 'Windows':
            print("🔧 Configurando event loop para Windows...")
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        try:
            print("🔄 Iniciando polling de Telegram...")
            # Crear un nuevo event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            print("✅ Bot iniciado correctamente. Esperando mensajes...")
            # Iniciar el bot
            self.app.run_polling()

        except Exception as e:
            print(f"❌ Error fatal al ejecutar el bot: {e}")
            logger.critical(f"Error fatal al ejecutar el bot: {e}", exc_info=True)
            raise

def main() -> None:
    print("🚀 Iniciando bot...")
    logger.info("🚀 Iniciando bot...")

    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN no está definido")
        logger.error("La variable de entorno BOT_TOKEN no está definida.")
        return
    if not OPENROUTER_API_KEY:
        print("⚠️ WARNING: OPENROUTER_API_KEY no está definido")
        logger.warning("La variable de entorno OPENROUTER_API_KEY no está definida. La función de resumen no funcionará.")

    print("✅ Variables de entorno verificadas")
    print(f"🔑 BOT_TOKEN: {'***' + BOT_TOKEN[-10:] if BOT_TOKEN else 'None'}")
    print(f"🔑 OPENROUTER_API_KEY: {'***' + OPENROUTER_API_KEY[-10:] if OPENROUTER_API_KEY else 'None'}")

    try:
        print("🤖 Creando instancia del bot...")
        bot = CinicoSummaryBot(BOT_TOKEN)
        print("✅ Bot creado exitosamente")
        print("🔄 Iniciando polling...")
        bot.run()
    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")
        logger.error(f"Error al iniciar el bot: {e}")
        raise

if __name__ == "__main__":
    # Esto se eliminará del bot2_core.py y se moverá al bot2.py principal
    pass
