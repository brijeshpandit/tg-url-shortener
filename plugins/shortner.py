import aiohttp

from pyrogram.types import ForceReply
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from pyshorteners import Shortener
from pyshorteners.exceptions import ShorteningErrorException
import re

app = Client("url_shortener_bot")

regex_filters = filters.regex(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
req_filters = filters.private & regex_filters

link = None
link_msg = None
link_id = None
@app.on_message(req_filters | filters.command(['short']))
async def reply_links(bot, update):
    global link, link_msg, link_id
    if update.command:
        link = update.reply_to_message.text
        link_msg = str(update.reply_to_message_id)
    else:
        link = update.matches[0].group(0)
        link_msg = str(update.id)
    link_id = update.id

    await bot.send_message(
        chat_id = update.chat.id,
        text="**Please select type of link**",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text='Random', callback_data='random')],
                [InlineKeyboardButton(text='Custom', callback_data='custom')]
            ]
        ),
        reply_to_message_id = int(link_msg)
    )

@app.on_callback_query(filters.regex('random'))
async def random(bot, update):
    msg = await update.message.edit_text(
        text="`Analysing your link...`",
        disable_web_page_preview=True
    )

    msg2 = await msg.edit_text(
        text="`Please wait...`",
        disable_web_page_preview = True
        )

    shorten_urls = await short(link)

    await msg2.edit_text(
        text=shorten_urls,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text='is.gd Link', url=url1)],
                [InlineKeyboardButton(text='v.gd Link', url=url2)],
                [InlineKeyboardButton(text='Custom', callback_data='custom')]
            ]
        ),
        disable_web_page_preview=True
    )
    print(f"Random Link Generated for {msg.chat.id}")


CUSTOM_TEXT = """**Please enter your custom url by replying to this message**\n
**--NOTE--** :-\n
`--> Specified url must be between 5 and 30 characters long
--> Can only contain alphabets, numbers, characters and underscores
--> Shortened URLs are case sensitive`"""

# ALREADY_TAKEN_TEXT = """**The shortened URL you picked already exists, please choose another and reply to this message**\n
# **--NOTE--** :-\n
# `--> Specified url must be between 5 and 30 characters long
# --> Can only contain alphabets, numbers, characters and underscores
# --> Shortened URLs are case sensitive`"""

ALREADY_TAKEN_TEXT = """**{}, please try again**\n
**--NOTE--** :-\n
`--> Specified url must be between 5 and 30 characters long
--> Can only contain alphabets, numbers, characters and underscores
--> Shortened URLs are case sensitive`"""

def error(error_txt):
    if "already" in error_txt:
        return "Error: The shortened URL you picked already exists, please choose another"
    elif "least 5 character" in error_txt:
        return "Error: Short URLs must be at least 5 characters long"
    elif "maximum of 30" in error_txt:
        return "Error: Short URLs must be a maximum of 30 characters long"
    else:
        return "Unknown error occurred"


latest_msg = None
reply_warning = None

@app.on_callback_query(filters.regex('custom'))
async def custom(bot, update):
    msg1 = await update.message.edit_text(
        text="`Analysing your link...`",
        disable_web_page_preview=True
    )
    await msg1.delete()

    msg2 = await bot.send_message(
        chat_id=msg1.chat.id,
        text=CUSTOM_TEXT,
        disable_web_page_preview=True,
        reply_to_message_id=link_id,
        reply_markup=ForceReply()
    )
    global latest_msg
    latest_msg = msg2

    @app.on_message(filters.private)
    async def not_reply(bot,update):
        if update.id != (latest_msg.id-1):
            not_reply_msg = await latest_msg.reply_text(
                quote=True,
                text='Please reply to this message!',
                disable_web_page_preview=True
            )
            global reply_warning
            reply_warning = not_reply_msg

@app.on_message(filters.private & filters.reply)
async def custom_text(bot, update):
    global latest_msg, reply_warning
    if reply_warning != None:
        await reply_warning.delete()

    if update.reply_to_message_id != latest_msg.id:
        reply_warning = await bot.send_message(
            chat_id=update.chat.id,
            text='Oops!, it seems you\'ve replied to the wrong message, please reply to the above message!',
            reply_to_message_id=latest_msg.id,
            disable_web_page_preview=True
        )
    else:
        after_cust = await update.reply_text(
            text="`Checking availability, please wait...`",
            disable_web_page_preview=True,
            reply_to_message_id=update.id
        )
        await after_cust.delete()
        await latest_msg.delete()

        try:
            custom_url = update.text
            shorten_urls = await short(link, custom_url)
            await update.reply_text(
                text=shorten_urls,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(text='is.gd Link', url=url1)],
                        [InlineKeyboardButton(text='v.gd Link', url=url2)]
                    ]
                ),
                reply_to_message_id=link_id,
                disable_web_page_preview=True
            )
            print(f"Custom Link Generated for {update.chat.id}")
        except:
            already_taken = await bot.send_message(
                chat_id=update.chat.id,
                text=ALREADY_TAKEN_TEXT.format(error(error_text)),
                disable_web_page_preview=True,
                reply_to_message_id=update.id,
                reply_markup=ForceReply()
            )
            latest_msg = already_taken

async def short(link, *custom):
    shorten_urls = "**--Shortened URL--**\n"

    # Is.gd shorten
    try:
        s = Shortener()
        global url1, url2
        url1 = ""
        if custom:
            url1 += s.isgd.short(link, list(custom)[0])
        else:
            url1 += s.isgd.short(link)
        shorten_urls += f"\n**Your is.gd url :-** {url1}"
    except Exception as error:
        global error_text
        error_text = str(error)
        print(f"is.gd error :- {error}")

    # # v.gd shorten
    try:
        s = Shortener()
        url2 = ""
        if custom:
            url2 += s.vgd.short(link, list(custom)[0])
        else:
            url2 += s.vgd.short(link)
        shorten_urls += f"\n**Your v.gd url :-** {url2}"
    except Exception as error:
        print(f"v.gd error :- {error}")

    # Send the text
    try:
        shorten_urls += "\n\nThank you!"
        return shorten_urls
    except Exception as error:
        return error

@app.on_inline_query(filters.regex(r'https?://[^\s]+'))
async def inline_short(bot, update):
    link = update.matches[0].group(0)
    shorten_urls = await short(link)
    answers = [
        InlineQueryResultArticle(
            title="Short Links",
            description=update.query,
            input_message_content=InputTextMessageContent(
                message_text=shorten_urls,
                disable_web_page_preview=True
            ),
            reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(text='is.gd Link', url=url1)],
                        [InlineKeyboardButton(text='v.gd Link', url=url2)]
                    ]
            )
        )
    ]
    await bot.answer_inline_query(
        inline_query_id=update.id,
        results=answers
    )


print('Running')
app.run()