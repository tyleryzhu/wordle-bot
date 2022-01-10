import random
from typing import List

import discord
from discord.ext import commands
from discord.user import User

from utils import WORDLEBANK

WORDS = WORDLEBANK
WORDS_SET = set(WORDS)


class WordleGame:
    def __init__(self, host: User, guild_name: str, channel: str, word: str):
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

    def process_guess(self, guess: str):
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

    def getWord(self):
        return self.word

    def getHistory(self):
        if self.history == "":
            return "No guesses."
        return self.history

    def getLetters(self):
        return self.letters


class Party:
    def __init__(self, host: User, guild_name: str):
        self.host = host
        self.guild_name = guild_name
        self.members = []
        self.magic = f"{host.name}'s party in [{guild_name}]"
        self.games = dict()
        self.open = True

    def getMembers(self) -> List[User]:
        return self.members

    def addMember(self, member: User):
        if self.open:
            print(f"{member.name} has joined {self.magic}.")
            self.members.append(member)

    def removeMember(self, member: User):
        if self.open:
            print(f"{member.name} has left {self.magic}.")
            self.members.remove(member)

    def closeParty(self):
        print(f"{self.magic} has closed.")
        self.open = False

    def isPartyOpen(self) -> bool:
        return self.open

    def addGame(self, member: User, game: WordleGame) -> bool:
        if member in self.members and member.id not in self.games:
            self.games[member.id] = game
            print(f"{self.magic} has added a game for {member.name}.")
            return True
        return False

    def getGame(self, member: User) -> WordleGame:
        return self.games[member.id] if member.id in self.games else None
