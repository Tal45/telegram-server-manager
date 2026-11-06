# Bacon Bot Development Guide

Welcome, Gemini. This project is a Telegram bot designed to monitor and manage a OnePlus One server (codename: bacon).

## Architecture Overview

The bot follows a clean, modular structure:

- bot/main.py: Entry point. Registration of handlers and application lifecycle.
- bot/handlers/: Contains command logic (the "Controller" layer).
- bot/services/: Contains system-level logic (the "Model/Service" layer).
- bot/security/: Logic for authorization and access control.
- bot/config.py: Environment-based configuration.

## Security Mandate

All commands that interact with the system MUST be protected by the @authorized_only decorator found in bot/security/auth.py. This ensures only the AUTHORIZED_USER_ID defined in .env can execute commands.

## Adding a New Command/Service

To implement a new feature (e.g., /reboot), follow these steps precisely:

### 1. Create the Service (bot/services/)
Encapsulate the system logic here. Avoid importing Telegram-specific libraries in this layer.
```python
# Example: bot/services/system.py
def reboot_system():
    try:
        subprocess.run(["reboot"], check=True)
        return True
    except Exception as e:
        return str(e)
```

### 2. Create the Handler (bot/handlers/)
Create a new file for the command handler. Use the @authorized_only decorator.
```python
# Example: bot/handlers/reboot.py
from security.auth import authorized_only
from services.system import reboot_system

@authorized_only
async def reboot(update, context):
    await update.message.reply_text("Rebooting...")
    reboot_system()
```

### 3. Register in bot/main.py
1. Import the new handler.
2. Add it to the application via application.add_handler(CommandHandler("cmd", handler)).

### 4. Interactive Commands (Inline Keyboards)
For complex interactions (e.g., Start/Stop buttons), use `InlineKeyboardMarkup` and register a `CallbackQueryHandler` in `main.py`.
- Ensure all callback functions are also decorated with `@authorized_only`.
- Use `query.edit_message_text` to update the status of the same message instead of sending new ones.

### 5. Update Help Documentation
Modify bot/handlers/start.py to reflect the new command in the /start welcome message.

## Conventions
- DRY (Don't Repeat Yourself): If a service needs logic already implemented in another service (e.g., retrieving system IP), refactor the existing service to export a reusable function rather than duplicating logic.
- No Emoji Usage: Do not use emojis in bot messages, logs, or documentation.
- Markdown: Use Markdown for bot replies (e.g., parse_mode="Markdown").
- Error Handling: Services should return error strings or raise exceptions that handlers can gracefully report to the user.
- Logging: Use the standard logging library. main.py is already configured to log to a file.

---
*Happy Hacking, Bacon-Spawn.*
