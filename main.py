from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
import hikari


load_dotenv()
TOKEN = os.getenv("TOKEN")
EASTERN_USER_ID = int(os.getenv("EASTERN_USER_ID"))
ADULT_ROLE_ID = int(os.getenv("ADULT_ROLE_ID"))
INTENTS = hikari.Intents.GUILD_MEMBERS


bot = hikari.GatewayBot(token=TOKEN, intents=INTENTS)


@bot.listen()
async def remove_eastern_adult_role(event: hikari.MemberUpdateEvent) -> None:
    """pls eastern stop adding the adult role"""

    if event.member.id != EASTERN_USER_ID:
        return

    if ADULT_ROLE_ID in event.member.role_ids:
        logging.info(f"See eastern ({event.member}) w/ adult role (id={ADULT_ROLE_ID}), removing...")
        await event.member.remove_role(ADULT_ROLE_ID)


bot.run()
