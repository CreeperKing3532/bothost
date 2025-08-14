import discord
from discord.ext import commands
from discord import app_commands
import os

# ---------- BOT SETUP ----------
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# ---------- PREDEFINED MESSAGES ----------
# This dict maps input -> (private reply, public reply)
MESSAGES = {
    "hamster": (":3", "# I will crush your hamster"),
    "spawnism": (":3", "spawnism is a CULT, WOMP WOMP. LLLLLLLLLLL"),
    "raid2": (":3", "https://cdn.discordapp.com/attachments/1339637233711579228/1371261921751203920/furboy.gif\nhttps://cdn.discordapp.com/attachments/1098575467541446688/1254016158663708732/IMG_2452.gif\nhttps://cdn.discordapp.com/attachments/1354990400284266536/1385081101030129804/IMG_5451.gif"),
    "raid": (":3", "https://tenor.com/view/benjammins-brain-rot-brainrot-math-67-mango-mustard-67-mango-gif-7709692426775559134\nhttps://cdn.discordapp.com/attachments/1221118543567913103/1375386745750945832/attachment.gif\nhttps://tenor.com/view/rainbow-colorful-pattern-art-gif-17640961\nJOIN NOW FOR FREE MONEY\nSUBSCRIBE NOW FOR FREE MONEY\nhttps://youtube.com/@CoolGuyApple\nhttps://discord.gg/y9t3QTJuCh"),
    # Add more mappings here
}

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.tree.sync()
    print("🌐 Slash commands synced!")


# ---------- /lol COMMAND ----------
@bot.tree.command(
    name="lol",
    description="Send a predefined private and public message."
)
@app_commands.describe(message="The message keyword to look up")  # Argument description
async def lol(interaction: discord.Interaction, message: str):
    """
    Sends an ephemeral (private) message and a public message based on input.
    """
    # Convert input to lowercase to make matching case-insensitive
    key = message.lower()

    if key in MESSAGES:
        private_msg, public_msg = MESSAGES[key]
        # Send ephemeral/private message
        await interaction.response.send_message(private_msg, ephemeral=True)
        # Send public message as a followup
        await interaction.followup.send(public_msg)
    else:
        # Message not found
        await interaction.response.send_message(
            "ayo the fu is that? that aint a message, do /help",
            ephemeral=True
        )


# ---------- /help COMMAND ----------
@bot.tree.command(
    name="help",
    description="Shows the available lol messages."
)
async def help(interaction: discord.Interaction):
    """
    Ephemeral reply showing instructions / available keywords.
    """
    available = ", ".join(MESSAGES.keys())
    help_text = (
        "📜 **LOL Command Help**\n"
        f"Use `/lol message:<keyword>` to trigger messages.\n"
        f"Available keywords: {available}\n"
        "Example: `/lol message:test`"
    )
    await interaction.response.send_message(help_text, ephemeral=True)


# ---------- RUN BOT ----------
TOKEN = os.environ.get("NUKETOKEN")
if not TOKEN:
    raise ValueError("No token found! Set NUKETOKEN in environment variables.")

bot.run(TOKEN)
