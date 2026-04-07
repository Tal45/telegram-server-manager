from telegram import Update
from telegram.ext import ContextTypes
from security.auth import authorized_only

@authorized_only
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await update.message.reply_text("Unknown command. Try /ip.")
