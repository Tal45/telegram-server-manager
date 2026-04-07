from telegram import Update
from telegram.ext import ContextTypes
from security.auth import authorized_only
from services.network import get_network_info

@authorized_only
async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return network info."""
    network_info = get_network_info()
    await update.message.reply_text(network_info)
