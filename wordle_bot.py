import random

from discord.mentions import A
from settings import MYTOKEN
from utils import WORDLEBANK

import discord
from discord.ext import commands
from discord.commands import Option
import logging

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


class WordleGame:
    def __init__(self, host, guild_name, channel, word):
        self.game_started = True
        self.host = host
        self.guild_name = guild_name
        self.channel = channel
        self.word = word
        self.turns = 0
        self.history = ""
        self.letters = {
            "open": list(map(chr, range(ord("A"), ord("Z") + 1))),
            "good": [],
        }
        print(f"Game started by {host} in guild [{guild_name}] with word {word}.")

    def process_guess(self, guess):
        out_string = ""
        letters_open = self.letters["open"]
        letters_good = self.letters["good"]

        # Make a pretty history first
        for i in range(5):
            out_string += f":regional_indicator_{guess[i].lower()}: "
        out_string += "\n"

        for i in range(5):
            if guess[i] in letters_open:
                letters_open.remove(guess[i])

            if guess[i] == self.word[i]:
                out_string += ":green_circle: "
                if guess[i] not in letters_good:
                    letters_good.append(guess[i])
            elif guess[i] in self.word:
                out_string += ":yellow_circle: "
                if guess[i] not in letters_good:
                    letters_good.append(guess[i])
            else:
                out_string += ":black_circle: "
        out_string += "\n"
        self.history += out_string
        self.turns += 1
        if guess == self.word:
            return (1, f"You won in {self.turns} turns!")  # win
        if self.turns == 6:
            return (-1, f"You lost! The word was {self.word}.")  # loss
        return (
            0,
            f"You still have {6-self.turns} "
            + ("turn" if self.turns == 5 else "turns")
            + " left!",
        )

    def endGame(self):
        self.turns = 6
        return self.word

    def getHistory(self):
        if self.history == "":
            return "No guesses."
        return self.history

    def getLetters(self):
        return self.letters


class WordleBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.games = dict()

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        await bot.change_presence(activity=discord.Game(name="Wordle! Use /start"))

    async def on_command_error(self, ctx, error):
        await ctx.send(f"Error: {error}")

    ## Custom functions
    async def checkGame(self, guild_id: int):
        return guild_id in self.games

    async def deleteGame(self, guild_id: int):
        if await self.checkGame(guild_id):
            del self.games[guild_id]
            return 0
        return 1

    async def addGame(self, guild_id: int, game: WordleGame):
        if await self.checkGame(guild_id):
            return False
        else:
            self.games[guild_id] = game

    async def getGame(self, guild_id: int):
        if await self.checkGame(guild_id):
            return self.games[guild_id]
        else:
            return None


intents = discord.Intents(messages=True, guilds=True)
intents.typing = False
intents.presences = False
bot = WordleBot(intents=intents)

guild_ids = [920463166591361076, 854112523464212510]
# guild_ids = [854112523464212510]
# guild_ids = None


async def _gameStarted(ctx):
    """Check if game has already started in the given context."""
    gid = ctx.guild.id
    if await bot.checkGame(gid):
        await ctx.respond(
            "Game already started. End the game first before starting a new one."
        )
        return True
    return False


async def _gameNotStarted(ctx):
    """Check if game has not yet started in the given context."""
    gid = ctx.guild.id
    if not await bot.checkGame(gid):
        await ctx.respond("No current game. Start a game first.")
        return True
    return False


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
async def start(
    ctx,
    game_type: Option(str, "Choose game type", choices=["collab", "custom", "battle"]),
):
    """Starts a new Wordle game (collab, custom, battle) if one hasn't begun already.
    """

    if await _gameStarted(ctx):
        return

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
            return

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
async def review(ctx):
    """Review your previous guesses."""
    if await _gameNotStarted(ctx):
        return

    await ctx.respond("Your guesses so far are:")
    game = await bot.getGame(ctx.guild.id)
    await ctx.send(game.getHistory())


@bot.slash_command(guild_ids=guild_ids)
async def letters(ctx):
    """Get which letters are still possible."""
    if await _gameNotStarted(ctx):
        return

    game = await bot.getGame(ctx.guild.id)
    await ctx.respond("Your available letters are:")
    for k, v in game.getLetters().items():
        if k == "open":
            await ctx.send(f":white_circle: Open letters: {' '.join(v)}")
        else:
            await ctx.send(f":green_circle: Found letters: {' '.join(v)}")


@bot.slash_command(guild_ids=guild_ids)
async def guess(ctx, guess: Option(str, "Enter your 5-letter guess")):
    """Make a guess in a wordle game."""
    if await _gameNotStarted(ctx):
        return
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
async def end(ctx):
    """Ends game in current guild."""
    gid = ctx.guild.id
    game = await bot.getGame(gid)
    word = game.endGame()
    await ctx.respond(f"Game over! The word was {word}")
    await bot.deleteGame(gid)


bot.run(MYTOKEN)
