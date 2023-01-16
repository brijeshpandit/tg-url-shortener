import aiohttp

from pyrogram.types import ForceReply
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from pyshorteners import Shortener
from pyshorteners.base import BaseShortener

app = Client("url_shortener_bot")

regex_filters = filters.regex(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
req_filters = filters.private & regex_filters

@app.on_message(req_filters | filters.command(['short']))
async def reply_links(bot, update):
    global link
    link = ""
    link_msg = ""
    if update.command:
        link += update.reply_to_message.text
        link_msg += str(update.reply_to_message_id)
    else:
        link += update.matches[0].group(0)
        link_msg += str(update.id)

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
                [InlineKeyboardButton(text='v.gd Link', url=url2)]
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

@app.on_callback_query(filters.regex('custom'))
async def custom(bot, update):
    msg1 = await update.message.edit_text(
        text="`Analysing your link...`",
        disable_web_page_preview=True
    )
    await msg1.delete()

    link_id = update.message.reply_to_message.id
    msg2 = await bot.send_message(
        chat_id=msg1.chat.id,
        text=CUSTOM_TEXT,
        disable_web_page_preview=True,
        reply_to_message_id=link_id,
        reply_markup=ForceReply()
    )
    @app.on_message(filters.private & filters.reply)
    async def custom_text(bot, update):
        if update.reply_to_message_id == msg2.id:
            global custom_url
            custom_url = update.text
            after_cust = await update.reply_text(
                text="`Please wait ...`",
                disable_web_page_preview=True
            )
            await msg2.delete()
            await after_cust.delete()

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

async def short(link, *custom):
    shorten_urls = "**--Shortened URL--**\n"

        # Is.gd shorten
    try:
        s = Shortener()
        global url1
        url1 = ""
        if custom:
            url1 += s.isgd.short(link, list(custom)[0])
        else:
            url1 += s.isgd.short(link)
        shorten_urls += f"\n**Your is.gd url :-** {url1}"
    except Exception as error:
        print(f"is.gd error :- {error}")

    # v.gd shorten
    try:
        s = Shortener()
        global url2
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

