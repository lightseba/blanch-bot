from __future__ import annotations

import asyncio
import datetime
import logging
import random
from typing import Optional, cast

import hikari

from config import (
    ADULT_ROLE_ID,
    BLANCHPOST_MAX_TYPING_TIME,
    BLANCHPOST_QUOTA,
    INTENTS,
    LOGS_CHANNEL_ID,
    MENTAL_ASYLUM_GUILD_ID,
    MINOR_IDS,
    TOKEN,
)

bot = hikari.GatewayBot(token=TOKEN, intents=INTENTS)  # type: ignore

BLANCHPOSTING_WEEK = -1
BLANCHPOSTING_COUNTS = {}


@bot.listen()
async def remove_minor_adult_role(event: hikari.MemberUpdateEvent) -> None:
    """pls eastern stop adding the adult role"""

    if event.member.id not in MINOR_IDS:
        return

    if ADULT_ROLE_ID in event.member.role_ids:
        logging.info(f"See child ({event.member}) w/ adult role, removing...")
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
            hikari.CommandOption(
                type=hikari.OptionType.STRING,
                name="message",
                description="His message.",
                is_required=True,
            )
        )
        .add_option(
            hikari.CommandOption(
                type=hikari.OptionType.STRING,
                name="reply",
                description="Message to reply to. Either a message ID or link.",
                is_required=False,
            )
        )
    ]

    await bot.rest.set_application_commands(
        application=application.id,
        commands=commands,
        guild=MENTAL_ASYLUM_GUILD_ID,
    )


async def _grab_logs_channel() -> Optional[hikari.GuildChannel]:
    return bot.cache.get_guild_channel(LOGS_CHANNEL_ID) or cast(
        hikari.GuildChannel, await bot.rest.fetch_channel(LOGS_CHANNEL_ID)
    )


@bot.listen()
async def init_bot(event: hikari.StartedEvent) -> None:
    guild = await bot.rest.fetch_guild(MENTAL_ASYLUM_GUILD_ID)

    for role_id, prob in BLANCHPOST_QUOTA.items():
        role = guild.roles[role_id]  # type: ignore
        logging.debug(f"{role} -> {prob}")


async def get_reply_message(
    reply_option: str,
    channel: hikari.TextableChannel,
) -> Optional[hikari.Message]:
    """grab the message object to reply to"""

    # discord message links go guild/channel/message
    prefix = f"https://discord.com/channels/{MENTAL_ASYLUM_GUILD_ID}/{channel.id}/"

    if reply_option.startswith(prefix):
        # remove the message link prefix
        reply_option = reply_option[len(prefix) :]

    if not reply_option.isdigit():
        return None

    try:
        reply_id = int(reply_option)
        reply_msg = await channel.fetch_message(reply_id)
    except hikari.NotFoundError:
        # couldn't find that message in this channel
        return None

    return reply_msg


def get_blanchpost_quota(member: hikari.Member) -> int:
    return max(
        (
            quota
            for role_id, quota in BLANCHPOST_QUOTA.items()
            if role_id in member.role_ids
        ),
        default=0,
    )


def check_blanchpost_week() -> None:
    global BLANCHPOSTING_WEEK, BLANCHPOSTING_COUNTS

    current_week = datetime.datetime.now().isocalendar()[1]

    if BLANCHPOSTING_WEEK != current_week:
        BLANCHPOSTING_COUNTS = {}
        BLANCHPOSTING_WEEK = current_week


def remaining_blanchpost(member: hikari.Member) -> int:
    check_blanchpost_week()

    so_far = BLANCHPOSTING_COUNTS.get(member.id, 0)
    quota = get_blanchpost_quota(member)
    remaining = quota - so_far

    if remaining:
        BLANCHPOSTING_COUNTS[member.id] = so_far + 1

    return remaining


async def handle_blanchpost(interaction: hikari.CommandInteraction) -> None:
    """respond to /blanchpost commands"""

    assert interaction.options

    channel = interaction.get_channel() or await interaction.fetch_channel()
    message_content = interaction.options[0].value
    logging.info(
        f"got blanchpost request from {interaction.member} "
        f"in {channel} with content '{message_content}'"
    )

    if len(interaction.options) >= 2:
        # replying to a specific message

        reply_option = interaction.options[1].value
        assert isinstance(reply_option, str)

        logging.info(f"got reply option: {reply_option}")
        reply_msg = await get_reply_message(reply_option, channel)
        logging.info(f"found message: {reply_msg}")

        if reply_msg is None:
            # invalid reply input
            logging.error("unable to find reply message!")
            await interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                "I can't find that message to reply to. It must be in this channel.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
    else:
        # no reply, just post it
        reply_msg = None

    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        "Thank you for the message, my loyal soldier.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )

    try:
        async with channel.trigger_typing():
            wait_time = random.random() * BLANCHPOST_MAX_TYPING_TIME
            await asyncio.sleep(wait_time)

        if reply_msg:
            # respond to a specific message
            await reply_msg.respond(
                content=message_content,
                reply=True,
                mentions_everyone=True,
                user_mentions=True,
                role_mentions=True,
            )
        else:
            # post without replying
            await channel.send(
                content=message_content,
                mentions_everyone=True,
                user_mentions=True,
                role_mentions=True,
            )

    except Exception as e:
        logging.error("Got error when blanchposting")
        logging.error(e)


@bot.listen()
async def handle_interactions(event: hikari.InteractionCreateEvent) -> None:
    """Listen for slash and message commands being executed."""

    if isinstance(event.interaction, hikari.CommandInteraction):
        # slash commands

        if event.interaction.command_name == "blanchpost":
            await handle_blanchpost(event.interaction)


bot.run()
