from pyrogram import Client
from config import CREDS

app = Client("url_shortener_bot",
             api_id=CREDS['API_ID'],
             api_hash=CREDS['API_HASH'],
             bot_token=CREDS['BOT_TOKEN']
             )

app.run()