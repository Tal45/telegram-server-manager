import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import AUTHORIZED_USER_ID

logger = logging.getLogger(__name__)

def authorized_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != AUTHORIZED_USER_ID:
            logger.warning(f"Unauthorized access attempt by ID: {user_id}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped
