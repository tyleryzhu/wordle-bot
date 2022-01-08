import discord
import random
from settings import MYTOKEN
from utils import WORDLEBANK

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
            f"You still have {self.turns} "
            + ("turn" if self.turns == 5 else "turns")
            + " left!",
        )

    def endGame(self):
        self.turns = 6
        return self.word

    def getHistory(self):
        return self.history

    def getLetters(self):
        return self.letters


class WordleClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.games = dict()

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    async def on_message(self, message):
        # don't respond to self
        if message.author == self.user:
            return
        guild = message.guild
        channel = message.channel
        # If a game currently exists in server
        if guild.id not in self.games:
            if message.content == "$start_standard":
                await message.channel.send("Starting standard game of Wordle...")
                word = random.choice(WORDS)

                host = self.user
                self.games[guild.id] = WordleGame(host, guild.name, channel.name, word)
                await message.channel.send(
                    "Send in a guess with $guess followed by your guess. You have 6 guesses."
                )
            elif message.content == "$start_custom":
                # TODO: add DM behavior
                await message.channel.send("Starting custom game of Wordle...")
                await message.channel.send(
                    "Choose a 5-letter word and DM the Bot with it."
                )
                host = message.author
        else:
            game = self.games[guild.id]
            if message.content == "$review":
                await message.channel.send("Your guesses so far are:")
                await message.channel.send(game.getHistory())
            elif message.content == "$letters":
                await message.channel.send("Your available letters are:")
                for k, v in game.getLetters().items():
                    if k == "open":
                        await message.channel.send(
                            f":white_circle: Open letters: {' '.join(v)}"
                        )
                    else:
                        await message.channel.send(
                            f":green_circle: Found letters: {' '.join(v)}"
                        )
            elif message.content == "$restart":
                await message.channel.send(f"Restarting... Word was {game.endGame()}")
                del self.games[guild.id]
            elif message.content.startswith("$guess"):
                guess = message.content.split()[1].strip().upper()
                print(f"Attempted guess in [{guild.name}] was {guess}")
                if len(guess) != 5:
                    await message.channel.send("Guess invalid, needs to be 5 letters.")
                    return
                if guess not in WORDS_SET:
                    await message.channel.send(
                        "Guess invalid, needs to be real 5 letter word."
                    )
                    return
                await message.channel.send(f"Your guess was: {guess}")
                guess_result, response = game.process_guess(guess)
                await message.channel.send(game.getHistory())
                await message.channel.send(response)
                if guess_result == -1 or guess_result == 1:
                    # Game over
                    del self.games[guild.id]
                return


client = WordleClient()
client.run(MYTOKEN)
