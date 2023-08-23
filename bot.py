import openai
import logging
import random
import requests
import os
from dotenv import load_dotenv

from telegram import __version__ as TG_VER
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Set up secret tokens
load_dotenv()
gpt_api_token = os.getenv('gpt_api_token')
telegram_bot_token = os.getenv('telegram_bot_token')
openweather_token = os.getenv('openweather_token')
organization = os.getenv('openai_organization')

openai.organization = organization
openai.api_key = gpt_api_token

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask weather"""
    city_name = "Espoo"
    post_code = "02150"
    country_code = "fi"
    latitude = "60.2047672"
    longitude = "24.6568435"
    #response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{post_code},{country_code}&appid={openweather_token}")
    # https://api.openweathermap.org/data/2.5/forecast?lat=60.2047672&lon=24.6568435&appid=94ffcce69da74e597bbe7c0371b1b912
    # response = requests.get(f"https://api.openweathermap.org/data/2.5/forecast/hourly?lat=60.2047672&lon=24.6568435&appid=94ffcce69da74e597bbe7c0371b1b912")
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={openweather_token}")
    

    
    await update.message.reply_text("Ole hyvä, tässä sinulle säätiedot! Eikun hups, sitä ei olekaan vielä implementoitu :(\n" + str(response.content))
    

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks chatGPT for an answer."""
    if "gpt" in update.message.text or random.random() < 0.01:
        message_without_gpt = update.message.text.replace("gpt", "")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Roolisi on nuori huumorintajunen slangia puhuva äijä. Oot osana tätä chat ryhmää. puhu chillisti ja tällee. Heitä vaik läppää mut spittaa faktoi kuiteski."},
                {"role": "user", "content": message_without_gpt}
            ]
        )
        
        cost = completion.usage.total_tokens * 0.2/1000
        f = open("cost.txt", "r")
        totalcost = float(f.readline()) + cost
        f.close()
        f = open("cost.txt", "w")
        f.write(f"{totalcost:.3f}")
        f.close()
        
        message = completion.choices[0].message.content
        
        await update.message.reply_text(f"{message} [{cost:.3f}¢, total:{totalcost:.3f}]")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("saa", weather_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()