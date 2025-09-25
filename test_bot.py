#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración del bot
"""
import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_bot_token():
    """Prueba si el token del bot es válido"""
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("❌ ERROR: BOT_TOKEN no está definido en el archivo .env")
        return False

    print(f"🔑 Probando token: ***{token[-10:]}")

    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print("✅ Token válido!")
                print(f"🤖 Nombre del bot: {bot_info.get('first_name')}")
                print(f"👤 Username: @{bot_info.get('username')}")
                print(f"🆔 ID del bot: {bot_info.get('id')}")
                return True
            else:
                print(f"❌ Respuesta de Telegram: {data}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_openrouter_key():
    """Prueba si la API key de OpenRouter es válida"""
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("⚠️ WARNING: OPENROUTER_API_KEY no está definido")
        return False

    print(f"🔑 Probando OpenRouter API key: ***{api_key[-10:]}")

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ OpenRouter API key válido!")
            return True
        else:
            print(f"❌ OpenRouter API key inválido - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al verificar OpenRouter: {e}")
        return False

def main():
    print("🧪 Probando configuración del bot...\n")

    print("=" * 50)
    print("1. Verificando BOT_TOKEN...")
    print("=" * 50)
    bot_ok = test_bot_token()

    print("\n" + "=" * 50)
    print("2. Verificando OPENROUTER_API_KEY...")
    print("=" * 50)
    api_ok = test_openrouter_key()

    print("\n" + "=" * 50)
    print("RESULTADO FINAL")
    print("=" * 50)

    if bot_ok and api_ok:
        print("✅ ¡Todo está configurado correctamente!")
        print("🚀 Puedes ejecutar el bot con: python bot2.py")
    elif bot_ok:
        print("⚠️ El bot está configurado, pero OpenRouter no funcionará")
        print("🚀 Puedes ejecutar el bot, pero los resúmenes no funcionarán")
    else:
        print("❌ Hay problemas con la configuración")
        print("🔧 Revisa tu archivo .env")

if __name__ == "__main__":
    main()