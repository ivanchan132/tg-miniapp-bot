import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = os.getenv("TOKEN", "").strip()  # токен задаёшь на Railway в Variables
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://example.com/")  # URL мини-аппа
OWNER_ID = int(os.getenv("OWNER_ID", "0") or 0)  # твой Telegram ID, чтобы бот слал тебе уведомления

# === ЛОГИ ===
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("bot")

# === Хендлер /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else user.first_name

    # Отправляем кнопку с мини-аппом
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Open Gift", web_app=WebAppInfo(url=MINI_APP_URL))]]
    )
    await update.message.reply_text("Привет! Открой мини-апп 🎁", reply_markup=kb)

    # Уведомляем владельца
    if OWNER_ID:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"Новый запуск бота!\nID: {user_id}\nПользователь: {username}"
        )

    log.info("User started bot: id=%s, name=%s", user_id, username)


async def on_startup(app: Application):
    # снимаем webhook
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

    # ставим кнопку в меню (⋯)
    try:
        await app.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open Gift", web_app=WebAppInfo(url=MINI_APP_URL))
        )
    except Exception:
        pass


def main():
    if not TOKEN:
        raise RuntimeError("TOKEN пуст. Задай переменную окружения TOKEN.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
