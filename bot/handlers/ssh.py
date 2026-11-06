import logging
from telegram import Update
from telegram.ext import ContextTypes
from security.auth import authorized_only
from services.ssh import add_authorized_key

logger = logging.getLogger(__name__)

@authorized_only
async def addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Accepts an SSH public key and appends it to authorized_keys.
    Supports:
    1. /addkey <public_key_string>
    2. Replying to a message containing a public key with /addkey
    3. Document attachments (.pub file) with caption /addkey
    """
    raw_key = None

    # Check command arguments
    if context.args:
        raw_key = " ".join(context.args).strip()

    # Check if this command was a reply to another message containing text
    elif update.message.reply_to_message:
        if update.message.reply_to_message.text:
            raw_key = update.message.reply_to_message.text.strip()
        elif update.message.reply_to_message.caption:
            raw_key = update.message.reply_to_message.caption.strip()

    # Check if a document (.pub file) is attached directly with caption /addkey
    elif update.message.document:
        try:
            doc_file = await update.message.document.get_file()
            content = await doc_file.download_as_bytearray()
            raw_key = content.decode("utf-8", errors="ignore").strip()
        except Exception as e:
            logger.error(f"Error reading attached key document: {e}")
            await update.message.reply_text(
                f"Bacon Bot: Error downloading document: {str(e)}",
                parse_mode="Markdown"
            )
            return

    # If no key was detected, display usage information
    if not raw_key:
        usage_msg = (
            "*Bacon Bot SSH Key Management*\n\n"
            "Usage:\n"
            "`/addkey <ssh-public-key>`\n\n"
            "Options:\n"
            "- Pass key directly: `/addkey ssh-ed25519 AAAAC3... user@host`\n"
            "- Reply to any message containing your public key with `/addkey`\n"
            "- Attach a `.pub` file with caption `/addkey`"
        )
        await update.message.reply_text(usage_msg, parse_mode="Markdown")
        return

    # Add the key
    success, message = add_authorized_key(raw_key)

    prefix = "Bacon Bot: " if success else "Bacon Bot Error: "
    try:
        await update.message.reply_text(f"{prefix}{message}", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(f"{prefix}{message}")

