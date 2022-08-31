import os
from typing import Mapping

import hikari
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
INTENTS = hikari.Intents.GUILD_MEMBERS

MENTAL_ASYLUM_GUILD_ID = 1005926922062139463

MINOR_IDS = (963674009986281534,)  # eastern
ADULT_ROLE_ID = 1007477954693058660

BLANCHPOST_MAX_TYPING_TIME = 5 # s
BLANCHPOSTS_PER_DAY = 3
BLANCHPOST_PROBABILITIES: Mapping[int, float] = {
    1005930930080325645: 0.05,  # member
    1007766237260025906: 0.10,  # good tranner
    1006033566272081970: 0.15,  # disciples
    1007766449349197894: 0.25,  # holesome
    1007767250457075792: 0.50,  # most holesome
    1007766898894716968: 1.00,  # blanchard's strongest
    # -1 = infinite blanchposting privledge
    1011409350444716133: -1,  # agents
    1011408948089335829: -1,  # little sister
    1005930819094851655: -1,  # big sister
}
