from telegram import Update
from telegram.ext import ContextTypes
from security.auth import authorized_only

@authorized_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm bot is alive."""
    await update.message.reply_text("Bot is alive and ready to serve bacon!")
