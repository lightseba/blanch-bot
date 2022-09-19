from __future__ import annotations

import asyncio
import datetime
import logging
import json
import random
import re
from typing import Optional, cast

import hikari

from config import (
    ADULT_ROLE_ID,
    AGP_ROLE_ID,
    BLANCHPOST_COUNTS_FILE,
    BLANCHPOST_MAX_TYPING_TIME,
    BLANCHPOST_QUOTA,
    BLANCHPOST_WEEK_KEY,
    CORN_ROLE_ID,
    HSTS_ROLE_ID,
    INTENTS,
    LOGS_CHANNEL_ID,
    MENTAL_ASYLUM_GUILD_ID,
    MINOR_IDS,
    SUS_WORDS,
    TOKEN,
    TRUSTED_NSFW_ROLE_ID,
    TRUSTED_ROLE_ID,
    VIKA_ID,
    VIKA_SUFFIX_DEFAULT,
    VIKA_SUFFIX_KEY,
)

bot = hikari.GatewayBot(token=TOKEN, intents=INTENTS)  # type: ignore

BLANCHPOSTING_WEEK = -1
BLANCHPOSTING_COUNTS = {}
vika_suffix = VIKA_SUFFIX_DEFAULT


def to_regex_subsequence(s: str) -> str:
    middle = "".join(rf"([{c.lower()}{c.upper()}])(.*?)" for c in s)
    return rf"^(.*?){middle}$"


corn_pattern = to_regex_subsequence("YouJustGotCorned")
corned = re.compile(corn_pattern, flags=re.MULTILINE)


def corn_subsequence(s: str) -> Optional[str]:
    m = corned.match(s)

    if m := corned.match(s):
        return "".join(
            f"||{sub}||" if i % 2 == 0 and len(sub) else sub
            for i, sub in enumerate(m.groups())
        )
    else:
        return None


@bot.listen()
async def listen_message(event: hikari.GuildMessageCreateEvent):
    """on each message"""

    msg = (event.message.content or "").lower()

    if "corn" in msg:
        await event.message.add_reaction("🌽")

    if event.message.member:
        if (
            # "corn" not in msg
            CORN_ROLE_ID in event.message.member.role_ids
        ):
            if rep := corn_subsequence(event.message.content or ""):
                if random.random() < 0.05:
                    await event.message.respond(rep, reply=True)

    for word in SUS_WORDS:
        if word in msg:
            await event.message.add_reaction("👀")
            return


async def remove_minor_adult_role(member: hikari.Member) -> None:
    """pls eastern stop adding the adult role"""

    if member.id not in MINOR_IDS:
        return

    if ADULT_ROLE_ID in member.role_ids:
        logging.info(f"See child ({member}) w/ adult role, removing...")
        await member.remove_role(ADULT_ROLE_ID)


async def scold_vika(
    member: hikari.Member,
    silent: bool = True,
    name: Optional[str] = None,
    old_suffix: Optional[str] = None,
) -> None:
    """kek"""

    logging.info(f"update from {member}")

    if member.id != VIKA_ID:
        return

    logging.info("see vika!!!!")

    is_agp = AGP_ROLE_ID in member.role_ids
    is_hsts = HSTS_ROLE_ID in member.role_ids
    is_lesbian = name is None and member.display_name.endswith(vika_suffix)

    if is_agp and not is_hsts and is_lesbian:
        return

    current_name = name or (
        member.display_name[: -len(old_suffix)]
        if old_suffix and member.display_name.endswith(old_suffix)
        else member.display_name
    )
    new_roles = hikari.UNDEFINED
    new_name = hikari.UNDEFINED

    # if not is_agp or is_hsts:
    #     new_roles = [role for role in member.role_ids if role != HSTS_ROLE_ID] + [
    #         AGP_ROLE_ID
    #     ]

    if not is_lesbian:
        prefix = current_name[: min(len(current_name), 32 - len(vika_suffix))]
        new_name = prefix + vika_suffix
        logging.info(
            f"see '{member.display_name}' not ending with '{vika_suffix}' -> '{new_name}'"
        )

    await member.edit(nickname=new_name, roles=new_roles)
    # if not silent and (not is_agp or is_hsts):
    #     await member.send("You can't fool me, autogenephile.")


async def enforce_trusted_nsfw_role(member: hikari.Member) -> None:
    """Trusted NSFW = Trusted AND adult"""

    has_adult = ADULT_ROLE_ID in member.role_ids
    has_trusted = TRUSTED_ROLE_ID in member.role_ids
    has_trusted_nsfw = TRUSTED_NSFW_ROLE_ID in member.role_ids

    if has_adult and has_trusted and not has_trusted_nsfw:
        logging.info(f"See trusted adult ({member}) w/o trusted_nsfw role, adding...")
        await member.add_role(TRUSTED_NSFW_ROLE_ID)
    elif has_trusted_nsfw and (not has_adult or not has_trusted):
        logging.info(
            f"See ({member}) with trusted_nsfw but "
            f"adult={has_adult} and trusted={has_trusted}, removing..."
        )
        await member.remove_role(TRUSTED_NSFW_ROLE_ID)


@bot.listen()
async def on_member_update(event: hikari.MemberUpdateEvent) -> None:
    """do all the role policing here on update"""

    await remove_minor_adult_role(event.member)
    await enforce_trusted_nsfw_role(event.member)
    # await scold_vika(event.member)


async def register_commands() -> None:
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
        ),
        bot.rest.slash_command_builder("bullyvika", "Change the suffix on Vika.")
        .add_option(
            hikari.CommandOption(
                type=hikari.OptionType.STRING,
                name="suffix",
                description="the new suffix (at most 31 characters)",
                is_required=True,
            )
        )
        .add_option(
            hikari.CommandOption(
                type=hikari.OptionType.STRING,
                name="prefix",
                description="new name prefix",
                is_required=False,
            )
        )
        .set_default_member_permissions(
            0
        ),  # perms 0 so it must be manually enabled on ppl
        bot.rest.context_menu_command_builder(
            hikari.CommandType.MESSAGE, "Report"
        )
        .set_is_dm_enabled(False),
    ]

    await bot.rest.set_application_commands(
        application=application.id,
        commands=commands,
        guild=MENTAL_ASYLUM_GUILD_ID,
    )


def write_post_count_to_file() -> None:
    global BLANCHPOSTING_COUNTS, BLANCHPOSTING_WEEK, vika_suffix
    BLANCHPOSTING_COUNTS[BLANCHPOST_WEEK_KEY] = BLANCHPOSTING_WEEK
    BLANCHPOSTING_COUNTS[VIKA_SUFFIX_KEY] = vika_suffix

    logging.info(f"Writing counts to file: {BLANCHPOSTING_COUNTS}")
    with open(BLANCHPOST_COUNTS_FILE, "w") as f:
        json.dump(BLANCHPOSTING_COUNTS, f)


def read_post_count_from_file() -> None:
    global BLANCHPOSTING_COUNTS, BLANCHPOSTING_WEEK, vika_suffix

    try:
        with open(BLANCHPOST_COUNTS_FILE, "r") as f:
            BLANCHPOSTING_COUNTS = json.load(f)
        BLANCHPOSTING_WEEK = BLANCHPOSTING_COUNTS[BLANCHPOST_WEEK_KEY]
        vika_suffix = BLANCHPOSTING_COUNTS[VIKA_SUFFIX_KEY]
    except FileNotFoundError:
        # no file, assume reset
        BLANCHPOSTING_COUNTS = {}
        BLANCHPOSTING_WEEK = -1
        vika_suffix = VIKA_SUFFIX_DEFAULT

    logging.info(f"Read counts from file: {BLANCHPOSTING_COUNTS}")


@bot.listen()
async def startup_blanchard(event: hikari.StartingEvent) -> None:
    """Register blanchposting command"""

    read_post_count_from_file()
    await register_commands()


@bot.listen()
async def shutdown_blanchard(event: hikari.StoppedEvent) -> None:
    """shutting down (sad beep)"""

    write_post_count_to_file()


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


def check_blanchpost_week() -> None:
    global BLANCHPOSTING_WEEK, BLANCHPOSTING_COUNTS

    current_week = datetime.datetime.now().isocalendar()[1]

    if BLANCHPOSTING_WEEK != current_week:
        BLANCHPOSTING_COUNTS = {}
        BLANCHPOSTING_WEEK = current_week


def get_blanchpost_quota(member: hikari.Member) -> int:
    """
    get # of blanchposts this person has this week
    """
    check_blanchpost_week()

    so_far = BLANCHPOSTING_COUNTS.get(member.id, 0)
    quota = max(
        (
            quota
            for role_id, quota in BLANCHPOST_QUOTA.items()
            if role_id in member.role_ids
        ),
        default=0,
    )
    remaining = quota - so_far

    if remaining > 0:
        BLANCHPOSTING_COUNTS[int(member.id)] = so_far + 1

    return remaining


async def handle_blanchpost(interaction: hikari.CommandInteraction) -> None:
    """respond to /blanchpost commands"""

    assert interaction.options
    assert interaction.member

    channel = await interaction.fetch_channel()
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

    remaining_posts = get_blanchpost_quota(interaction.member)

    if remaining_posts == 0:
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            "Be silent you sputtering peon. "
            "Don't you dare speak for me. "
            "(You've run out of blanchposts this week!)",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        "Thank you for the message, my loyal soldier. "
        f"(You have {remaining_posts-1} blanchposts remaining this week)",
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


async def handle_bullyvika(interaction: hikari.CommandInteraction) -> None:
    """respond to /blanchpost commands"""
    global vika_suffix

    assert interaction.options
    assert interaction.member

    new_suffix = cast(str, interaction.options[0].value)
    new_prefix = (
        cast(str, interaction.options[1].value)
        if len(interaction.options) >= 2
        else None
    )

    logging.info(f"Got vika suffix request from {interaction.member}, '{new_suffix}'")

    if len(new_suffix) > 31:
        logging.error("suffix is too long!!")
        await interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            "That suffix is too long! It can be at most 31 characters.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return

    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        f"Thank you {interaction.member.display_name}. Allow me to apply it...",
        flags=hikari.MessageFlag.EPHEMERAL,
    )

    old_suffix = vika_suffix
    vika_suffix = " " + new_suffix

    vika = await bot.rest.fetch_member(MENTAL_ASYLUM_GUILD_ID, VIKA_ID)
    await scold_vika(vika, silent=True, name=new_prefix, old_suffix=old_suffix)


async def handle_report(interaction: hikari.CommandInteraction) -> None:
    """respond to /blanchpost commands"""
    global vika_suffix

    assert interaction.member

    await interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        f"Thank you {interaction.member.display_name}. This message has been reported to the moderators.",
        flags=hikari.MessageFlag.EPHEMERAL,
    )

    channel = await interaction.fetch_channel()
    message = await channel.fetch_message(interaction.target_id)
    logs_channel = await bot.rest.fetch_channel(LOGS_CHANNEL_ID)

    await logs_channel.send(
        content=f"{interaction.member.mention} has reported a message:\n"+f"{message.make_link(MENTAL_ASYLUM_GUILD_ID)}\n"+"<@&1005930819094851655> <@&1011408948089335829> <@&1011409350444716133>",
        mentions_everyone=True,
        user_mentions=True,
        role_mentions=True,
    )

@bot.listen()
async def handle_interactions(event: hikari.InteractionCreateEvent) -> None:
    """Listen for slash and message commands being executed."""

    if isinstance(event.interaction, hikari.CommandInteraction):
        # slash commands

        if event.interaction.command_name == "blanchpost":
            await handle_blanchpost(event.interaction)
        elif event.interaction.command_name == "bullyvika":
            await handle_bullyvika(event.interaction)
        elif event.interaction.command_name == "Report":
            await handle_report(event.interaction)


bot.run()
