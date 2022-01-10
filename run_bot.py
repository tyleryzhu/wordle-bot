import functools
import random
import logging

import discord
from discord.mentions import A
from discord.ext import commands
from discord.commands import Option

from settings import MYTOKEN
from utils import WORDLEBANK
from wordle_game import WordleGame
from wordle_bot import WordleBot

WORDS = WORDLEBANK
WORDS_SET = set(WORDS)

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("discord")
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
# handler.setFormatter(
#     logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
# )
# logger.addHandler(handler)


intents = discord.Intents(messages=True, guilds=True)
intents.typing = False
intents.presences = False
bot = WordleBot(intents=intents)

guild_ids = [920463166591361076, 854112523464212510, 760551825379164170]
# guild_ids = [854112523464212510]
# guild_ids = None

# TODO: add in locking so games can't be started over each other


def verifyGameNotStarted(func):
    """Decorator to verity no game has started in ctx, and exit early if so."""

    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        gid = ctx.guild.id
        if await bot.checkGame(gid):
            await ctx.respond("Game in progress. End game first to start a new one.")
            return
        return await func(ctx, *args, **kwargs)

    return wrapper


def verifyGameStarted(func):
    """Decorator to verify a game has started in ctx, and exit early if so."""

    @functools.wraps(func)
    async def wrapper(ctx, *args, **kwargs):
        gid = ctx.guild.id
        if not await bot.checkGame(gid):
            await ctx.respond("No current game. Start a game first.")
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
    ctx,
    game_type: Option(str, "Choose game type", choices=["collab", "custom", "battle"]),
):
    """Starts a new Wordle game (collab, custom, battle) if one hasn't begun already."""

    gid = ctx.guild.id
    if game_type == "collab":
        await ctx.respond("Starting collaborative game of Wordle...")
        word = random.choice(WORDS)

        host = ctx.me  # TODO: adjust to bot's name
        await bot.addGame(gid, WordleGame(host, ctx.guild.name, ctx.channel.name, word))
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
            await bot.addGame(
                gid, WordleGame(host, ctx.guild.name, ctx.channel.name, word),
            )
            await ctx.send("Word has been chosen! Send in a guess. You have 6 tries.")
    elif game_type == "battle":
        await ctx.respond("Feature not yet supported. Try something else!")
    else:
        await ctx.respond(
            f"Invalid game type chosen. Choose either collab, custom, or battle."
        )


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def review(ctx):
    """Review your previous guesses."""
    game = await bot.getGame(ctx.guild.id)
    await ctx.respond("Your guesses so far are:" + game.getHistory())


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def letters(ctx):
    """Get which letters are still possible."""

    game = await bot.getGame(ctx.guild.id)
    letters = game.getLetters()
    msg = "Your available letters are:\n"
    msg += f":white_circle: Open letters: {' '.join(letters['open'])}\n"
    msg += f":green_circle: Found letters: {' '.join(letters['good'])}"
    await ctx.respond(msg)


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def guess(ctx, guess: Option(str, "Enter your 5-letter guess")):
    """Make a guess in a wordle game."""

    guess = guess.upper()
    gid = ctx.guild.id
    game = await bot.getGame(gid)
    if ctx.author == game.host:
        await ctx.respond(f"We can't have the host {game.host.name} guessing!")
        return

    print(f"Attempted guess in [{ctx.guild.name}] was {guess}")

    if not await _validateWord(ctx, guess, is_guess=True):
        return
    guess_result, response = game.process_guess(guess)
    await ctx.send(game.getHistory())
    await ctx.send(response)
    if guess_result == -1 or guess_result == 1:
        # Game over
        await bot.deleteGame(gid)
    return


@bot.slash_command(guild_ids=guild_ids)
@verifyGameStarted
async def end(ctx):
    """Ends game in current guild."""
    gid = ctx.guild.id
    game = await bot.getGame(gid)
    word = game.getWord()
    await ctx.respond(f"Game over! The word was {word}")
    await bot.deleteGame(gid)


bot.run(MYTOKEN)
