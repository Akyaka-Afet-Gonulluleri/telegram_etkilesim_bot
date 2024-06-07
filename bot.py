#!/usr/bin/env python
from email import message
import logging
from tabnanny import check
from typing import List
from copy import deepcopy
from pymemri.pod.client import PodClient
from pymemri.data.schema import Person, Edge, Location, Photo, PhoneNumber
from schema import Report, Reporter
import re
import os

#from config import TELEGRAM_TOKEN
from dotenv import load_dotenv

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
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
POD_OWNER = os.getenv('POD_OWNER')
POD_KEY = os.getenv('POD_KEY')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
APP_ENV = os.getenv('APP_ENV','development')
PORT = int(os.environ.get('PORT', '5000'))
APP_URL = os.environ.get('APP_URL')

if os.path.exists('config.py'):
    from config import TELEGRAM_TOKEN, POD_OWNER, POD_KEY, GROUP_CHAT_ID


if not TELEGRAM_TOKEN:
    print('please specify TELEGRAM_TOKEN')
    exit(-1)

if not POD_OWNER or not POD_KEY:
    print('please specify POD_OWNER and POD_KEY')
    exit(-1)

# Init Pod connection
pod = PodClient(owner_key=POD_OWNER, database_key=POD_KEY)
pod.add_to_schema(Reporter, Location, Photo, Report, PhoneNumber)
processed_file_ids = []
processed_location_keys = []

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


sessions = {}
users = {}

def init_session(name):
    sessions[name] = deepcopy(DEFAULT_SESSION)
    return sessions[name]

def get_session(name):
    try:
        return sessions[name]
    except:
        return init_session(name)

def string_format(sess):
    text = "Yeni bildirim yapildi!"
    if sess['user_info']:
        text += f"\nGonderen: {sess['user_info']}"
    else:
        text += f"\nGonderen: {sess['user']['username']} {sess['user']['first_name']}"
    if sess["history"]:
        text += f"\nBildiri: {'-'.join(sess['history'])}"
    if sess["text"]:
        text += f"\nMesaj: {sess['text']}"
    return text

def save_report(session):
    id = session["id"]
    user = session["user"]
    hist = session["history"]
    category = hist[0]
    subtype = hist[1] if len(hist) > 1 else None
    data = session["data"]
    text = session["text"] if session["status"] else ""
    status = session["status"] if session["status"] else ""
    items = []
    updates = []
    edges = []
    files = []

    if id:
        item = pod.get(id)
        updates.append(item)
    else:
        item = Report(category=category, subtype=subtype)
        items.append(item)

    if item.text and text:
        item.text += f"\n{text}"
    else:
        item.text = text
    item.status = status

    user_key = f"{user.username}_{user.first_name}"
    try:
        if user_key in users:
            reporter = users[user_key]
        else:
            reporter = pod.search({"type":"Reporter", "userKey": user_key})[0]
            print("We have the reporter in db", reporter.__dict__)
    except:
        print("ERROR: User does not exist in db")

    if not item.reporter:   
        edges.append(Edge(item, reporter, "reporter"))
    
    for i, loc in enumerate(data["location"]):
        loc_key = str(loc.latitude * loc.longitude)
        if loc_key not in processed_location_keys:
            location = Location(latitude=loc.latitude, longitude=loc.longitude)
            items.append(location)
            edges.append(Edge(item, location, "location"))
            processed_location_keys.append(loc_key)

    for i, file in enumerate(data["photo"]):
        if file.file_id not in processed_file_ids:
            image_bytes = bytes(file.download_as_bytearray())
            photo = Photo.from_bytes(image_bytes)
            edges += photo.get_edges("file")
            items += [photo, photo.file[0]]
            edges.append(Edge(item, photo, 'photo'))
            files.append(photo.data)
            processed_file_ids.append(file.file_id)
    
    pod.bulk_action(create_items=items, update_items=updates, create_edges=edges)

    for file in files:
        pod._upload_image(file, asyncFlag=False)
    # update item id - mark as saved
    session["id"] = item.id

def register_user(user, user_info):
    user_key = f"{user.username}_{user.first_name}"
    reporter = Reporter(userKey=user_key, username=user.username, information=user_info)
    
    # look for phone number
    phone_search = re.search('(\+?0?5[3456]\d{7,9})', user_info)
    if phone_search:
        phoneNumber = phone_search.group(1)
        phone_item = PhoneNumber(phoneNumber=phoneNumber)
        pod.create(phone_item)
        reporter.add_edge('hasPhoneNumber', phone_item)
    
    print("Adding new reporter:", reporter.__dict__)
    reporter.update(pod)
    users[user_key] = reporter
    return reporter

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with 5 inline buttons attached."""
    context.bot.callback_data_cache.clear_callback_data()
    context.bot.callback_data_cache.clear_callback_queries()
    session_key = f"{update.effective_user.username}_{update.effective_user.first_name}"
    # init session
    sess = init_session(session_key)
    sess["user"] = update.effective_user
    try:
        if session_key not in users:
            user = pod.search({"type":"Reporter", "userKey": session_key})[0]
            users[session_key] = user
    except:
        register_text = """
Merhaba. Kayıt olmak icin lütfen 
Adınız ve Soyadınız, Telefon Numarasınız, Kan Grubunuz ve Acil Durumda Ulaşılması için bir yakınınızın Ad Soyad ve Telefon numarasını giriniz.

Örnek:
Ali Çetin, 05551234567, ARH+, Tuna Bilge 05551234567
        """
        update.message.reply_text(register_text)
        return

    update.message.reply_text('Ben Akyaka Afet Gonulluleri envanter/etkilesim botu. Ne bildirmek istiyorsunuz?', reply_markup=build_keyboard(OPTIONS))
    logger.info("Started interacting with {}".format(update.effective_user))


def help(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text(
        "/basla yazarak etkilesime gecebilirsiniz.\n"
        "Yonergeleri izleyerek bilgileri bize hizlica ulastirabilirsiniz.\n"
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

def check_status(update: Update, context: CallbackContext):
    sess = get_session(update.effective_user.username)
    if sess and sess["user"] and sess["data"] and sess["data"]["location"] and len(sess["history"]) > 0:
        save(update, context)
        if not sess["data"]["photo"] and not sess["text"]:
            update.message.reply_text("Bilgiler kaydedildi. Resim gonderebilir ve/veya mesaj yazabilirsiniz. Sonlandirmak icin '/bitir' yaziniz.")
        if not sess["data"]["location"] and not sess["text"]:
            update.message.reply_text("Bilgiler kaydedildi. Lokasyon gonderebilir ve/veya mesaj yazabilirsiniz. Sonlandirmak icin '/bitir' yaziniz.")
        if sess["data"]["location"] and sess["data"]["photo"] and not sess["text"]:
            update.message.reply_text(
                "Bildiriminiz alindi!\n"
                "Etkilesiminiz icin tesekkurler. Yangin tehlikesi durumunda bana yazmayi unutmayin! Yeniden baslatmak icin /basla yaziniz."
            )
            context.bot.send_message(GROUP_CHAT_ID, string_format(sess))
            for l in sess["data"]["location"]:
                context.bot.send_location(GROUP_CHAT_ID, location=l)
            for p in sess["data"]["photo"]:
                context.bot.send_photo(GROUP_CHAT_ID, p.file_id)
            clear(update, context)
            return True
    return False

def check_complete(update: Update, context: CallbackContext):
    sess = get_session(update.effective_user.username)
    if sess and sess["user"] and sess["data"] and sess["data"]["location"] and sess["data"]["photo"] and sess["text"]:
        return True
    else:
        return False

def save(update: Update, context: CallbackContext) -> None:
    sess = get_session(update.effective_user.username)
    logger.info("Saving report {}".format(sess))
    save_report(sess)

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
    if text == "/yeniden": restart(update, context)
    if text == "/bitir": clear(update, context)

    sess = get_session(update.effective_user.username)
    if text[0] != "/" and len(text) > 5:
        user_key = f"{update.effective_user.username}_{update.effective_user.first_name}"
        if user_key in users:
            sess["text"] = text
            check_status(update, context)
        else:
            print(f"Registering user {update.effective_user} with {text}")
            sess["user_info"] = text
            register_user(update.effective_user, text)
            start(update, context)

def image_handler(update: Update, context: CallbackContext):
    sess = get_session(update.effective_user.username)
    file = context.bot.getFile(update.message.photo[-1].file_id)
    sess["data"]["photo"].append(file)
    check_status(update, context)

def location_handler(update: Update, context: CallbackContext):
    sess = get_session(update.effective_user.username)
    sess["data"]["location"].append(update.message.location)
    check_status(update, context)

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
    if APP_ENV == 'production':
        updater.start_webhook(listen="0.0.0.0",port=PORT,url_path=TELEGRAM_TOKEN, webhook_url=APP_URL + TELEGRAM_TOKEN)
    else:
        updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()