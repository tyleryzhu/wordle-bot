import random
from typing import List, Dict

import discord
from discord.abc import GuildChannel
from discord.ext import commands
from discord.guild import Guild
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
    def __init__(self, host: User, guild_name: str, base_channel: GuildChannel):
        self.host = host
        self.guild_name = guild_name
        self.base_channel = base_channel
        self.members = []
        self.magic = f"{host.name}'s party in [{guild_name}]"
        self.games = dict()
        self.channels = dict()
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

    def getGame(self, member: User) -> WordleGame:
        return self.games[member] if member in self.games else None

    def deleteGame(self, member: User):
        del self.games[member]

    def allGamesDone(self):
        return not self.games

    def addGame(self, game: WordleGame, member: User) -> bool:
        if member in self.members and member not in self.games:
            self.games[member] = game
            print(f"{self.magic} has added a game for {member.name}.")
            return True
        return False

    def getChannels(self) -> Dict[User, GuildChannel]:
        return self.channels

    def addChannel(self, member: User, channel: GuildChannel) -> bool:
        if member in self.members and member not in self.channels:
            self.channels[member] = channel
            print(f"{self.magic} has added channel [{channel.name}] for {member.name}.")
            return True
        return False

