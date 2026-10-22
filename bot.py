
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

SERVICES = {
    "posts": ("Посты для соцсетей", "3 поста — 5 €"),
    "products": ("Описания товаров", "5 описаний — 5 €"),
    "ads": ("Рекламные тексты", "3 текста — 5 €"),
}

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Посты", callback_data="posts")],
        [InlineKeyboardButton("🛍 Описания товаров", callback_data="products")],
        [InlineKeyboardButton("📢 Реклама", callback_data="ads")],
        [InlineKeyboardButton("💶 Цены", callback_data="prices")],
        [InlineKeyboardButton("📩 Оставить заявку", callback_data="order")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я SmartTextServiceBot 🤖\nВыбери услугу:",
        reply_markup=menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data in SERVICES:
        name, price = SERVICES[q.data]
        await q.message.reply_text(f"{name}\nЦена: {price}")
    elif q.data == "prices":
        text = "\n".join(f"{name}: {price}" for name, price in SERVICES.values())
        await q.message.reply_text(text)
    elif q.data == "order":
        context.user_data["order"] = True
        await q.message.reply_text("Напиши, какая услуга нужна и что ты хочешь заказать.")

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("order"):
        await update.message.reply_text("Напиши /start, чтобы увидеть услуги.")
        return

    order = update.message.text
    admin_id = os.getenv("ADMIN_CHAT_ID")

    if admin_id:
        try:
            await context.bot.send_message(
                chat_id=int(admin_id),
                text=f"Новая заявка от {update.effective_user.full_name}:\n{order}"
            )
            await update.message.reply_text("Заявка отправлена! Спасибо.")
        except Exception:
            await update.message.reply_text("Не удалось передать заявку. Попробуй позже.")
    else:
        print("Заявка:", order)
        await update.message.reply_text("Заявка принята в тестовом режиме.")

    context.user_data["order"] = False

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Не задан BOT_TOKEN. Настрой его перед запуском.")
        return

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    print("SmartTextServiceBot запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
