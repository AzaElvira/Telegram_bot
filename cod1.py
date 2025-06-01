Мои коды, [01.06.2025 16:46]
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    CallbackContext,
)

# Настройки бота
TOKEN = "7793360965:AAEwE3rSW2JIyhVpWPyhmTIHu1eTWLX2L_8"
ADMIN_ID = 5279682897  # ID администратора (получателя сообщений)

# Ведём лог
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(name)

# Хранилище данных (в реальном боте лучше использовать базу данных)
user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    if user.id == ADMIN_ID:
        update.message.reply_text(
            "Привет, админ! Ты можешь просматривать анонимные сообщения и отвечать на них."
        )
    else:
        update.message.reply_text(
            f"Привет, {user.first_name}! Этот бот позволяет отправить анонимное сообщение. "
            "Просто напиши сообщение, и оно будет переслано админу."
        )

def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик обычных сообщений"""
    user = update.effective_user
    message = update.message

    # Если сообщение от админа - проверяем, не ответ ли это на пересланное сообщение
    if user.id == ADMIN_ID and message.reply_to_message:
        original_message = message.reply_to_message
        if original_message.from_user.id == context.bot.id and original_message.forward_from:
            # Это ответ на анонимное сообщение
            original_sender_id = original_message.forward_from.id
            context.bot.send_message(
                chat_id=original_sender_id,
                text=f"🔔 Ответ на ваше анонимное сообщение:\n\n{message.text}",
            )
            message.reply_text("✅ Ответ отправлен!")
        return

    # Если сообщение не от админа - пересылаем админу
    if user.id != ADMIN_ID:
        # Сохраняем информацию об отправителе
        user_data[message.message_id] = user.id

        # Создаем клавиатуру с кнопкой "Ответить"
        keyboard = [
            [InlineKeyboardButton("Ответить", callback_data=f"reply_{message.message_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Пересылаем сообщение админу с кнопкой
        forwarded_msg = context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📨 Анонимное сообщение:\n\n{message.text}",
            reply_markup=reply_markup,
        )

        # Сохраняем ID пересланного сообщения
        user_data[f"forwarded_{message.message_id}"] = forwarded_msg.message_id

        update.message.reply_text("✅ Ваше сообщение отправлено анонимно!")

def button_callback(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    query.answer()

    if query.data.startswith("reply_"):
        # Извлекаем ID оригинального сообщения
        original_msg_id = int(query.data.split("_")[1])

        # Получаем ID отправителя
        sender_id = user_data.get(original_msg_id)

        if sender_id:
            # Сохраняем информацию для ответа
            context.user_data["replying_to"] = sender_id
            context.user_data["original_msg_id"] = original_msg_id

            # Запрашиваем текст ответа
            query.edit_message_text(
                text=f"✍️ Введите ответ для пользователя:\n\n{query.message.text}"
            )
        else:
            query.edit_message_text("❌ Не удалось найти отправителя.")

def error_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик ошибок"""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main() -> None:
    """Запуск бота"""
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    # Обработчики команд
    dp.add_handler(CommandHandler("start", start))

    # Обработчики сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

Мои коды, [01.06.2025 16:46]
# Обработчики кнопок
    dp.add_handler(CallbackQueryHandler(button_callback))

    # Обработчик ошибок
    dp.add_error_handler(error_handler)

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if name == "main":
    main()