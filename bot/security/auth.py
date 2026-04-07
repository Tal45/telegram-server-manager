from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import AUTHORIZED_USER_ID

def authorized_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != AUTHORIZED_USER_ID:
            print(f"Unauthorized access attempt by ID: {user_id}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped
