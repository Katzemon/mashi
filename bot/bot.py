import discord
from discord.ext import commands

from bot.message_module import get_notify_embed
from config.config import RELEASES_CHANNEL_ID, TEST_CHANNEL_ID, NEW_RELEASES_ROLE_ID


class MashiBot(commands.Bot):
    _instance = None

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        MashiBot._instance = self


    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = MashiBot()
        return cls._instance


    async def release_notify(self, data: dict):
        try:
            if not dict:
                return

            embed = get_notify_embed(data)
            channel = self.instance().get_channel(RELEASES_CHANNEL_ID)
            role = channel.guild.get_role(NEW_RELEASES_ROLE_ID)
            await channel.send(f"{role.mention}", embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))
        except Exception as e:
            channel = self.instance().get_channel(TEST_CHANNEL_ID)
            await channel.send(f"Notify: {e} for {data}")


    async def setup_hook(self):
        await self.load_extension("bot.mashi_module")
        await self.tree.sync()
