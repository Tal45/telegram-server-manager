from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from security.auth import authorized_only
from services.nginx import get_nginx_status, start_nginx, stop_nginx, get_local_ip

def get_nginx_keyboard():
    """Generates the inline keyboard for nginx control."""
    status = get_nginx_status()
    
    keyboard = [
        [
            InlineKeyboardButton("Start", callback_data="nginx_start"),
            InlineKeyboardButton("Stop", callback_data="nginx_stop"),
        ],
        [
            InlineKeyboardButton("Refresh Status", callback_data="nginx_refresh"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard), status

@authorized_only
async def nginx_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry command for nginx control."""
    reply_markup, status = get_nginx_keyboard()
    await update.message.reply_text(
        f"Bacon Bot Nginx Management:\nStatus: {status.upper()}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

@authorized_only
async def nginx_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles nginx control button presses."""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    
    if action == "nginx_start":
        result = start_nginx()
        if result is True:
            ip = get_local_ip()
            message = f"Bacon Bot: Nginx started successfully.\nAddress: http://{ip}:80"
        else:
            message = f"Bacon Bot: Error starting nginx: {result}"
    
    elif action == "nginx_stop":
        result = stop_nginx()
        if result is True:
            message = "Bacon Bot: Nginx stopped successfully."
        else:
            message = f"Bacon Bot: Error stopping nginx: {result}"
            
    elif action == "nginx_refresh":
        # Just update the status below
        pass

    reply_markup, status = get_nginx_keyboard()
    # If it's a refresh or after an action, update the status message
    if action == "nginx_refresh":
        await query.edit_message_text(
            f"Bacon Bot Nginx Management:\nStatus: {status.upper()}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # For start/stop actions, show result and allow returning to management or just keeping the new state
        await query.edit_message_text(
            f"{message}\n\nStatus: {status.upper()}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
