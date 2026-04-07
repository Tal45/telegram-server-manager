import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN, LOG_FILE
from handlers.start import start
from handlers.ip import ip
from handlers.health import health
from handlers.shutdown import shutdown
from handlers.unknown import unknown

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Set specific levels for noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("telegram.ext").setLevel(logging.WARNING)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).read_timeout(30).connect_timeout(30).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ip", ip))
    application.add_handler(CommandHandler("health", health))
    application.add_handler(CommandHandler("shutdown", shutdown))
    
    # Unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    print("Bacon bot is starting...")
    application.run_polling(bootstrap_retries=-1)

if __name__ == "__main__":
    main()
