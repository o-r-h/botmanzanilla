# Bot2 - Summary Bot 

Este es un bot de Telegram que genera resúmenes de chats con diferentes personalidades (Cínico). Esta versión ha sido refactorizada para una mejor estructura y mantenibilidad.

## Características

-   Resume conversaciones de grupos de Telegram.
-   **Cínico**: Resúmenes con humor mordaz y sarcasmo sutil.
-   Comandos para interactuar con el bot:
    -   `/start`: Muestra un mensaje de bienvenida.
    -   `/resumen` o `/resumido`: Solicita un resumen del chat.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```
.
├── bot2.py                     # Punto de entrada principal para ejecutar el bot
├── bot2_scripts/               # Lógica principal del bot
│   ├── __init__.py
│   ├── bot2_core.py            # Clase principal del bot y manejo de Telegram
│   ├── handlers/               # Clases handler para cada personalidad
│   │   ├── __init__.py
│   │   ├── cinico_handler.py
│   └── utils/                  # Utilidades (actualmente vacío)
│       └── __init__.py
├── .env.example                # Ejemplo de archivo de configuración de entorno
├── .env                        # Archivo de configuración de entorno 
├── requirements.txt            # Dependencias de Python
└── README.md                   # Este archivo
```

## Configuración

1.  **Clonar el repositorio (si aplica).**

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar variables de entorno:**
    Crea un archivo llamado `.env` en la raíz del proyecto, copiando el formato de `.env.example`. Edita `.env` con tus propios valores:

    ```dotenv
    # Token para el bot de Telegram
    BOT_TOKEN="TU_BOT_TOKEN_AQUI"

    # API Key para OpenRouter AI (o el servicio LLM que uses)
    OPENROUTER_API_KEY="TU_OPENROUTER_API_KEY_AQUI"

    # Configuración del buffer de mensajes
    ULTIMOS_MENSAJES=20
    MAX_MESSAGE_LENGTH=4000 # Longitud máxima de un mensaje enviado por el bot

    # Environtment variables
    ```
    -   `BOT_TOKEN`: Tu token de bot de Telegram obtenido de BotFather.
    -   `OPENROUTER_API_KEY`: Tu API key para el servicio OpenRouter.ai (usado para la generación de resúmenes con LLM).
    -   `ULTIMOS_MENSAJES`: Número de mensajes recientes a considerar para el resumen.
    -   `MAX_MESSAGE_LENGTH`: Longitud máxima de los mensajes que enviará el bot (para evitar límites de Telegram).
    

## Ejecución

Para iniciar el bot, ejecuta:

```bash
python bot.py
```

## Dependencias Requeridas

Las principales dependencias se encuentran en `requirements.txt`:

-   `python-telegram-bot`: Para la interacción con la API de Telegram.
-   `python-dotenv`: Para cargar variables de entorno desde el archivo `.env`.
-   `requests`: Para realizar peticiones HTTP a la API de OpenRouter.

(Otras dependencias como `ctransformers` y `torch` estaban en el `bot.py` original, pero no se usan activamente en esta versión si solo se utiliza OpenRouter. Se mantienen por retrocompatibilidad o posible uso futuro.)

## Modificaciones Realizadas (Resumen de la Refactorización)

-   **Estructura Modular:** El código se dividió en módulos: `bot2_core.py` para la lógica principal, y `handlers` para cada personalidad.
-   **Gestión de Variables de Entorno:** Todos los tokens, API keys y prompts se gestionan a través de un archivo `.env` usando `python-dotenv`. Se proporciona un `.env.example`.
-   **Type Hinting:** Se añadieron y mejoraron los type hints en todo el código.
-   **Logging Mejorado:** Se utiliza el módulo `logging` para un mejor seguimiento y depuración.
-   **Separación de Configuración:** La configuración (tokens, prompts) está separada de la lógica de negocio.
-   **Buenas Prácticas:** Se ha intentado seguir PEP 8, incluir docstrings y mejorar el manejo de errores.
```


