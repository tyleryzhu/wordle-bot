import discord
from discord.abc import GuildChannel
from discord.ext import commands
from discord.commands import Option
from discord.user import User


from settings import MYTOKEN
from wordle_game import WordleGame, Party


class WordleBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.games = dict()  # contains either WordleGames or a Party of WordleGames

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        await self.change_presence(activity=discord.Game(name="Wordle! Use /start"))

    async def on_command_error(self, ctx, error):
        await ctx.send(f"Error: {error}")

    ## Custom functions
    def checkGame(self, guild_id: int, member: User = None):
        # Checks that a game/party exists for the guild
        if member is None:  # means checking for either party or a normal game
            return guild_id in self.games
        else:  # Check withiin a guild for a game
            if guild_id not in self.games or not isinstance(
                self.games[guild_id], Party
            ):
                return False
            return False if self.games[guild_id].getGame(member) is None else True

    def checkOpenParty(self, guild_id: int):
        """Check if guild has a party, and if it's open."""
        return (
            guild_id in self.games
            and isinstance(self.games[guild_id], Party)
            and self.games[guild_id].isPartyOpen()
        )

    def deleteGame(self, guild_id: int, member: User = None):
        # Only makes sense to delete the whole party together
        if self.checkGame(guild_id, member):
            del self.games[guild_id]
            return True
        return False

    def addGame(self, guild_id: int, game: WordleGame, member: User = None):
        if self.checkGame(guild_id, member):
            return False
        else:
            if member is None:
                self.games[guild_id] = game
                return True
            else:
                return self.games[guild_id].addGame(game, member)

    def getGame(self, guild_id: int, member: User = None):
        if self.checkGame(guild_id, member):
            if member is None:
                return self.games[guild_id]
            else:
                return self.games[guild_id].getGame(member)
        else:
            return None

    def isParty(self, guild_id: int):
        return isinstance(self.games[guild_id], Party)

    def addParty(
        self, guild_id: int, host: User, guild_name: str, base_channel: GuildChannel
    ) -> Party:
        if self.checkGame(guild_id):
            return False
        self.games[guild_id] = Party(host, guild_name, base_channel)
        print(f"Party in [{guild_name}] w/ host {host.name} added!")
        return self.games[guild_id]

