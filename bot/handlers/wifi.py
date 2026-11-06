import shlex
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from security.auth import authorized_only
from services.network import (
    scan_wifi,
    get_saved_wifi_connections,
    connect_wifi,
    get_current_connection,
    get_ip_address,
)

logger = logging.getLogger(__name__)


async def _safe_reply(message, text: str, reply_markup=None):
    """Replies with Markdown, falling back to plain text if entity parsing fails."""
    try:
        return await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Markdown parse failed, falling back to plain text: {e}")
        plain_text = text.replace("*", "").replace("`", "")
        return await message.reply_text(plain_text, reply_markup=reply_markup)


async def _safe_edit(query, text: str, reply_markup=None):
    """Edits message with Markdown, falling back to plain text if entity parsing fails."""
    try:
        return await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Markdown edit failed, falling back to plain text: {e}")
        plain_text = text.replace("*", "").replace("`", "")
        return await query.edit_message_text(plain_text, reply_markup=reply_markup)


def build_scan_view():
    """
    Scans Wi-Fi networks and builds the message text and inline keyboard.
    Returns (message_text: str, reply_markup: InlineKeyboardMarkup).
    """
    current_name, _ = get_current_connection()
    current_ip = get_ip_address() or "Unknown"
    saved_conns = get_saved_wifi_connections()

    success, scan_result = scan_wifi()

    safe_current = (current_name or "None").replace("`", "")
    safe_ip = current_ip.replace("`", "")

    text_lines = [
        "*Bacon Bot Wi-Fi Management*",
        "",
        f"Active Connection: `{safe_current}`",
        f"IP Address: `{safe_ip}`",
        "",
        "*Nearby Networks:*"
    ]

    keyboard = [
        [
            InlineKeyboardButton("Rescan", callback_data="wifi_rescan"),
            InlineKeyboardButton("Saved Networks", callback_data="wifi_saved"),
        ]
    ]

    if not success:
        safe_err = str(scan_result).replace("`", "")
        text_lines.append(f"Scan failed: `{safe_err}`")
    elif not scan_result:
        text_lines.append("No Wi-Fi networks found.")
    else:
        for net in scan_result[:10]:
            ssid = net["ssid"]
            signal = net["signal"]
            security = net["security"].replace("_", "-").replace("*", "").replace("`", "")
            in_use = net["in_use"]
            is_saved = ssid in saved_conns

            status_tags = []
            if in_use:
                status_tags.append("Active")
            elif is_saved:
                status_tags.append("Saved")

            tag_str = f" ({', '.join(status_tags)})" if status_tags else ""
            safe_ssid = ssid.replace("`", "")
            prefix = "+" if in_use else "-"
            text_lines.append(f"{prefix} `{safe_ssid}` (Signal: {signal}%, {security}){tag_str}")

            # If it is a saved network nearby and not currently active, offer quick connect button
            if is_saved and not in_use and len(keyboard) < 6:
                callback_id = f"wifi_conn:{ssid}"
                if len(callback_id.encode("utf-8")) <= 64:
                    keyboard.append([
                        InlineKeyboardButton(f"Connect: {safe_ssid}", callback_data=callback_id)
                    ])

    text_lines.extend([
        "",
        "*Commands:*",
        "`/wifi connect <SSID> <password>`",
        "`/wifi connect <SSID>` (for saved or open networks)",
        "`/wifi saved` (view all saved networks)"
    ])

    return "\n".join(text_lines), InlineKeyboardMarkup(keyboard)


def build_saved_view():
    """
    Builds the message text and keyboard for saved connections.
    """
    saved_conns = get_saved_wifi_connections()
    current_name, _ = get_current_connection()
    safe_current = (current_name or "None").replace("`", "")

    text_lines = [
        "*Bacon Bot Saved Wi-Fi Networks*",
        "",
        f"Active Connection: `{safe_current}`",
        "",
        "*Saved Profiles:*"
    ]

    keyboard = []

    if not saved_conns:
        text_lines.append("No saved Wi-Fi networks found.")
    else:
        for name in saved_conns:
            is_active = (name == current_name)
            safe_name = name.replace("`", "")
            active_marker = " (Active)" if is_active else ""
            text_lines.append(f"- `{safe_name}`{active_marker}")

            if not is_active:
                callback_id = f"wifi_conn:{name}"
                if len(callback_id.encode("utf-8")) <= 64:
                    keyboard.append([
                        InlineKeyboardButton(f"Connect: {safe_name}", callback_data=callback_id)
                    ])

    keyboard.append([
        InlineKeyboardButton("Back to Scan", callback_data="wifi_rescan")
    ])

    return "\n".join(text_lines), InlineKeyboardMarkup(keyboard)


@authorized_only
async def wifi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Entry point for /wifi command.
    Supports:
    /wifi (scan and display)
    /wifi scan (scan and display)
    /wifi saved (view saved connections)
    /wifi connect <SSID> [password]
    """
    args = context.args or []

    if not args or args[0].lower() in ["scan", "list"]:
        msg, markup = build_scan_view()
        await _safe_reply(update.message, msg, reply_markup=markup)
        return

    subcommand = args[0].lower()

    if subcommand == "saved":
        msg, markup = build_saved_view()
        await _safe_reply(update.message, msg, reply_markup=markup)
        return

    if subcommand == "connect":
        remaining_str = " ".join(args[1:]).strip()
        if not remaining_str:
            await _safe_reply(
                update.message,
                "Usage: `/wifi connect <SSID> [password]`\nExample: `/wifi connect MyHomeWiFi secret123`"
            )
            return

        try:
            tokens = shlex.split(remaining_str)
        except ValueError:
            tokens = remaining_str.split()

        target_ssid = tokens[0]
        password = tokens[1] if len(tokens) > 1 else None

        safe_ssid = target_ssid.replace("`", "")
        await _safe_reply(
            update.message,
            f"Bacon Bot: Connecting to network `{safe_ssid}`...\nPlease wait."
        )

        success, message = connect_wifi(target_ssid, password)
        prefix = "Bacon Bot: " if success else "Bacon Bot Error: "
        await update.message.reply_text(f"{prefix}{message}")
        return

    # Unknown subcommand
    await _safe_reply(
        update.message,
        "Unknown /wifi option. Use `/wifi`, `/wifi saved`, or `/wifi connect <SSID> [password]`."
    )


@authorized_only
async def wifi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles inline keyboard callbacks for Wi-Fi management.
    """
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "wifi_rescan":
        msg, markup = build_scan_view()
        await _safe_edit(query, msg, reply_markup=markup)

    elif data == "wifi_saved":
        msg, markup = build_saved_view()
        await _safe_edit(query, msg, reply_markup=markup)

    elif data.startswith("wifi_conn:"):
        target_ssid = data[len("wifi_conn:"):]
        safe_ssid = target_ssid.replace("`", "")

        await _safe_edit(
            query,
            f"Bacon Bot: Switching to network `{safe_ssid}`...\nPlease wait up to 30 seconds."
        )

        success, message = connect_wifi(target_ssid)
        prefix = "Bacon Bot: " if success else "Bacon Bot Error: "

        # Attempt to edit or send new message after network transition
        try:
            await query.edit_message_text(f"{prefix}{message}")
        except Exception:
            await query.message.reply_text(f"{prefix}{message}")
