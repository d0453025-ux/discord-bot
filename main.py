import discord
import os
from discord import app_commands

# Bot setup
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ⬇️ EASY TO EDIT - Your Prices ⬇️

NORMAL_PRICES = """
**🎮 NORMAL PRICES**
💰 100 Robux = $1.00
💰 500 Robux = $4.99
💰 1,000 Robux = $9.99
💰 2,500 Robux = $24.99
💰 10,000 Robux = $99.99
"""

TURF_PRICES = """
**🏘️ TURF PRICES**
🏠 Small Turf = 50,000 Robux
🏠 Medium Turf = 100,000 Robux
🏠 Large Turf = 250,000 Robux
🏠 Massive Turf = 500,000 Robux
"""

GAME_AND_LINKS = """
**🎯 GAME & LINKS**
🎮 Game Link: https://www.roblox.com/games/YOURGAMEID
👥 Roblox Group: https://www.roblox.com/groups/YOURGROUPID
🪙 Discord Server: https://discord.gg/YOURINVITECODE
"""

# ⬆️ EDIT ABOVE ⬆️

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot is ONLINE as {bot.user}")

@tree.command(name="prices", description="Show the price menu")
async def prices(interaction: discord.Interaction):
    embed = discord.Embed(title="📋 PRICE MENU", color=discord.Color.blue())
    embed.description = "React to see prices:\n1️⃣ Normal Prices\n2️⃣ Turf Prices\n3️⃣ Game & Links"
    msg = await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")

@tree.command(name="normal_prices", description="Show normal Robux prices")
async def normal_prices(interaction: discord.Interaction):
    embed = discord.Embed(description=NORMAL_PRICES, color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@tree.command(name="turf_prices", description="Show turf prices")
async def turf_prices(interaction: discord.Interaction):
    embed = discord.Embed(description=TURF_PRICES, color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)

@tree.command(name="game_links", description="Show game and links")
async def game_links(interaction: discord.Interaction):
    embed = discord.Embed(description=GAME_AND_LINKS, color=discord.Color.purple())
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if reaction.emoji == "1️⃣":
        embed = discord.Embed(description=NORMAL_PRICES, color=discord.Color.green())
        try:
            await user.send(embed=embed)
        except:
            pass
    elif reaction.emoji == "2️⃣":
        embed = discord.Embed(description=TURF_PRICES, color=discord.Color.orange())
        try:
            await user.send(embed=embed)
        except:
            pass
    elif reaction.emoji == "3️⃣":
        embed = discord.Embed(description=GAME_AND_LINKS, color=discord.Color.purple())
        try:
            await user.send(embed=embed)
        except:
            pass

token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("DISCORD_TOKEN environment variable is not set. Please add your Discord bot token as a secret.")
bot.run(token)
