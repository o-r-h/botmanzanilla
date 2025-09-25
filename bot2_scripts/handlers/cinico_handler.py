import os
import random
import re
from collections import Counter
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ChatMetrics:
    total_messages: int
    active_users: List[str]
    time_span: str
    dominant_topics: List[str]
    sentiment_score: float
    chaos_level: int
    repetition_rate: float

class CinicoHandler:
    def __init__(self, prompt_template: str, empty_responses: List[str]):
        """
        Inicializa el handler para la personalidad Cínica.

        Args:
            prompt_template (str): La plantilla del prompt a usar.
            empty_responses (List[str]): Lista de respuestas para cuando no hay mensajes.
        """
        if not prompt_template:
            raise ValueError("La plantilla del prompt no puede estar vacía para CinicoHandler.")
        self.prompt_template = prompt_template
        self.empty_responses = empty_responses or ["Supongo que el silencio es oro, o simplemente nadie tiene nada que decir."]

    def get_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """
        Construye el prompt específico para el Cínico usando los mensajes dados.

        Args:
            messages (List[Dict[str, Any]]): Lista de mensajes del chat.

        Returns:
            str: El prompt formateado.
        """
        # Obtener métricas del chat
        metrics = self.get_analizar_metricas(messages)

        joined_messages = "\n".join([f"{m['user']}: {m['text']}" for m in messages])

        return self.prompt_template.format(
            joined=joined_messages,
            total_messages=metrics.total_messages,
            active_users=", ".join(metrics.active_users) if metrics.active_users else "Ninguno destacado",
            time_span=metrics.time_span,
            dominant_topics=", ".join(metrics.dominant_topics) if metrics.dominant_topics else "Ninguno claro",
            chaos_level=metrics.chaos_level,
            sentiment_score=metrics.sentiment_score,
            repetition_rate=metrics.repetition_rate
        )

    def get_analizar_metricas(self, messages: List[Dict[str, Any]]) -> ChatMetrics:
        """
        Extrae métricas del chat para análisis más precisos

        Args:
            messages (List[Dict[str, Any]]): Lista de mensajes del chat.

        Returns:
            ChatMetrics: Un objeto con las métricas del chat.
        """
        # Análisis básico de mensajes
        total_msgs = len(messages)

        # Extraer usuarios del formato de diccionario
        usuarios = [msg['user'] for msg in messages if 'user' in msg]

        users_counter = Counter(usuarios)
        active_users = list(users_counter.keys())[:5]  # Top 5 activos

        # Calcular nivel de caos (basado en interrupciones y cambios de tema)
        chaos_level = min(10, len(set(usuarios)) // 2 + random.randint(1, 3))

        # Detectar temas dominantes (palabras más frecuentes)
        all_text = " ".join([msg.get('text', '') for msg in messages]).lower()
        words = re.findall(r'\b\w+\b', all_text)
        word_freq = Counter(words)
        # Filtrar palabras comunes
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'como', 'pero', 'sus', 'me', 'ha', 'o', 'si', 'porque', 'esta', 'son', 'mi', 'ese', 'ella', 'tan', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'ser', 'tiene', 'yo', 'todo', 'esta', 'era', 'eso'}

        dominant_topics = [word for word, count in word_freq.most_common(5)
                          if word not in stop_words and len(word) > 3]

        # Sentiment score simulado
        negative_words = ['no', 'mal', 'terrible', 'odio', 'horrible', 'peor','chimbo', 'cagada','malo']
        sentiment_score = sum(1 for word in negative_words if word in all_text) / total_msgs if total_msgs > 0 else 0

        return ChatMetrics(
            total_messages=total_msgs,
            active_users=active_users,
            time_span="últimas 2 horas",  # Placeholder
            dominant_topics=dominant_topics,
            sentiment_score=sentiment_score,
            chaos_level=chaos_level,
            repetition_rate=len(usuarios) / total_msgs if total_msgs > 0 else 0
        )

    def get_empty_response(self) -> str:
        """
        Devuelve una respuesta aleatoria para cuando no hay mensajes.

        Returns:
            str: Una respuesta de la lista de respuestas vacías.
        """
        return random.choice(self.empty_responses)

    def get_intro(self) -> str:
        """
        Devuelve una introducción aleatoria para el resumen del Cínico.

        Returns:
            str: Una frase de introducción.
        """
        intros = [
            "😒 Como si alguien realmente se interesara, pero aquí está el resumen:",
            "🤦‍♂️ *suspira* ¿En serio quieres que pierda mi tiempo con esto? Bueno, ahí va:",
            "🧐 Analicemos juntos por qué esto probablemente es una pérdida de tiempo:",
            "🙄 Oh, vaya, más palabras. Aquí tienes tu dosis de 'sabiduría' grupal:"
        ]
        return random.choice(intros)

# Las variables globales de prompts y empty_responses ya no son necesarias aquí.
# Se cargarán en bot2_core y se pasarán al constructor del Handler.

# Ejemplo de cómo se obtendrían estas variables en bot2_core.py:
# PROMPT_CINICO_ENV = os.getenv("PROMPT_CINICO", "Default Cinico Prompt")
# EMPTY_CINICO_ENV = [
#     "La soledad no es mala… hasta que te das cuenta de que tu mejor conversación es con Siri.",
#     "Al fin dejaron de escribir, no vuelvan",
#     "La esperanza es lo último que se pierde… espero que no escriban mas"
# ]
# cinico_handler_instance = CinicoHandler(PROMPT_CINICO_ENV, EMPTY_CINICO_ENV)
