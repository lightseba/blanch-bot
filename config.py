import os
from typing import Final, Mapping, Sequence

import hikari
from dotenv import load_dotenv

load_dotenv()

TOKEN: Final[str] = os.getenv("TOKEN") or ""
INTENTS: Final[hikari.Intents] = (
    hikari.Intents.GUILD_MEMBERS | hikari.Intents.GUILD_MESSAGES
)

MENTAL_ASYLUM_GUILD_ID: Final[int] = 1005926922062139463
LOGS_CHANNEL_ID: Final[int] = 1007811381694824469
REPORTS_CHANNEL_ID: Final[int] = 1007811353404264548

MINOR_IDS: Final[Sequence[int]] = (
    963674009986281534,  # eastern
    # 394329175680352258,  # clem
)
VIKA_ID: Final[int] = 398125196567117824

ADULT_ROLE_ID: Final[int] = 1007477954693058660
TRUSTED_ROLE_ID: Final[int] = 1009589091777646643
TRUSTED_NSFW_ROLE_ID: Final[int] = 1015352468147806359
AGP_ROLE_ID: Final[int] = 1006014075538513973
HSTS_ROLE_ID: Final[int] = 1006014165929959505
CORN_ROLE_ID: Final[int] = 1017197709775609946

VIKA_SUFFIX_DEFAULT: Final[str] = ""
VIKA_SUFFIX_KEY: Final[str] = "VIKA_SUFFIX"

SUS_WORDS: Final[Sequence[str]] = ("agp", "hsts", "aap")
BANNED_LINK: Final[str] = "anthro.cs.uni-freiburg.de"

BLANCHPOST_COUNTS_FILE: Final[str] = "blanchposting_counts.json"
BLANCHPOST_WEEK_KEY = "BLANCHPOST_WEEK"
BLANCHPOST_MAX_TYPING_TIME: Final[int] = 5
BLANCHPOSTS_PER_DAY: Final[int] = 3
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
