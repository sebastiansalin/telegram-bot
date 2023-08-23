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
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={openweather_token}")
    

    
    await update.message.reply_text("Ole hyvä, tässä sinulle säätiedot! Eikun hups, sitä ei olekaan vielä implementoitu :(\n" + str(response.content))

gpt_role_list = [
    "Hauskuuttaja Harry: Harry on botin oma komediantti, joka jakaa vitsejä ja stand-up -huumoria.",
    "Tiedonetsijä Tina: Tina on tietämyksen asiantuntija ja hän vastaa kaikkiin kysymyksiin pitkällä ja monimutkaisella tiedolla.",
    "Moraalipoliisi Mike: Mike on itseoppinut moraalipoliisi, joka antaa moraalista tukea ja neuvoo eettisissä pulmissa.",
    "Runoilija Ronja: Ronja lähettää runoja ja säkeitä aiheista, jotka ovat ajankohtaisia tai pyydettyjä.",
    "Sci-fi Sami: Sami pukeutuu avaruuspukuun ja tarjoaa tieteiskirjallisuuteen liittyviä keskusteluja ja tarinoita.",
    "Historioitsija Henri: Henri on historian ystävä, joka tarjoaa historiallisia anekdootteja ja kertoo tarinoita menneisyydestä.",
    "Hölmöhuulimimmi Heidi: Heidi puhuu hassuja kieliä ja lähettää hassuja ääni- ja tekstimuotoisia viestejä.",
    "Elokuvatietäjä Eetu: Eetu on elokuvafani ja tarjoaa elokuvavinkkejä, triviaa ja arvosteluja.",
    "Matkailija Maria: Maria matkustaa maailmaa ja lähettää kuvia eri paikoista, tarjoaa matkavinkkejä ja matkakokemuksia.",
    "Kokki Kalle: Kalle on virtuaalinen kokki, joka antaa reseptejä ja ruoanlaittovinkkejä, jos käyttäjä kaipaa ruoka-inspiraatiota.",
    "My man Make: chilli young huumorintajune slangii viskova jäbä. Oot osana tätä chat ryhmää. puhu chillisti ja tällee. Heitä vaik läppää mut spittaa faktoi kuiteski."
]

def random_gpt_role():
    return gpt_role_list[random.randint(0, len(gpt_role_list)-1)]
    

message_history = []

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks chatGPT for an answer."""
    
    
    if "gpt" in update.message.text or random.random() < 0.01:
        message_without_gpt = update.message.text.replace("gpt", "")
        
        all_messages = message_history[-5:]
        all_messages.append({"role": "system", "content": random_gpt_role()})
        all_messages.append({"role": "user", "content": message_without_gpt})
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = all_messages
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
    msg = f"{update.message.text}"
    message_history.append( {"role": "user", "content": msg} )

# async def role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Asks chatGPT for an answer."""
#     args = " ".join(context.args)
#     global gpt_role
#     gpt_role = args
    
#     await update.message.reply_text(f"aight bet, mun rooli on nyt: {gpt_role}")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("saa", weather_command))
    # application.add_handler(CommandHandler("rooli", role))
    

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gpt))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()