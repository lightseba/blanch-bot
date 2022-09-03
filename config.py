import os
from typing import Mapping

import hikari
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
INTENTS = hikari.Intents.GUILD_MEMBERS

MENTAL_ASYLUM_GUILD_ID = 1005926922062139463
LOGS_CHANNEL_ID = 1007811381694824469

MINOR_IDS = (963674009986281534,)  # eastern
ADULT_ROLE_ID = 1007477954693058660
TRUSTED_ROLE_ID = 1009589091777646643
TRUSTED_NSFW_ROLE_ID = 1015352468147806359

BLANCHPOST_MAX_TYPING_TIME = 5
BLANCHPOSTS_PER_DAY = 3
BLANCHPOST_QUOTA: Mapping[int, int] = {
    # -1 = infinite blanchposting privledge
    1005930819094851655: 10**9,  # big sister
    1011408948089335829: 10**9,  # little sister
    1011409350444716133: 10**9,  # agents
    1007766898894716968: 5,  # blanchard's strongest
    1007767250457075792: 4,  # most holesome
    1007766449349197894: 3,  # holesome
    1006033566272081970: 2,  # disciples
    1007766237260025906: 1,  # good tranner
    1005930930080325645: 0,  # member
    1005926922062139463: 0,  # everyone
}

#        |                |
#        ------           |    my mom
#             \------------------ +---
#  geyser ->                    |-|  |
#             /------------------ +---
#        ------           |
#        |                |
