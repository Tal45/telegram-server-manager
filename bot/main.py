import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers.start import start
from handlers.ip import ip
from handlers.health import health
from handlers.unknown import unknown

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ip", ip))
    application.add_handler(CommandHandler("health", health))
    
    # Unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    print("Bacon bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
