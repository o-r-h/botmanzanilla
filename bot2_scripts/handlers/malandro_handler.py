import os
import random
from typing import List, Dict, Any

class MalandroHandler:
    def __init__(self, prompt_template: str, empty_responses: List[str]):
        """
        Inicializa el handler para la personalidad Malandro.

        Args:
            prompt_template (str): La plantilla del prompt a usar.
            empty_responses (List[str]): Lista de respuestas para cuando no hay mensajes.
        """
        if not prompt_template:
            raise ValueError("La plantilla del prompt no puede estar vacía para MalandroHandler.")
        self.prompt_template = prompt_template
        self.empty_responses = empty_responses or ["No hay chisme nuevo, menor."]

    def get_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """
        Construye el prompt específico para el Malandro usando los mensajes dados.

        Args:
            messages (List[Dict[str, Any]]): Lista de mensajes del chat.
                                             Cada mensaje es un dict con 'user' y 'text'.

        Returns:
            str: El prompt formateado.
        """
        joined_messages = "\n".join([f"{m['user']}: {m['text']}" for m in messages])
        return self.prompt_template.format(joined=joined_messages)

    def get_empty_response(self) -> str:
        """
        Devuelve una respuesta aleatoria para cuando no hay mensajes.

        Returns:
            str: Una respuesta de la lista de respuestas vacías.
        """
        return random.choice(self.empty_responses)

    def get_intro(self) -> str:
        """
        Devuelve una introducción aleatoria para el resumen del Malandro.

        Returns:
            str: Una frase de introducción.
        """
        intros = [
            "🚦 ¡No se coman la luz! Aquí está el resumen menol! ",
            "🚲 Llego el bot boleta con lo que ronca:",
            "🙌 Todos quietos arriba las manos! ahhh se cagaron, es joda:",
            "🔥🔪 Pendientes que llego el beta:",
        ]
        return random.choice(intros)

# Las variables globales de prompts y empty_responses ya no son necesarias aquí
# Se cargarán en bot2_core y se pasarán al constructor del Handler.

# Ejemplo de cómo se obtendrían estas variables en bot2_core.py:
# PROMPT_MALANDRO_ENV = os.getenv("PROMPT_MALANDRO", "Default Malandro Prompt")
# EMPTY_MALANDRO_ENV = [
#     "Esta vaina esta mas sola que cajera en peaje ",
#     "Verga chamo a este grupo se lo llevo la policia",
#     "Bulda e solo!"
# ]
# malandro_handler_instance = MalandroHandler(PROMPT_MALANDRO_ENV, EMPTY_MALANDRO_ENV)
