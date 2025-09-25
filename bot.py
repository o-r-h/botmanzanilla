from bot2_scripts.bot2_core import main, CinicoSummaryBot, BOT_TOKEN, OPENROUTER_API_KEY, logger

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("La variable de entorno BOT_TOKEN no está definida en su archivo .env o en el entorno.")
    elif not OPENROUTER_API_KEY:
        logger.warning("La variable de entorno OPENROUTER_API_KEY no está definida. La función de resumen no funcionará correctamente.")
    else:
        logger.info("Iniciando el bot desde bot2.py")

    main()
