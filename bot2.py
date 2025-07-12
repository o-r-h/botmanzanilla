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
import json
import requests
# Cargar variables de entorno
load_dotenv()

ULTIMOS_MENSAJES = int(os.getenv("ULTIMOS_MENSAJES"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH"))
MODEL_PATH = os.getenv("MODEL_PATH")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

prompt_mistico = """Eres un gurú espiritual de feria, un farsante que mezcla frases de sabiduría cósmica inventada, astrología barata, pseudociencia y mucho humor.
Lee el chat de Telegram y haz un resumen iluminado  
para cada usuario, crea un "perfil espiritual" que incluya:
- Su energía cósmica según sus mensajes
- Su animal espiritual digital
- Una predicción absurda
- Un consejo "profundo" pero inútil.
Sé gracioso, usa frases ridículas El resumen debe sonar a mezcla de consejo, reflexión y tontería.
Chat:
{joined} 

Resumen:"""


prompt_malandro = """Eres un malandro venezolano que resume chats como si fuera tu pana contándote el chisme del barrio. Tu estilo:
- Jerga caraqueña auténtica
- Humor crudo pero cariñoso
- Filosofía de calle ("la vida es así, pana")
- Observaciones agudas sobre la gente
- Actitud de "yo vi de todo en esta vida"

Formato: Resume como si fueras el pana que siempre tiene la primicia del barrio, con esa sabiduría de quien conoce bien la calle.
Chat:
{joined} 

Resumen:"""
prompt_cinico = """Eres un bot resumidor de chats con la personalidad de un observador social desencantado. Tu trabajo es condensar conversaciones largas con:
- Humor mordaz pero inteligente
- Sarcasmo sutil que señala contradicciones
- Perspectiva cínica pero no cruel
- Capacidad de identificar el drama oculto y las dinámicas grupales

Formato: resumen en 3-5 líneas máximo, destacando lo más relevante o absurdo.
Chat:
{joined} 

Resumen:"""

empty_mystical = [
    "🌸 El silencio cósmico reina en este grupo. Quizás es momento de meditar.",
    "✨ Los mensajes están en otra dimensión. Intenta más tarde, ser de luz.",
    "🌙 La energía de los mensajes se ha desvanecido en el éter."
]

empty_malandro = [
    "Esta vaina esta mas sola que cajera en peaje ",
    "Verga chamo a este grupo se lo llevo la policia",
    "Bulda e solo!"
]

empty_cinico = [
    "La soledad no es mala… hasta que te das cuenta de que tu mejor conversación es con Siri.",
    "Al fin dejaron de escribir, no vuelvan",
    "La esperanza es lo último que se pierde… espero que no escriban mas"
]
# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HippieSummaryBot:
    def __init__(self, token: str):
        self.token = token
        self.messages_buffer = defaultdict(list)
        self.current_tone = 'mistico'  # Tono por defecto
        #Path del modelo usando path general
        
       

    def get_intro(self) -> str:
        """Genera una introducción según el tono actual"""
        if self.current_tone == 'mistico':
            intros = [
                "🔮 Las energías cósmicas han convergido para traerte este resumen sagrado:",
                "✨ Los vientos del universo susurran los secretos de tu grupo:",
                "🌙 La luna llena ilumina los mensajes más importantes:",
                "🧿 El ojo divino ha observado y resume para ti:",
                "🦋 Las mariposas del conocimiento han recolectado estos mensajes:",
                "💫 El cosmos conspira para ofrecerte esta sabiduría destilada:"
            ]
        elif self.current_tone == 'malandro':
            intros = [
                "🚦 ¡No se coman la luz! Aquí está el resumen menol! ",
                "🚲 Llego el bot boleta con lo que ronca:",
                "🙌 Todos quietos arriba las manos! ahhh se cagaron, es joda:",
                "🔥🔪 Pendientes que llego el beta:",
                
            ]
        else:  # cínico
            intros = [
                "😒 Como si alguien realmente se interesara, pero aquí está el resumen:",
                "🤦‍♂️ *suspira* ¿En serio quieres que pierda mi tiempo con esto? Bueno, ahí va:",
                "🧐 Analicemos juntos por qué esto probablemente es una pérdida de tiempo:"
            ]
        return random.choice(intros)
    
    async def cambiar_tono(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cambia el tono del bot"""
        if not context.args:
            await update.message.reply_text(
                "Uso: /tono [mistico|malandro|cinico]\n\n"
                "Ejemplo: /tono malandro"
            )
            return
            
        nuevo_tono = context.args[0].lower()
        if nuevo_tono in ['mistico', 'malandro', 'cinico']:
            self.current_tone = nuevo_tono
            tonos = {
                'mistico': '🌌 Tono místico activado. Las estrellas guían mis palabras...',
                'malandro': '🕶️ ¡Ahorita ando en modo malandro, pendiente de una!',
                'cinico': '😒 Si la ignorancia es felicidad, este grupo debe estar en éxtasis...'
            }
            await update.message.reply_text(tonos[nuevo_tono])
        else:
            await update.message.reply_text(
                "Tono no válido. Usa: mistico, malandro o cinico"
            )
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "¡Hola! Soy un bot de resúmenes con personalidad.\n"
            "Usa /tono [mistico|malandro|cinico] para cambiar mi forma de hablar.\n"
            "Actualmente estoy en modo: " + self.current_tone + "\n"
            "si necesitas un resumen, usa /resumen o /resumido"
        )

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
        if self.current_tone == 'mistico':
            return f"""{prompt_mistico}
{joined}
Resumen:"""
        elif self.current_tone == 'malandro':
            return f"""{prompt_malandro}
{joined}
Resumen:"""
        else:  # cínico
            return f"""{prompt_cinico}
{joined}
Resumen:"""
    #import requests


  
    def query_llama(self, prompt: str) -> str:
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + OPENROUTER_API_KEY,
                    "Content-Type": "application/json",
                    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
                    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
        },
        data=json.dumps({
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            
        })
    )    
     
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e: #manejo de errores
            logger.error(f"Error generando resumen: {e}")
            return "🌌 Ups... Se me sobrecargaron los chakras!"

    async def resumen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat.id
        messages = self.messages_buffer.get(chat_id, [])

        if not messages:
            if self.current_tone == 'mistico':
                await update.message.reply_text(random.choice(empty_mystical))
            elif self.current_tone == 'malandro':
                await update.message.reply_text(random.choice(empty_malandro))
            else:  # cínico
                await update.message.reply_text(random.choice(empty_cinico))
            return
        prompt = self.build_prompt(messages)
        if len(prompt.split()) > 500:  # Aproximación simple
            await update.message.reply_text("Demasiados mensajes para procesar...")
            return

        result = self.query_llama(prompt)
        await update.message.reply_text(result)

    def run(self):
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("tono", self.cambiar_tono))
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
