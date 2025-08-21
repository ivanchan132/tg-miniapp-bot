import os
import logging
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, MenuButtonWebApp
)
from telegram.ext import Application, CommandHandler, ContextTypes

# ====== НАСТРОЙКИ И ОКРУЖЕНИЕ ======
TOKEN        = os.getenv("TOKEN", "").strip()                     # токен бота
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://example.com/")  # URL твоего мини-аппа
ADMIN_ID     = int(os.getenv("ADMIN_ID", "1031115105") or 0)               # твой Telegram ID (кому слать уведомления)

# ====== ЛОГИ ======
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("bot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start: показать кнопку мини-аппа и прислать админу ID пользователя."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Кнопка для открытия мини-аппа
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Open Gift", web_app=WebAppInfo(url=MINI_APP_URL))]]
    )
    await context.bot.send_message(chat_id=chat_id, text="Привет! Открой мини-апп 🎁", reply_markup=kb)

    # Присылаем админу ID пользователя, который запустил бота
    if ADMIN_ID:
        username = f"@{user.username}" if user and user.username else f"{user.first_name or ''} {user.last_name or ''}".strip()
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новый запуск бота\nID: {user.id}\nПользователь: {username or '—'}"
        )
    log.info("User started: id=%s, username=%s", user.id, user.username)


async def on_startup(app: Application):
    """Отключаем webhook и ставим кнопку мини-аппа в меню (⋯)."""
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        log.info("Webhook deleted.")
    except Exception as e:
        log.warning("Webhook delete failed: %s", e)

    try:
        await app.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open Gift", web_app=WebAppInfo(url=MINI_APP_URL))
        )
        log.info("Menu button set.")
    except Exception as e:
        log.warning("Menu button set failed: %s", e)


def main():
    if not TOKEN:
        raise RuntimeError("TOKEN пуст. Задай переменную окружения TOKEN.")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup

    log.info("Starting polling…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
