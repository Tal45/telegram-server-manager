from telegram import Update
from telegram.ext import ContextTypes
from security.auth import authorized_only

@authorized_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm bot is alive and list commands."""
    welcome_msg = (
        "*Bacon Bot Status: Online*\n\n"
        "Available commands:\n"
        "/start - Show this help message\n"
        "/ip - Show network information (Hostname, SSID, IP)\n"
        "/health - Show device health (Battery status, Capacity)\n"
        "/nginx - Manage nginx service (Start/Stop/Status)\n"
        "/shutdown - Power off the system"
    )
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")
