import os
import random
from typing import List, Dict, Any

class MisticoHandler:
    def __init__(self, prompt_template: str, empty_responses: List[str]):
        """
        Inicializa el handler para la personalidad Mística.

        Args:
            prompt_template (str): La plantilla del prompt a usar.
            empty_responses (List[str]): Lista de respuestas para cuando no hay mensajes.
        """
        if not prompt_template:
            raise ValueError("La plantilla del prompt no puede estar vacía para MisticoHandler.")
        self.prompt_template = prompt_template
        self.empty_responses = empty_responses or ["El cosmos está en silencio. Medita."]

    def get_prompt(self, messages: List[Dict[str, Any]]) -> str:
        """
        Construye el prompt específico para el Místico usando los mensajes dados.

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
        Devuelve una introducción aleatoria para el resumen del Místico.

        Returns:
            str: Una frase de introducción.
        """
        intros = [
            "🔮 Las energías cósmicas han convergido para traerte este resumen sagrado:",
            "✨ Los vientos del universo susurran los secretos de tu grupo:",
            "🌙 La luna llena ilumina los mensajes más importantes:",
            "🧿 El ojo divino ha observado y resume para ti:",
            "🦋 Las mariposas del conocimiento han recolectado estos mensajes:",
            "💫 El cosmos conspira para ofrecerte esta sabiduría destilada:"
        ]
        return random.choice(intros)

# Las variables globales de prompts y empty_responses ya no son necesarias aquí.
# Se cargarán en bot2_core y se pasarán al constructor del Handler.

# Ejemplo de cómo se obtendrían estas variables en bot2_core.py:
# PROMPT_MISTICO_ENV = os.getenv("PROMPT_MISTICO", "Default Mistico Prompt")
# EMPTY_MISTICO_ENV = [
#     "🌸 El silencio cósmico reina en este grupo. Quizás es momento de meditar.",
#     "✨ Los mensajes están en otra dimensión. Intenta más tarde, ser de luz.",
#     "🌙 La energía de los mensajes se ha desvanecido en el éter."
# ]
# mistico_handler_instance = MisticoHandler(PROMPT_MISTICO_ENV, EMPTY_MISTICO_ENV)
