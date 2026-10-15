import frappe
import requests
import json

def send_notification(level="info", category="trip", title="", message=""):
    """
    Sends notification via Telegram Bot if configured, and writes a Telegram Log record.
    """
    try:
        config = frappe.get_single("Telegram Config")
        if not config.is_active or not config.bot_token:
            return

        chat_ids = []
        if config.chat_ids:
            try:
                chat_ids = json.loads(config.chat_ids)
            except Exception:
                chat_ids = [c.strip() for c in config.chat_ids.split(",") if c.strip()]

        formatted_text = f"<b>[{level.upper()}] {title}</b>\n<i>Category: {category}</i>\n\n{message}"
        api_url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"

        for chat_id in chat_ids:
            success = True
            err = None
            try:
                resp = requests.post(api_url, json={
                    "chat_id": chat_id,
                    "text": formatted_text,
                    "parse_mode": "HTML"
                }, timeout=5)
                if resp.status_code != 200:
                    success = False
                    err = resp.text
            except Exception as e:
                success = False
                err = str(e)

            log = frappe.get_doc({
                "doctype": "Telegram Log",
                "level": level,
                "category": category,
                "title": title,
                "message": message,
                "chat_id": str(chat_id),
                "success": 1 if success else 0,
                "error_message": err
            })
            log.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Telegram notification error: {str(e)}", "Wende Transport Telegram")
