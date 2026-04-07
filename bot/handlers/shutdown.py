from telegram import Update
from telegram.ext import ContextTypes
from security.auth import authorized_only
from services.system import shutdown_system

@authorized_only
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiate a poweroff of the system."""
    await update.message.reply_text("Bacon Bot: Shutting down system now...", parse_mode="Markdown")
    
    # Perform shutdown
    result = shutdown_system()
    
    if result is not True:
        await update.message.reply_text(f"Bacon Bot Error: {result}", parse_mode="Markdown")
