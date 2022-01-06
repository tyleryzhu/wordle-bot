from re import A
import discord
import random
from settings import MYTOKEN
from utils import WORDLEBANK

WORDS = WORDLEBANK
WORDS_SET = set(WORDS)

# TODO: implement living keyboard


class WordleClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_started = False

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    async def on_message(self, message):
        # don't respond to self
        if message.author == self.user:
            return

        # If no current game, start one
        if not self.game_started:
            if message.content == "$start_standard":
                await message.channel.send("Starting standard game of Wordle...")
                host = self.user
                word = random.choice(WORDS)
                self.initialize_game(host, word)
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
            if message.content == "$review":
                await message.channel.send("Your guesses so far are:")
                await message.channel.send(self.history)
            elif message.content.startswith("$guess"):
                guess = message.content.split()[1].strip().upper()
                print(f"Attempted guess was {guess}")
                if len(guess) != 5:
                    await message.channel.send("Guess invalid, needs to be 5 letters.")
                    return
                if guess not in WORDS_SET:
                    await message.channel.send(
                        "Guess invalid, needs to be real 5 letter word."
                    )
                    return
                await message.channel.send(f"Your guess was: {guess}")
                guess_result = self.process_guess(guess)
                await message.channel.send(self.history)
                if guess_result == -1:
                    await message.channel.send(f"You lost! The word was {self.word}.")
                    self.game_started = False
                elif guess_result == 1:
                    await message.channel.send(f"You won in {self.turns} turns!")
                    self.game_started = False
                else:
                    if self.turns == 5:
                        await message.channel.send(
                            f"You still have {6 - self.turns} turn left!"
                        )
                    else:
                        await message.channel.send(
                            f"You still have {6 - self.turns} turns left!"
                        )
                return

        # Behavior for current games

    def initialize_game(self, host, word):
        self.game_started = True
        self.host = host
        self.word = word
        self.turns = 0
        self.history = ""
        print(f"Game started by {host} with word {word}.")

    def process_guess(self, guess):
        out_string = ""

        # Make a pretty history first
        for i in range(5):
            out_string += f":regional_indicator_{guess[i].lower()}: "
        out_string += "\n"

        for i in range(5):
            if guess[i] == self.word[i]:
                out_string += ":green_circle:"
            elif guess[i] in self.word:
                out_string += ":yellow_circle:"
            else:
                out_string += ":black_circle:"
        out_string += "\n"
        print(out_string)
        self.history += out_string
        self.turns += 1
        if guess == self.word:
            return 1  # win
        if self.turns == 6:
            return -1  # loss
        return 0  # game continues


client = WordleClient()
client.run(MYTOKEN)
