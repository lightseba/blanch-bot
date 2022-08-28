from __future__ import annotations

import asyncio
import logging
import os
import random

from dotenv import load_dotenv
import hikari


load_dotenv()
TOKEN = os.getenv("TOKEN")
EASTERN_USER_ID = int(os.getenv("EASTERN_USER_ID"))
ADULT_ROLE_ID = int(os.getenv("ADULT_ROLE_ID"))
MENTAL_ASYLUM_GUILD_ID = int(os.getenv("MENTAL_ASYLUM_GUILD_ID"))
BLANCHPOSTING_PERMS = 2  # can kick = can blanchpost
INTENTS = hikari.Intents.GUILD_MEMBERS


bot = hikari.GatewayBot(token=TOKEN, intents=INTENTS)


@bot.listen()
async def remove_eastern_adult_role(event: hikari.MemberUpdateEvent) -> None:
    """pls eastern stop adding the adult role"""

    if event.member.id != EASTERN_USER_ID:
        return

    if ADULT_ROLE_ID in event.member.role_ids:
        logging.info(
            f"See eastern ({event.member}) w/ adult role (id={ADULT_ROLE_ID}), removing..."
        )
        await event.member.remove_role(ADULT_ROLE_ID)


@bot.listen()
async def register_commands(event: hikari.StartingEvent) -> None:
    """Register blanchposting command"""
    application = await bot.rest.fetch_application()

    commands = [
        bot.rest.slash_command_builder(
            "blanchpost", "Summon the ghost of Ray Blanchard."
        )
        .add_option(
            hikari.commands.CommandOption(
                type=hikari.commands.OptionType.STRING,
                name="message",
                description="His message",
                is_required=True,
            )
        )
        .add_option(
            hikari.commands.CommandOption(
                type=hikari.commands.OptionType.STRING,
                name="reply",
                description="Message ID to reply to.",
                is_required=False,
            )
        )
        .set_default_member_permissions(BLANCHPOSTING_PERMS)
    ]

    await bot.rest.set_application_commands(
        application=application.id,
        commands=commands,
        guild=MENTAL_ASYLUM_GUILD_ID,
    )


@bot.listen()
async def handle_interactions(event: hikari.InteractionCreateEvent) -> None:
    """Listen for slash commands being executed."""
    global pattern

    if not isinstance(event.interaction, hikari.CommandInteraction):
        # only listen to command interactions, no others!
        return

    if event.interaction.command_name != "blanchpost":
        return

    try:
        message = event.interaction.options[0].value
        reply_msg_id = (
            event.interaction.options[1].value
            if len(event.interaction.options) >= 2
            else None
        )
        channel = await event.interaction.fetch_channel()
        reply_msg = (
            await channel.fetch_message(int(reply_msg_id)) if reply_msg_id else None
        )

        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            "Thank you for the message, my loyal soldier.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )

        async with channel.trigger_typing():
            wait_time = random.random() * 5
            await asyncio.sleep(wait_time)

        if reply_msg:
            # respond to a specific message given the ID
            await reply_msg.respond(
                content=message,
                reply=True,
                mentions_everyone=True,
                user_mentions=True,
                role_mentions=True,
            )
        else:
            # post without replying
            await channel.send(
                content=message,
                mentions_everyone=True,
                user_mentions=True,
                role_mentions=True,
            )
    except Exception as e:
        logging.error("Got error when blanchposting")
        logging.error(e)


bot.run()
