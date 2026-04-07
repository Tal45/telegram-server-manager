from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from security.auth import authorized_only
from services.system import shutdown_system

@authorized_only
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt the user for shutdown confirmation."""
    keyboard = [
        [
            InlineKeyboardButton("Shutdown", callback_data="shutdown_confirm"),
            InlineKeyboardButton("Abort", callback_data="shutdown_abort"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bacon Bot: Are you sure?", reply_markup=reply_markup, parse_mode="Markdown")

@authorized_only
async def shutdown_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the shutdown confirmation callback."""
    query = update.callback_query
    await query.answer()

    if query.data == "shutdown_confirm":
        await query.edit_message_text("Bacon Bot: Shutting down system now...", parse_mode="Markdown")
        
        # Perform shutdown
        result = shutdown_system()
        
        if result is not True:
            await query.edit_message_text(f"Bacon Bot Error: {result}", parse_mode="Markdown")
    elif query.data == "shutdown_abort":
        await query.edit_message_text("Bacon Bot: Shutdown aborted.", parse_mode="Markdown")
