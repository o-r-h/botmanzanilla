from bot2_scripts.bot2_core import main, HippieSummaryBot, BOT_TOKEN, OPENROUTER_API_KEY, logger

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("La variable de entorno BOT_TOKEN no está definida en su archivo .env o en el entorno.")
    elif not OPENROUTER_API_KEY:
        logger.warning("La variable de entorno OPENROUTER_API_KEY no está definida. La función de resumen no funcionará correctamente.")
    else:
        logger.info("Iniciando el bot desde bot2.py")
    
    # Llama a la función main de bot2_core.py si existe,
    # o directamente instancia y corre el bot.
    # Esto asume que bot2_core.main() maneja la creación de la instancia del bot y su ejecución.
    # Si main() no está diseñado para eso, ajusta según sea necesario.
    # Por ejemplo, podrías hacer:
    # bot = HippieSummaryBot(BOT_TOKEN)
    # bot.run()
    # En este caso, main() ya existe en bot2_core.py y hace eso.
    
    main()
