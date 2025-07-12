import os
import random
from typing import List, Dict, Any

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
