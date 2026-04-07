from telegram import Update
from telegram.ext import ContextTypes
from security.auth import authorized_only
from services.battery import get_battery_info

@authorized_only
async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns device data such as battery capacity and status."""
    battery_info = get_battery_info()
    await update.message.reply_text(battery_info)
