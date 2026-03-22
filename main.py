import discord
from discord.ext import commands

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

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
    print(f"✅ Bot is ONLINE as {bot.user}")

@bot.command(name="prices")
async def prices(ctx):
    """Show price menu"""
    embed = discord.Embed(title="📋 PRICE MENU", color=discord.Color.blue())
    embed.description = "React to see prices:\n1️⃣ Normal Prices\n2️⃣ Turf Prices\n3️⃣ Game & Links"
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")
    await msg.add_reaction("3️⃣")

@bot.command(name="1")
async def normal_prices(ctx):
    embed = discord.Embed(description=NORMAL_PRICES, color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command(name="2")
async def turf_prices(ctx):
    embed = discord.Embed(description=TURF_PRICES, color=discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command(name="3")
async def game_links(ctx):
    embed = discord.Embed(description=GAME_AND_LINKS, color=discord.Color.purple())
    await ctx.send(embed=embed)

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

bot.run("PASTE_YOUR_TOKEN_HERE")
