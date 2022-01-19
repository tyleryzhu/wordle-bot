import asyncio
import functools
import random
import logging

import discord
from discord import Guild
from discord.ext import commands
from discord.commands import Option
from discord.user import User

from settings import MYTOKEN
from utils import WORDLEBANK, GAME_WORDS
from wordle_game import WordleGame
from wordle_bot import WordleBot

ALL_WORDS = WORDLEBANK
CHOICE_WORDS = GAME_WORDS
WORDS_SET = set(ALL_WORDS)
GAME_SET = set(GAME_WORDS)


intents = discord.Intents(messages=True, guilds=True)
intents.typing = False
intents.presences = False
activity = discord.Game(name="Wordle! Use /start")
bot = WordleBot(intents=intents, activity=activity)

# guild_ids = [920463166591361076, 854112523464212510, 760551825379164170]
# guild_ids = [854112523464212510]
guild_ids = None

# TODO: add in locking so games can't be started over each other
# TODO: implement hardmode


def create_overwrites(ctx, *objects):
    """This is just a helper function that creates the overwrites for the
    voice/text channels.
    A `discord.PermissionOverwrite` allows you to determine the permissions
    of an object, whether it be a `discord.Role` or a `discord.Member`.
    In this case, the `view_channel` permission is being used to hide the channel
    from being viewed by whoever does not meet the criteria, thus creating a
    secret channel.
    """
    # Taken from https://github.com/Pycord-Development/pycord/blob/master/examples/secret.py

    # a dict comprehension is being utilised here to set the same permission overwrites
    # for each `discord.Role` or `discord.Member`.
    overwrites = {
        obj: discord.PermissionOverwrite(view_channel=True) for obj in objects
    }

    # prevents the default role (@everyone) from viewing the channel
    # if it isn't already allowed to view the channel.
    overwrites.setdefault(
        ctx.guild.default_role, discord.PermissionOverwrite(view_channel=False)
    )

    # makes sure the client is always allowed to view the channel.
    overwrites[ctx.guild.me] = discord.PermissionOverwrite(view_channel=True)

    return overwrites


def verifyGameNotStarted(func):
    """Decorator to verify no game has started in ctx, and exit early if not."""

    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        gid = ctx.guild.id
        if bot.checkGame(gid) or bot.checkOpenParty(gid):
            await ctx.respond("Game in progress. End game first to start a new one.")
            return
        return await func(ctx, *args, **kwargs)

    return wrapper


def verifyGameStarted(func):
    """Decorator to verify a game has started in ctx, and exit early if not."""

    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        if ctx.guild is None:
            await ctx.respond("Guesses don't work in DMs! Do it in the channel.")
            return
        gid = ctx.guild.id
        # Either a game/party exists, which is good, unless the party is still open
        if not bot.checkGame(gid) or bot.checkOpenParty(gid):
            await ctx.respond("No current game. Start a game first.")
            return
        return await func(ctx, *args, **kwargs)

    return wrapper


def verifyPartyOpen(func):
    """Decorator to verify there is an open party in guild, and exit early if not."""

    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        gid = ctx.guild.id
        if not bot.checkOpenParty(gid):
            await ctx.respond(
                "No open party. Either game in progress already, or party has not been made."
            )
            return
        return await func(ctx, *args, **kwargs)

    return wrapper


async def _validateWord(ctx, word, is_guess=True):
    """Validates that a word is 5 letter words and in our dictionary."""
    pref = "Guess" if is_guess else "Word"
    if len(word) != 5:
        msg = f"{pref} {word} invalid, needs to be 5 letters."
        if is_guess:
            await ctx.respond(msg)
        else:
            await ctx.author.send(msg)
        return False
    if word not in WORDS_SET:
        msg = f"{pref} {word} invalid, needs to be real 5 letter word."
        if is_guess:
            await ctx.respond(msg)
        else:
            await ctx.author.send(msg)
        return False
    if is_guess:
        await ctx.respond(f"Your guess was: {word}")
    else:
        await ctx.author.send(f"Your word was: {word}")
    return True


@bot.slash_command(guild_ids=guild_ids)
@verifyGameNotStarted
async def start(
    ctx: commands.Context,
    game_type: Option(str, "Choose game type", choices=["collab", "custom", "battle"]),
):
    """Starts a new Wordle game (collab, custom, battle) if one hasn't begun already."""

    gid = ctx.guild.id
    if game_type == "collab":
        await ctx.respond("Starting collaborative game of Wordle...")
        word = random.choice(CHOICE_WORDS)

        host = ctx.me  # TODO: adjust to bot's name
        bot.addGame(gid, WordleGame(host, ctx.guild.name, ctx.channel.name, word))
        await ctx.send("Send in a guess. You have 6 guesses.")
    elif game_type == "custom":
        await ctx.respond("Starting custom game of Wordle... Check your DMs!")
        host = ctx.author
        await ctx.author.send(
            "What is your custom word? It must be five-letters and in our dictionary."
        )

        def check(m):
            """Check that message is from DM and game starter, and valid."""
            return isinstance(m.channel, discord.DMChannel) and m.author == host

        msg = await bot.wait_for("message", check=check)
        word = msg.content.upper()
        # Validate word
        if not await _validateWord(ctx, word, is_guess=False):
            await ctx.send("Invalid word chosen. Try again.")
        else:
            bot.addGame(
                gid, WordleGame(host, ctx.guild.name, ctx.channel.name, word),
            )
            await ctx.send("Word has been chosen! Send in a guess. You have 6 tries.")
    elif game_type == "battle":
        host = ctx.author
        await ctx.respond(
            f"{host.name} is starting a Wordle battle... Get ready to fight!\n"
            + "A party has been opened. Use /join or /leave to interact with the party.\n"
            + "When ready, the host should use /ready to close the party and start the battle!"
        )
        party = bot.addParty(gid, host, ctx.guild.name, ctx.channel)
        party.addMember(host)
        await host.send(f"You have started a battle in [{ctx.guild.name}].")
    else:
        await ctx.respond(
            f"Invalid game type chosen. Choose either collab, custom, or battle."
        )


@bot.slash_command(guild_ids=guild_ids)
@verifyPartyOpen
async def join(ctx: commands.Context):
    """Join current party being made. Only relevant for party modes."""
    gid = ctx.guild.id
    party = bot.getGame(gid)  # gets Party if member is None
    host_name = party.host.name
    member = ctx.author
    if member in party.getMembers():
        await member.send(
            f"You are already in {host_name}'s game in [{ctx.guild.name}]."
        )
    else:
        party.addMember(member)
        await member.send(f"You have joined {host_name}'s game in [{ctx.guild.name}].")
        await ctx.respond(f"{member.name} has joined {host_name}'s game.")
    return


@bot.slash_command(guild_ids=guild_ids)
@verifyPartyOpen
async def leave(ctx: commands.Context):
    """Leave current party you are in. Only relevant for party modes."""
    gid = ctx.guild.id
    party = bot.getGame(gid)
    host_name = party.host.name
    member = ctx.author
    # Can't let the host leave!
    if member == party.host:
        await ctx.respond(
            f"You're the host, you can't leave! Use /end to end the game instead."
        )
        return
    if member in party.getMembers():
        party.removeMember(member)
        await member.send(f"You have left {host_name}'s game in [{ctx.guild.name}].")
        await ctx.respond(f"{member.name} has left {host_name}'s game.")
    else:
        await member.send(f"You are not in {host_name}'s game in [{ctx.guild.name}].")


@bot.slash_command(guild_ids=guild_ids)
@verifyPartyOpen
async def ready(ctx: commands.Context):
    """Close current party you are in and start the game. Only relevant for party modes."""
    gid = ctx.guild.id
    party = bot.getGame(gid)
    host_name = party.host.name
    await ctx.respond(f"Closing {host_name}'s party...")
    party.closeParty()

    await ctx.send(f"Creating private channels for you to battle in...")
    for member in party.getMembers():

        overwrites = create_overwrites(ctx, member)  # permission is just user, bot

        channel = await ctx.guild.create_text_channel(
            name="wordle-battle-" + member.name,
            overwrites=overwrites,
            topic="Private channel for battlin'. Hush!",
            reason="Very secret business.",
        )
        await channel.send("Your private channel is here. Battle starts in 5 seconds!")
        party.addChannel(member, channel)

    # TODO: start games in each channel and update party with them,
    # TODO: then handle guesses from each game
    word = random.choice(GAME_WORDS)
    members = party.getMembers()
    channels = party.getChannels()
    host = ctx.me  # TODO: adjust to bot's name

    member_names = ", ".join([member.name for member in members])
    await ctx.send(
        f"{member_names} will be duking it out in a battle!\n"
        + "Battle starting in 5 seconds..."
    )
    await asyncio.sleep(5)
    await ctx.send("Go!")

    for member, channel in channels.items():
        result = bot.addGame(
            gid, WordleGame(host, ctx.guild.name, channel.name, word), member
        )
        if not result:
            await ctx.send(
                f"Bad error trying to add {member.name}'s game! Exiting now..."
            )
            await end(ctx)
            return
        await channel.send("Send in a guess. You have 6 guesses.")


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def review(ctx):
    """Review your previous guesses."""
    gid = ctx.guild.id
    if bot.isParty(gid):
        game = bot.getGame(gid, ctx.author)
    else:
        game = bot.getGame(gid)
    await ctx.respond("Your guesses so far are:\n" + game.getHistory())


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def letters(ctx):
    """Get which letters are still possible."""
    gid = ctx.guild.id
    if bot.isParty(gid):
        game = bot.getGame(gid, ctx.author)
    else:
        game = bot.getGame(gid)
    letters = game.getLetters()
    msg = "Your available letters are:\n"
    msg += f":white_circle: Open letters: {' '.join(letters['open'])}\n"
    msg += f":green_circle: Found letters: {' '.join(letters['good'])}"
    await ctx.respond(msg)


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def guess(ctx, guess: Option(str, "Enter your 5-letter guess")):
    """Make a guess in a wordle game."""
    # TODO: restrict channel owner to guessing

    guess = guess.upper()
    gid = ctx.guild.id
    if bot.isParty(gid):
        party = bot.getGame(gid)
        channels = party.getChannels()
        # Verify person guessing in the channel belongs there
        if channels[ctx.author] != ctx.channel:
            await ctx.respond(
                f"{ctx.author.name}, this isn't your game! Stop guessing."
            )
            return
        game = bot.getGame(gid, ctx.author)
    else:
        game = bot.getGame(gid)
    if ctx.author == game.host:
        await ctx.respond(f"We can't have the host {game.host.name} guessing!")
        return

    print(f"Attempted guess in [{ctx.channel.name}] by {ctx.author.name} was {guess}")

    if not await _validateWord(ctx, guess, is_guess=True):
        return
    guess_result, response = game.process_guess(guess)
    await ctx.send(game.getHistory())
    await ctx.send(response)
    if guess_result == -1 or guess_result == 1:
        # Game over
        if bot.isParty(gid):
            await updateMemberFinish(ctx.guild, ctx.author, guess_result)

            party = bot.getGame(gid)
            if party.allGamesDone():
                await party.base_channel.send(
                    "All games are over. Ending in 10 seconds..."
                )
                await asyncio.sleep(10)
                await end(ctx)
            return
        bot.deleteGame(gid)
        return
    await ctx.send("Try again!")
    return


async def updateMemberFinish(guild: Guild, member: User, result: int):
    """Updates party given by gid when member finishes a game."""
    gid = guild.id
    if not bot.isParty(gid):
        return
    party = bot.getGame(gid)
    game = bot.getGame(gid, member)
    print(f"{member.name} is done!")

    # First send their status to the main channel.
    if result == 1:
        await party.base_channel.send(
            f"{member.name} has finished in {game.turns} turns!"
        )
    else:
        await party.base_channel.send(
            f"{member.name} did not finish in {game.turns} turns!"
        )
    # First allow them to see all the private channels
    channels = party.getChannels()
    for channel in channels.values():
        await channel.set_permissions(
            member, overwrite=discord.PermissionOverwrite(view_channel=True)
        )

    # Then add this member to the done list by deleting the game
    party.deleteGame(member)


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def end(ctx):
    """Ends game in current guild."""
    gid = ctx.guild.id
    if bot.isParty(gid):
        party = bot.getGame(gid)
        members = party.getMembers()
        channels = party.getChannels()
        for member, channel in channels.items():
            await channel.delete()
        await party.base_channel.send(f"Game over!")
        bot.deleteGame(gid)
    else:
        game = bot.getGame(gid)
        word = game.getWord()
        bot.deleteGame(gid)
        await ctx.respond(f"Game over! The word was {word}")


bot.run(MYTOKEN)
