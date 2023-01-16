from os import environ
from shortner import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CREDS
from pyshorteners.base import BaseShortener

START_TEXT = """Hello {} 😌
I am a link shortener telegram bot
with custom link support.

`I can short any type of link`

Made by @lamaphssi"""

HELP_TEXT = """Send any long link which you want to shorten"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('My Master', url='lamaphssi.t.me')
        ]
    ]
)

@app.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    await update.reply_text(
        text=START_TEXT.format(update.from_user.mention),
        reply_markup=START_BUTTONS,
        disable_web_page_preview=True,
        quote=True
    )

@app.on_message(filters.private & filters.command(["help"]))
async def start(bot, update):
    await update.reply_text(
        text=HELP_TEXT,
        disable_web_page_preview=True,
        quote=True
    )


@app.on_message(filters.private & filters.command(["expand"]))
async def expand(bot, update):
    msg1 = await bot.send_message(
        chat_id = update.chat.id,
        text = "`Please wait...`"
    )
    # await msg1.delete()

    expanded_text = f'**--Expanded Link--**\n'
    if update.reply_to_message:
        text = update.reply_to_message.text
    else:
        text = update.text.split()[1]

    ex = BaseShortener()
    link = ex.expand(text)
    await msg1.reply_text(
        text=expanded_text + f'\n{link}\n\nThank You!',
        disable_web_page_preview=True,
        quote=True
    )

