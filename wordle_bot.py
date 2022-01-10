import discord
from discord.mentions import A
from discord.ext import commands
from discord.commands import Option


from settings import MYTOKEN
from wordle_game import WordleGame


class WordleBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.games = dict()

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        await self.change_presence(activity=discord.Game(name="Wordle! Use /start"))

    async def on_command_error(self, ctx, error):
        await ctx.send(f"Error: {error}")

    ## Custom functions
    async def checkGame(self, guild_id: int):
        return guild_id in self.games

    async def deleteGame(self, guild_id: int):
        if await self.checkGame(guild_id):
            del self.games[guild_id]
            return True
        return False

    async def addGame(self, guild_id: int, game: WordleGame):
        if await self.checkGame(guild_id):
            return False
        else:
            self.games[guild_id] = game
            return True

    async def getGame(self, guild_id: int):
        if await self.checkGame(guild_id):
            return self.games[guild_id]
        else:
            return None
