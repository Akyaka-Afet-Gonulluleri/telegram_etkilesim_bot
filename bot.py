#!/usr/bin/env python
import logging
from tabnanny import check
from typing import List
from copy import deepcopy

from config import TELEGRAM_TOKEN
from constants import DEFAULT_SESSION, OPTIONS, REQUEST_INFO_TEMPLATE

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Filters,
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    CallbackContext,
    InvalidCallbackData,
    PicklePersistence,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


sessions = {}

def get_session(name):
    try:
        return sessions[name]
    except:
        sessions[name] = deepcopy(DEFAULT_SESSION)
        return sessions[name]


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with 5 inline buttons attached."""
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    session_key = update.effective_user.username
    sess = get_session(session_key)
    sess["user"] = update.effective_user
    update.message.reply_text('Akyaka Afet Gonulluleri etkilesim alanina hosgeldiniz. Ne bildirmek istiyorsunuz?', reply_markup=build_keyboard(OPTIONS))
    logger.info("Started interacting with {}".format(update.effective_user))


def help(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text(
        "/basla yazarak etkilesime gecebilirsiniz.\n"
        "Yonergeleri izleyerek bildirilerinizi bize hizlica ulastirabilirsiniz.\n"
        "Bir sorun veya eksiklik yasanirsa /temizle yazarak yeniden baslayabilirsiniz.\n"
    )


def clear(update: Update, context: CallbackContext) -> None:
    """Clears the session and the callback data cache"""
    # clear session
    sess = get_session(update.effective_user.username)
    logger.info("Clearing session: {}".format(sess))
    del sessions[update.effective_user.username]
    # clear callback data
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    # update.effective_message.reply_text('Etkilesim temizlendi')

def restart(update: Update, context: CallbackContext) -> None:
    clear(update, context)
    start(update, context)

def check_finalized(update: Update, context: CallbackContext):
    sess = get_session(update.effective_user.username)
    if sess and sess["user"] and sess["data"] and sess["data"]["location"] and sess["data"]["photo"]:
        return True
    else:
        return False
    
def finalize(update: Update, context: CallbackContext) -> None:
    sess = get_session(update.effective_user.username)
    logger.info("New report {}".format(sess))
    context.bot.send_message("-723669546", "Yeni bildirim yapildi!\nGonderen: {}\nBildiri: {}".format(sess["user"]["username"], "-".join(sess["history"])))
    for l in sess["data"]["location"]:
        context.bot.send_location("-723669546", location=l)
    for p in sess["data"]["photo"]:
        context.bot.send_photo("-723669546", open("images/{}".format(p.file_unique_id), 'rb'))
    update.message.reply_text(
        "Bildiriminiz alindi!\n"
        "Etkilesiminiz icin tesekkurler. Yangin tehlikesi durumunda bana yazmayi unutmayin!"
    )
    clear(update, context)

def build_keyboard(options: List[int]) -> InlineKeyboardMarkup:
    """Helper function to build the next inline keyboard."""
    columns = []
    for o in options.keys():
        columns.append(InlineKeyboardButton(str(o), callback_data=o))
    return InlineKeyboardMarkup.from_column(columns)

def process_next(session, query):
    option = query.data
    logger.info("User {} replied with {}".format(session["user"] , option))
    current_options = deepcopy(OPTIONS)
    for h in session["history"]:
        try:
            current_options = current_options[h]
        except Exception as e:
            pass
    text = current_options["text"]
    del current_options["text"]
    # if option == "location":
    #     query.message.reply_text(text)
    if len(current_options.keys()) > 0:
        query.message.reply_text(text, reply_markup=build_keyboard(current_options))
    else:
        # QA is done, now request location and picture
        query.message.reply_text(REQUEST_INFO_TEMPLATE.format(h), reply_markup=ReplyKeyboardRemove())

def option_selected(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    print("Query data", query)
    sess = get_session(query.from_user.username)
    # ensure user data is included
    if not sess["user"] or not sess["user"].username:
        sess["user"] = update.effective_user
    # Get the data from the callback_data.
    # If you're using a type checker like MyPy, you'll have to use typing.cast
    # to make the checker get the expected type of the callback_data
    option = query.data
    # append the number to the list
    sess["history"].append(option)
    process_next(sess, query)

    # we can delete the data stored for the query, because we've replaced the buttons
    context.drop_callback_data(query)

def text_handler(update: Update, context: CallbackContext):
    text = update.message.text
    logger.info("User {} wrote {}".format(update.effective_user.username, text))

    if text == "/basla": start(update, context)
    if text == "/yardim": help(update, context)
    if text == "/temizle": restart(update, context)


def image_handler(update: Update, context: CallbackContext):
    sess = get_session(update.effective_user.username)
    file = context.bot.getFile(update.message.photo[-1].file_id)
    print("Downloading file", file)
    file.download("images/{}".format(file.file_unique_id))
    sess["data"]["photo"].append(file)
    if check_finalized(update, context):
        finalize(update, context)
    else:
        update.message.reply_text("Resim alindi. Lutfen simdi ilgili lokasyonu paylasin.", reply_markup=ReplyKeyboardRemove())

def location_handler(update: Update, context: CallbackContext):
    sess = get_session(update.effective_user.username)
    sess["data"]["location"].append(update.message.location)
    if check_finalized(update, context):
        finalize(update, context)
    else:
        update.message.reply_text("Lokasyon alindi. Lutfen simdi resim cekip gonderin.", reply_markup=ReplyKeyboardRemove())

def handle_invalid_button(update: Update, context: CallbackContext) -> None:
    """Informs the user that the button is no longer available."""
    update.callback_query.answer()
    update.effective_message.edit_text("Bu adim geride kaldi.")


def main() -> None:
    """Run the bot."""
    # We use persistence to demonstrate how buttons can still work after the bot was restarted
    persistence = PicklePersistence(
        filename='persistence.pickle', store_callback_data=True
    )
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN, persistence=persistence, arbitrary_callback_data=True)

    updater.dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, text_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(handle_invalid_button, pattern=InvalidCallbackData))
    updater.dispatcher.add_handler(CallbackQueryHandler(option_selected))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()