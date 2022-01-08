import random
from settings import MYTOKEN
from utils import WORDLEBANK

from discord.ext import commands

WORDS = WORDLEBANK
WORDS_SET = set(WORDS)


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


class MyContext(commands.Context):
    async def checkGame(self, guild_id):
        return guild_id in self.gamess


class WordleBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.games = dict()

    # Override superclass Context class with my own
    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

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


bot = WordleBot(command_prefix="$")


# @bot.slash_command()
@bot.command()
async def start(ctx, game_type: str):
    """Starts a new Wordle game (solo, collab, custom) if one hasn't begun already.
    """
    gid = ctx.guild.id

    if await bot.checkGame(gid):
        await ctx.send(
            "Game already started. End the game first before starting a new one."
        )
        return

    if game_type == "collab":
        await ctx.send("Starting standard game of Wordle...")
        word = random.choice(WORDS)

        host = ctx.author
        await bot.addGame(gid, WordleGame(host, ctx.guild.name, ctx.channel.name, word))
        await ctx.send("Send in a guess. You have 6 guesses.")
    elif game_type == "solo":
        await ctx.send("Feature not yet supported. Try something else!")
    elif game_type == "custom":
        await ctx.send("Feature not yet supported. Try something else!")
    else:
        await ctx.send(
            f"Invalid game type chosen. Choose either solo, collab, or custom."
        )


# @bot.slash_command()
@bot.command()
async def review(ctx):
    """Review your previous guesses."""
    await ctx.send("Your guesses so far are:")
    game = await bot.getGame(ctx.guild.id)
    await ctx.send(game.getHistory())


# @bot.slash_command()
@bot.command()
async def letters(ctx):
    """Get which letters are still possible."""
    game = await bot.getGame(ctx.guild.id)
    await ctx.send("Your available letters are:")
    for k, v in game.getLetters().items():
        if k == "open":
            await ctx.send(f":white_circle: Open letters: {' '.join(v)}")
        else:
            await ctx.send(f":green_circle: Found letters: {' '.join(v)}")


# @bot.slash_command()
@bot.command()
async def guess(ctx, guess: str):
    """Make a guess in a wordle game."""
    guess = guess.upper()
    print(f"Attempted guess in [{ctx.guild.name}] was {guess}")
    if len(guess) != 5:
        await ctx.send("Guess invalid, needs to be 5 letters.")
        return
    if guess not in WORDS_SET:
        await ctx.send("Guess invalid, needs to be real 5 letter word.")
        return
    await ctx.send(f"Your guess was: {guess}")
    gid = ctx.guild.id
    game = await bot.getGame(gid)
    guess_result, response = game.process_guess(guess)
    await ctx.send(game.getHistory())
    await ctx.send(response)
    if guess_result == -1 or guess_result == 1:
        # Game over
        await bot.deleteGame(gid)
    return


# @bot.slash_command()
@bot.command()
async def end(ctx):
    """Ends game in current guild."""
    gid = ctx.guild.id
    game = await bot.getGame(gid)
    word = game.endGame()
    await ctx.send(f"Game over! The word was {word}")
    await bot.deleteGame(gid)


bot.run(MYTOKEN)
