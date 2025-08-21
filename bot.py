import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, ContextTypes

# ====== НАСТРОЙКИ ======
TOKEN = os.getenv("TOKEN", "").strip()  # токен зададим на Railway в Variables
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://example.com/")  # сюда позже поставим GitHub Pages URL

# ====== ЛОГИ ======
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("bot")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Open Gift", web_app=WebAppInfo(url=MINI_APP_URL))]]
    )
    text = "Привет именинникам. Так как ты просила не звонить, а просто написать мне показалось слишком банальным, получилась вот такая вот штука)<br>Она включает в себя небольшую игру (а что бы было интереснее играть при проигрыше с определнным счетом тебя будут ждать небольшие поздравления внутри игры (их всего четыре, от 5 до 35)), само поздравление и подарок"
    if update.message:
        await update.message.reply_text(text, reply_markup=kb)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=kb)

async def on_startup(app: Application):
    # выключаем вебхук на всякий случай, чтобы polling работал стабильно
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        log.info("Webhook deleted.")
    except Exception as e:
        log.warning("Webhook delete failed: %s", e)

    # ставим кнопку мини-аппа в меню чата (⋯)
    try:
        await app.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open Gift", web_app=WebAppInfo(url=MINI_APP_URL))
        )
    except Exception as e:
        log.warning("Menu button set failed: %s", e)

def main():
    if not TOKEN:
        raise RuntimeError("TOKEN пуст. Задай переменную окружения TOKEN на сервере.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    log.info("Starting polling…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
