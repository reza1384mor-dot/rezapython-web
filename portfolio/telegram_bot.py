import urllib.request
import urllib.parse
import json
import logging
import threading
import html
from django.conf import settings

logger = logging.getLogger(__name__)

def _send_notification_worker(name: str, email: str, subject: str, message: str):
    bot_token = getattr(settings, "TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", "").strip()

    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # ایمن‌سازی مقادیر پویا در برابر تزریق کدهای HTML و جلوگیری از خطای تلگرام
    safe_name = html.escape(str(name or "کاربر ناشناس").strip())
    safe_email = html.escape(str(email or "ندارد").strip())
    safe_subject = html.escape(str(subject or "بدون موضوع").strip())
    safe_message = html.escape(str(message or "").strip())

    text = (
        "📬 <b>پیام جدید از وب‌سایت شخصی!</b> 🌐\n"
        "────────────────────\n"
        f"👤 <b>فرستنده:</b> {safe_name}\n"
        f"📧 <b>ایمیل:</b> <code>{safe_email}</code>\n"
        f"📝 <b>موضوع:</b> {safe_subject}\n"
        "────────────────────\n"
        f"💬 <b>متن پیام:</b>\n{safe_message}\n\n"
        "<i>این پیام به صورت خودکار از طریق وب‌سایت به ربات تلگرام ارسال شد.</i>"
    )

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                logger.info(f"Telegram notification sent successfully for message from {safe_name}.")
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {e}")


def send_telegram_contact_notification(name: str, email: str, subject: str, message: str) -> None:
    """ارسال ناهمگام و بدون تاخیر پیام از وب‌سایت به ربات تلگرام با داده‌های پاک‌سازی‌شده"""
    thread = threading.Thread(
        target=_send_notification_worker,
        args=(name, email, subject, message),
        daemon=True
    )
    thread.start()
