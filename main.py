import discord
import os
import asyncio
import random
import time
import json
from datetime import datetime, timedelta
from discord import app_commands

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ⬇️ EASY TO EDIT - Staff Role Name ⬇️
# Users must have this role to use giveaway, poll, ban, and kick commands
STAFF_ROLE_NAME = "Hc/botacces"
# ⬆️ EDIT ABOVE ⬆️

def has_staff_role(interaction: discord.Interaction) -> bool:
    if isinstance(interaction.user, discord.Member):
        return any(r.name == STAFF_ROLE_NAME for r in interaction.user.roles)
    return False

# Warnings storage (resets on bot restart)
warnings_db = {}

# Bot start time for uptime tracking
START_TIME = None

# ========== DATABASE ==========
DATA_FILE = "data.json"

def get_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_tokens(user_id, amount):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"tokens": 0, "last_daily": None, "daily_streak": 0}
    data[uid]["tokens"] += amount
    save_data(data)

def remove_tokens(user_id, amount):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"tokens": 0, "last_daily": None, "daily_streak": 0}
    data[uid]["tokens"] = max(0, data[uid]["tokens"] - amount)
    save_data(data)

def get_tokens(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"tokens": 0, "last_daily": None, "daily_streak": 0}
        save_data(data)
    return data[uid].get("tokens", 0)

def set_daily(user_id, streak):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"tokens": 0, "last_daily": None, "daily_streak": 0}
    data[uid]["last_daily"] = datetime.now().isoformat()
    data[uid]["daily_streak"] = streak
    save_data(data)

def get_daily_streak(user_id):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        return 0
    last_daily = data[uid].get("last_daily")
    if not last_daily:
        return 0
    last_time = datetime.fromisoformat(last_daily)
    if datetime.now() - last_time < timedelta(days=1):
        return data[uid].get("daily_streak", 0)
    return 0

async def check_token_roles(member):
    tokens = get_tokens(member.id)
    guild = member.guild
    role_map = {
        1000000: "Rich MF",
        25000: "Daily Active",
        10000: "Rising",
        5000: "Just Starting"
    }
    for token_amount, role_name in role_map.items():
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            if tokens >= token_amount:
                if role not in member.roles:
                    try:
                        await member.add_roles(role)
                    except:
                        pass
            else:
                if role in member.roles:
                    try:
                        await member.remove_roles(role)
                    except:
                        pass

# 8Ball responses
EIGHT_BALL_RESPONSES = [
    "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.",
    "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
    "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.",
    "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.",
    "Don't count on it.", "My reply is no.", "My sources say no.",
    "Outlook not so good.", "Very doubtful."
]

# ⬇️ EASY TO EDIT - Your Prices ⬇️

NORMAL_PRICES = """
**🛒 SHOP — CUSTOM WEAPONS**
🔫 **Custom Draco** — 250 Robux
┣ 20 Base Spawns
┗ Name, Level, Laser/Glow Effects, Trails

🔫 **Custom SG** — 300 Robux
┣ 25 Base Spawns
┗ Name, Level, Laser/Glow Effects

🔫 **Custom Golden Gun** — 350 Robux
┣ 25 Base Spawns
┗ Name, Level, Laser/Glow Effects, Golden Finish

─────────────────────────
**🔧 BUNDLES & ADD-ONS**
📦 Custom Name + Level Bundle — 150 Robux
✨ Laser / Glow / Trail Effects — 100–150 Robux each
➕ Extra Spawns (+5) — 75 Robux (stackable up to 5x)

─────────────────────────
**💵 IN-GAME ITEMS**
💰 Small Cash (10k) — 50 Robux
💰 Medium Cash (25k) — 120 Robux 🔥 HOT DEAL
💰 Large Cash (50k) — 200 Robux ⭐ BEST VALUE
"""

TURF_PRICES = """
**🏟️ TURF TYPES & AVAILABILITY**
🏠 **Small Turf** — 300 Robux | 📦 5 Crates | 📊 5 Available
┗ 2 Rooms: 🛋️ Main Area, 📦 Crate Room

🏠 **Mid Turf** — 800 Robux | 📦 8 Crates | 📊 6 Available
┗ 4 Rooms: 🏋️ Training Area, 🛋️ Main Area, 🎨 Custom Room, 📦 Crate Room

🏢 **Big Turf** — 1,000 Robux | 📦 12 Crates | 📊 10 Available
┗ 2 Levels: 🚪 Entry, 📦 Crates, 🎨 Custom Room, 😌 Chill Room, 🏋️ Training, 🥊 Boxing Arena

─────────────────────────
🥊 **ARENA ROOM (Boxing / PvP)**
Supports 1v1, 2v2, etc.
Base Arena — 700 Robux
Add-ons: extra crates, decorations, visual effects

─────────────────────────
🚗 **CAR DISPLAY / SHOWROOM**
500–800 Robux per car slot
Includes: paint, decals, lights
Add-ons: neon underglow, custom rims, horn sounds

─────────────────────────
✨ **EXTRAS & ADD-ONS**
📦 Extra Crate — 100 Robux
🔤 Names on Walls — 25 Robux
🎨 Custom Room — 250 Robux
🎭 Special Turf Design / Theme — 150–300 Robux
🪴 Extra Decorations — 50–150 Robux
💨 Animated Effects (smoke, sparkles) — 75–200 Robux
🎵 Exclusive Turf Music — 100–150 Robux
🪧 Custom Turf Nameplate — 50–100 Robux
📦 Extra Storage / Expansion Slot — 100–200 Robux
"""

GAME_AND_LINKS = """
### 🎯 GAME & LINKS

### 🎮 [Roblox Game](https://www.roblox.com/share?code=2ee1ff592f4e4843b7c6390da0f61844&type=ExperienceDetails&stamp=1771789166361)

### 👥 [Roblox Group](https://www.roblox.com/share/g/628331601)

### 🪙 [Discord Server](https://discord.gg/rpC8RahxHs)
"""

# ⬆️ EDIT ABOVE ⬆️

@bot.event
async def on_ready():
    global START_TIME
    START_TIME = time.time()
    await tree.sync()
    print(f"✅ Bot is ONLINE as {bot.user}")

@tree.command(name="prices", description="Show the price menu")
async def prices(interaction: discord.Interaction):
    embed = discord.Embed(title="📋 PRICE MENU", color=discord.Color(0x808080))
    embed.description = "React to see prices:\n1️⃣ Normal Prices\n2️⃣ Turf Prices\n3️⃣ Game & Links"
    msg = await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")

@tree.command(name="shop", description="Show the shop with custom weapons and in-game items")
async def normal_prices(interaction: discord.Interaction):
    embed = discord.Embed(description=NORMAL_PRICES, color=discord.Color(0x808080))
    await interaction.response.send_message(embed=embed)

@tree.command(name="turf_prices", description="Show turf prices")
async def turf_prices(interaction: discord.Interaction):
    embed = discord.Embed(description=TURF_PRICES, color=discord.Color(0x808080))
    await interaction.response.send_message(embed=embed)

@tree.command(name="game_links", description="Show game and links")
async def game_links(interaction: discord.Interaction):
    embed = discord.Embed(description=GAME_AND_LINKS, color=discord.Color(0x808080))
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if reaction.emoji == "1️⃣":
        embed = discord.Embed(description=NORMAL_PRICES, color=discord.Color(0x808080))
        try:
            await user.send(embed=embed)
        except:
            pass
    elif reaction.emoji == "2️⃣":
        embed = discord.Embed(description=TURF_PRICES, color=discord.Color(0x808080))
        try:
            await user.send(embed=embed)
        except:
            pass
    elif reaction.emoji == "3️⃣":
        embed = discord.Embed(description=GAME_AND_LINKS, color=discord.Color(0x808080))
        try:
            await user.send(embed=embed)
        except:
            pass

@tree.command(name="poll", description="Create a poll (Staff only)")
@app_commands.describe(
    question="What is the poll question?",
    option1="First option",
    option2="Second option",
    option3="Third option (optional)",
    option4="Fourth option (optional)"
)
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    options = [option1, option2]
    if option3:
        options.append(option3)
    if option4:
        options.append(option4)

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    description = f"**{question}**\n\n"
    for i, option in enumerate(options):
        description += f"{emojis[i]} {option}\n"

    embed = discord.Embed(
        title="📊 POLL",
        description=description,
        color=discord.Color(0x808080)
    )
    embed.set_footer(text=f"Poll by {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    for i in range(len(options)):
        await message.add_reaction(emojis[i])

@tree.command(name="kick", description="Kick a member (Staff only)")
@app_commands.describe(member="The member to kick", reason="Reason for kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.kick_members:
        await interaction.response.send_message("❌ I don't have permission to kick members.", ephemeral=True)
        return
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Member Kicked",
            description=f"**{member}** has been kicked.\n**Reason:** {reason}",
            color=discord.Color(0x808080)
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't kick that member. They may have a higher role than me.", ephemeral=True)

@tree.command(name="ban", description="Ban a member (Staff only)")
@app_commands.describe(member="The member to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ I don't have permission to ban members.", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"**{member}** has been banned.\n**Reason:** {reason}",
            color=discord.Color(0x808080)
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't ban that member. They may have a higher role than me.", ephemeral=True)

@tree.command(name="giveaway", description="Start a giveaway (Staff only)")
@app_commands.describe(
    prize="What are you giving away?",
    minutes="How long should the giveaway last (in minutes)?",
    winners="How many winners? (default: 1)"
)
async def giveaway(interaction: discord.Interaction, prize: str, minutes: int, winners: int = 1):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    end_time = discord.utils.utcnow().timestamp() + (minutes * 60)

    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Prize:** {prize}\n\nReact with 🎉 to enter!\n\n**Winners:** {winners}\n**Ends:** <t:{int(end_time)}:R>",
        color=discord.Color(0x808080)
    )
    embed.set_footer(text=f"Hosted by {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("🎉")

    await asyncio.sleep(minutes * 60)

    message = await interaction.channel.fetch_message(message.id)
    reaction = discord.utils.get(message.reactions, emoji="🎉")

    if reaction is None or reaction.count <= 1:
        await interaction.channel.send("❌ Not enough people entered the giveaway!")
        return

    users = [u async for u in reaction.users() if not u.bot]

    if len(users) < winners:
        winners = len(users)

    picked = random.sample(users, winners)
    winner_mentions = ", ".join(w.mention for w in picked)

    result_embed = discord.Embed(
        title="🎉 GIVEAWAY ENDED 🎉",
        description=f"**Prize:** {prize}\n\n🏆 **Winner(s):** {winner_mentions}\n\nCongratulations!",
        color=discord.Color(0x808080)
    )
    await interaction.channel.send(embed=result_embed)
    await interaction.channel.send(f"🎉 Congrats {winner_mentions}! You won **{prize}**!")

# ── SERVER INFO ──────────────────────────────────────────────────────────────

@tree.command(name="serverinfo", description="Show server information")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color(0x808080))
    embed.add_field(name="👥 Members", value=guild.member_count)
    embed.add_field(name="📅 Created", value=f"<t:{int(guild.created_at.timestamp())}:D>")
    embed.add_field(name="👑 Owner", value=f"<@{guild.owner_id}>")
    embed.add_field(name="🎭 Roles", value=len(guild.roles))
    embed.add_field(name="💬 Channels", value=len(guild.channels))
    embed.add_field(name="🌍 Region", value="Automatic")
    await interaction.response.send_message(embed=embed)

@tree.command(name="roleinfo", description="Show info about a role")
@app_commands.describe(role="The role to look up")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    embed = discord.Embed(title=f"🎭 {role.name}", color=role.color)
    embed.add_field(name="🎨 Color", value=str(role.color))
    embed.add_field(name="📌 Mentionable", value="Yes" if role.mentionable else "No")
    embed.add_field(name="🔼 Hoisted", value="Yes" if role.hoist else "No")
    embed.add_field(name="📊 Position", value=role.position)
    embed.add_field(name="🆔 ID", value=role.id)
    embed.add_field(name="📅 Created", value=f"<t:{int(role.created_at.timestamp())}:D>")
    await interaction.response.send_message(embed=embed)

@tree.command(name="userinfo", description="Show info about a user")
@app_commands.describe(member="The member to look up (leave empty for yourself)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    embed = discord.Embed(title=f"👤 {member}", color=discord.Color(0x808080))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=member.id)
    embed.add_field(name="📅 Joined Server", value=f"<t:{int(member.joined_at.timestamp())}:D>")
    embed.add_field(name="🎂 Account Created", value=f"<t:{int(member.created_at.timestamp())}:D>")
    embed.add_field(name="🎭 Roles", value=", ".join(roles) if roles else "None", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="roles", description="List all roles in the server")
async def roles(interaction: discord.Interaction):
    guild = interaction.guild
    role_list = [r.mention for r in reversed(guild.roles) if r.name != "@everyone"]
    embed = discord.Embed(
        title=f"🎭 Roles in {guild.name}",
        description="\n".join(role_list) if role_list else "No roles",
        color=discord.Color(0x808080)
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="invites", description="Show server invites")
async def invites(interaction: discord.Interaction):
    try:
        server_invites = await interaction.guild.invites()
        if not server_invites:
            await interaction.response.send_message("No active invites found.", ephemeral=True)
            return
        lines = [f"🔗 `{inv.code}` — by {inv.inviter.mention if inv.inviter else 'Unknown'} — **{inv.uses}** uses" for inv in server_invites]
        embed = discord.Embed(title="📨 Server Invites", description="\n".join(lines), color=discord.Color(0x808080))
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I need **Manage Guild** permission to view invites.", ephemeral=True)

# ── FUN COMMANDS ──────────────────────────────────────────────────────────────

@tree.command(name="8ball", description="Ask the magic 8 ball a question")
@app_commands.describe(question="Your yes/no question")
async def eightball(interaction: discord.Interaction, question: str):
    response = random.choice(EIGHT_BALL_RESPONSES)
    embed = discord.Embed(title="🎱 Magic 8 Ball", color=discord.Color(0x808080))
    embed.add_field(name="❓ Question", value=question, inline=False)
    embed.add_field(name="💬 Answer", value=response, inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="dice", description="Roll a dice (1–6)")
async def dice(interaction: discord.Interaction):
    result = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 You rolled a **{result}**!")

@tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 It's **{result}**!")

@tree.command(name="rps", description="Play Rock Paper Scissors against the bot")
@app_commands.describe(choice="rock, paper, or scissors")
async def rps(interaction: discord.Interaction, choice: str):
    choices = ["rock", "paper", "scissors"]
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    choice = choice.lower()
    if choice not in choices:
        await interaction.response.send_message("❌ Choose **rock**, **paper**, or **scissors**.", ephemeral=True)
        return
    bot_choice = random.choice(choices)
    if choice == bot_choice:
        result = "It's a **tie**! 🤝"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):
        result = "You **win**! 🎉"
    else:
        result = "You **lose**! 😔"
    await interaction.response.send_message(f"You: {emojis[choice]}  vs  Bot: {emojis[bot_choice]}\n{result}")

@tree.command(name="say", description="Make the bot say something (Staff only)")
@app_commands.describe(message="What should the bot say?")
async def say(interaction: discord.Interaction, message: str):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    await interaction.response.send_message("✅ Sent!", ephemeral=True)
    await interaction.channel.send(message)

# ── MODERATION (extra) ────────────────────────────────────────────────────────

@tree.command(name="mute", description="Timeout (mute) a member (Staff only)")
@app_commands.describe(member="Member to mute", minutes="Duration in minutes (default 10)")
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int = 10):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role.", ephemeral=True)
        return
    try:
        until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
        await member.timeout(until, reason=f"Muted by {interaction.user}")
        embed = discord.Embed(title="🔇 Member Muted", description=f"**{member}** has been muted for **{minutes} minute(s)**.", color=discord.Color(0x808080))
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to timeout that member.", ephemeral=True)

@tree.command(name="unmute", description="Remove timeout from a member (Staff only)")
@app_commands.describe(member="Member to unmute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role.", ephemeral=True)
        return
    try:
        await member.timeout(None, reason=f"Unmuted by {interaction.user}")
        embed = discord.Embed(title="🔊 Member Unmuted", description=f"**{member}** has been unmuted.", color=discord.Color(0x808080))
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to unmute that member.", ephemeral=True)

@tree.command(name="warn", description="Warn a member (Staff only)")
@app_commands.describe(member="Member to warn", reason="Reason for the warning")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role.", ephemeral=True)
        return
    if member.id not in warnings_db:
        warnings_db[member.id] = []
    warnings_db[member.id].append({"reason": reason, "moderator": str(interaction.user)})
    count = len(warnings_db[member.id])
    embed = discord.Embed(
        title="⚠️ Member Warned",
        description=f"**{member}** has been warned.\n**Reason:** {reason}\n**Total warnings:** {count}",
        color=discord.Color(0x808080)
    )
    await interaction.response.send_message(embed=embed)
    try:
        await member.send(f"⚠️ You have been warned in **{interaction.guild.name}**.\n**Reason:** {reason}\n**Total warnings:** {count}")
    except:
        pass

@tree.command(name="warnings", description="Check a member's warnings (Staff only)")
@app_commands.describe(member="Member to check")
async def check_warnings(interaction: discord.Interaction, member: discord.Member):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role.", ephemeral=True)
        return
    user_warns = warnings_db.get(member.id, [])
    if not user_warns:
        await interaction.response.send_message(f"✅ **{member}** has no warnings.", ephemeral=True)
        return
    lines = [f"{i+1}. {w['reason']} — by {w['moderator']}" for i, w in enumerate(user_warns)]
    embed = discord.Embed(title=f"⚠️ Warnings for {member}", description="\n".join(lines), color=discord.Color(0x808080))
    await interaction.response.send_message(embed=embed)

# ── HELP / INFO ───────────────────────────────────────────────────────────────

@tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 BOT COMMANDS", color=discord.Color(0x808080))
    embed.add_field(name="💰 Price Commands", value="`/prices` `/shop` `/turf_prices` `/game_links`", inline=False)
    embed.add_field(name="📊 Server Info", value="`/serverinfo` `/roleinfo` `/userinfo` `/roles` `/invites`", inline=False)
    embed.add_field(name="🎮 Fun", value="`/8ball` `/dice` `/coinflip` `/rps` `/say`", inline=False)
    embed.add_field(name="🏷️ Personal Prefix", value="`/setprefix` `/myprefix` `/checkprefix` `/removeprefix`", inline=False)
    embed.add_field(name="🪙 Tokens", value="`/beg` `/daily` `/roll` `/steal` `/balance` `/tokens_leaderboard` `/invites_leaderboard`", inline=False)
    embed.add_field(name="🛡️ Moderation (Staff only)", value="`/kick` `/ban` `/mute` `/unmute` `/warn` `/warnings` `/giveaway` `/poll`", inline=False)
    embed.add_field(name="❓ Info", value="`/help` `/ping` `/botinfo`", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ping", description="Check the bot's response speed")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: **{latency}ms**")

@tree.command(name="botinfo", description="Show bot information")
async def botinfo(interaction: discord.Interaction):
    uptime_seconds = int(time.time() - START_TIME) if START_TIME else 0
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    embed = discord.Embed(title="🤖 Bot Info", color=discord.Color(0x808080))
    embed.add_field(name="🤖 Name", value=str(bot.user))
    embed.add_field(name="⏱️ Uptime", value=uptime_str)
    embed.add_field(name="🌍 Servers", value=len(bot.guilds))
    embed.add_field(name="📡 Latency", value=f"{round(bot.latency * 1000)}ms")
    await interaction.response.send_message(embed=embed)

# ── PERSONAL PREFIX ───────────────────────────────────────────────────────────

def get_prefix(user_id):
    data = get_data()
    return data.get(str(user_id), {}).get("prefix", None)

def save_prefix(user_id, prefix):
    data = get_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"tokens": 0, "last_daily": None, "daily_streak": 0}
    data[uid]["prefix"] = prefix
    save_data(data)

def delete_prefix(user_id):
    data = get_data()
    uid = str(user_id)
    if uid in data and "prefix" in data[uid]:
        del data[uid]["prefix"]
        save_data(data)

@tree.command(name="setprefix", description="Set your personal prefix (e.g. Hc, Ez)")
@app_commands.describe(prefix="Your personal prefix tag")
async def setprefix(interaction: discord.Interaction, prefix: str):
    if len(prefix) > 10:
        await interaction.response.send_message("❌ Prefix must be 10 characters or less.", ephemeral=True)
        return
    save_prefix(interaction.user.id, prefix)
    member = interaction.user
    if isinstance(member, discord.Member):
        base_name = member.display_name
        # Strip existing prefix if present (format: "tag | name")
        if " | " in base_name:
            base_name = base_name.split(" | ", 1)[1]
        new_nick = f"{prefix} | {base_name}"
        try:
            await member.edit(nick=new_nick)
        except discord.Forbidden:
            pass
    embed = discord.Embed(
        description=f"✅ Your personal prefix has been set to **{prefix}**!",
        color=discord.Color(0x808080)
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="myprefix", description="Check your personal prefix")
async def myprefix(interaction: discord.Interaction):
    prefix = get_prefix(interaction.user.id)
    if not prefix:
        await interaction.response.send_message("❌ You don't have a personal prefix set. Use `/setprefix` to set one.", ephemeral=True)
        return
    embed = discord.Embed(
        description=f"🏷️ Your personal prefix is **{prefix}**",
        color=discord.Color(0x808080)
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="checkprefix", description="Check someone else's personal prefix")
@app_commands.describe(member="The member to check")
async def checkprefix(interaction: discord.Interaction, member: discord.Member):
    prefix = get_prefix(member.id)
    if not prefix:
        await interaction.response.send_message(f"❌ **{member.display_name}** doesn't have a personal prefix set.", ephemeral=True)
        return
    embed = discord.Embed(
        description=f"🏷️ **{member.display_name}**'s personal prefix is **{prefix}**",
        color=discord.Color(0x808080)
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="removeprefix", description="Remove your personal prefix (Staff can remove anyone's)")
@app_commands.describe(member="Member to remove prefix from (Staff only, leave empty for yourself)")
async def removeprefix(interaction: discord.Interaction, member: discord.Member = None):
    if member and member.id != interaction.user.id:
        if not has_staff_role(interaction):
            await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to remove someone else's prefix.", ephemeral=True)
            return
    target = member or interaction.user
    delete_prefix(target.id)
    if isinstance(target, discord.Member):
        base_name = target.display_name
        if " | " in base_name:
            base_name = base_name.split(" | ", 1)[1]
        try:
            await target.edit(nick=base_name if base_name != target.name else None)
        except discord.Forbidden:
            pass
    await interaction.response.send_message(f"✅ Prefix removed for **{target.display_name}**.", ephemeral=True)

# ── TOKEN ECONOMY ─────────────────────────────────────────────────────────────

@tree.command(name="beg", description="Beg for some tokens")
async def beg(interaction: discord.Interaction):
    amount = random.randint(50, 500)
    add_tokens(interaction.user.id, amount)
    if isinstance(interaction.user, discord.Member):
        await check_token_roles(interaction.user)
    embed = discord.Embed(
        description=f"🎁 {interaction.user.mention} begged and got **{amount}** tokens!",
        color=discord.Color(0x808080)
    )
    embed.set_footer(text=f"Total: {get_tokens(interaction.user.id)} tokens")
    await interaction.response.send_message(embed=embed)

@tree.command(name="daily", description="Claim your daily token reward")
async def daily(interaction: discord.Interaction):
    streak = get_daily_streak(interaction.user.id)
    if streak > 0:
        await interaction.response.send_message("❌ You already claimed your daily! Come back tomorrow.", ephemeral=True)
        return
    new_streak = streak + 1
    amount = 100 + (new_streak - 1)
    add_tokens(interaction.user.id, amount)
    set_daily(interaction.user.id, new_streak)
    if isinstance(interaction.user, discord.Member):
        await check_token_roles(interaction.user)
    embed = discord.Embed(
        description=f"📅 {interaction.user.mention} claimed daily reward! **{amount}** tokens",
        color=discord.Color(0x808080)
    )
    embed.add_field(name="Streak", value=f"🔥 {new_streak} day(s)", inline=False)
    embed.set_footer(text=f"Total: {get_tokens(interaction.user.id)} tokens")
    await interaction.response.send_message(embed=embed)

@tree.command(name="roll", description="Gamble your tokens (50/50)")
@app_commands.describe(bet="Amount of tokens to bet")
async def roll(interaction: discord.Interaction, bet: int):
    tokens = get_tokens(interaction.user.id)
    if bet <= 0:
        await interaction.response.send_message("❌ Bet must be more than 0!", ephemeral=True)
        return
    if tokens < bet:
        await interaction.response.send_message(f"❌ You don't have enough tokens! You have **{tokens}**.", ephemeral=True)
        return
    result = random.choice([True, False])
    if result:
        add_tokens(interaction.user.id, bet)
        embed = discord.Embed(description=f"🎲 {interaction.user.mention} **WON!** +**{bet}** tokens!", color=discord.Color(0x808080))
    else:
        remove_tokens(interaction.user.id, bet)
        embed = discord.Embed(description=f"🎲 {interaction.user.mention} **LOST!** -{bet} tokens!", color=discord.Color(0x808080))
    embed.set_footer(text=f"Total: {get_tokens(interaction.user.id)} tokens")
    await interaction.response.send_message(embed=embed)
    if isinstance(interaction.user, discord.Member):
        await check_token_roles(interaction.user)

@tree.command(name="steal", description="Try to steal tokens from someone (need 5,000+, 40% success)")
@app_commands.describe(member="Who to steal from")
async def steal(interaction: discord.Interaction, member: discord.Member):
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You can't steal from yourself!", ephemeral=True)
        return
    tokens = get_tokens(interaction.user.id)
    if tokens < 5000:
        await interaction.response.send_message(f"❌ You need at least **5,000** tokens to steal! You have {tokens}.", ephemeral=True)
        return
    if random.randint(1, 100) <= 40:
        amount = random.randint(10, 200)
        remove_tokens(member.id, amount)
        add_tokens(interaction.user.id, amount)
        embed = discord.Embed(
            description=f"🔓 {interaction.user.mention} successfully stole **{amount}** tokens from {member.mention}!",
            color=discord.Color(0x808080)
        )
    else:
        embed = discord.Embed(
            description=f"🔒 {interaction.user.mention} tried to steal but **FAILED!** {member.mention} caught them!",
            color=discord.Color(0x808080)
        )
    await interaction.response.send_message(embed=embed)
    if isinstance(interaction.user, discord.Member):
        await check_token_roles(interaction.user)

@tree.command(name="balance", description="Check your token balance (or someone else's)")
@app_commands.describe(member="Member to check (leave empty for yourself)")
async def balance(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    tokens = get_tokens(member.id)
    embed = discord.Embed(
        description=f"💰 {member.mention} has **{tokens}** tokens",
        color=discord.Color(0x808080)
    )
    await interaction.response.send_message(embed=embed)

# ── LEADERBOARDS ──────────────────────────────────────────────────────────────

@tree.command(name="tokens_leaderboard", description="Show the top token earners")
async def tokens_leaderboard(interaction: discord.Interaction):
    data = get_data()
    if not data:
        await interaction.response.send_message("❌ No data yet!", ephemeral=True)
        return
    sorted_users = sorted(data.items(), key=lambda x: x[1].get("tokens", 0), reverse=True)[:10]
    lines = [f"{i+1}. <@{uid}> — **{udata.get('tokens', 0)}** tokens" for i, (uid, udata) in enumerate(sorted_users)]
    embed = discord.Embed(title="💰 TOKEN LEADERBOARD", description="\n".join(lines), color=discord.Color(0x808080))
    await interaction.response.send_message(embed=embed)

@tree.command(name="invites_leaderboard", description="Show the top inviters")
async def invites_leaderboard(interaction: discord.Interaction):
    try:
        server_invites = await interaction.guild.invites()
    except discord.Forbidden:
        await interaction.response.send_message("❌ I need **Manage Guild** permission to view invites.", ephemeral=True)
        return
    invite_data = {}
    for inv in server_invites:
        if inv.inviter:
            invite_data[inv.inviter.id] = invite_data.get(inv.inviter.id, 0) + inv.uses
    if not invite_data:
        await interaction.response.send_message("❌ No invites yet!", ephemeral=True)
        return
    sorted_inviters = sorted(invite_data.items(), key=lambda x: x[1], reverse=True)[:10]
    lines = [f"{i+1}. <@{uid}> — **{count}** invites" for i, (uid, count) in enumerate(sorted_inviters)]
    embed = discord.Embed(title="👥 INVITES LEADERBOARD", description="\n".join(lines), color=discord.Color(0x808080))
    await interaction.response.send_message(embed=embed)

# ── MEMBER JOIN (invite role tracking) ───────────────────────────────────────

@bot.event
async def on_member_join(member):
    await asyncio.sleep(1)
    guild = member.guild
    invite_data = {}
    try:
        server_invites = await guild.invites()
        for inv in server_invites:
            if inv.inviter:
                invite_data[inv.inviter.id] = invite_data.get(inv.inviter.id, 0) + inv.uses
    except:
        return
    invite_roles = {
        100: 1483938598050070712,
        50: 1483938384132051186,
        30: 1483937935391850496,
        20: 1483937466560806943,
        12: 1483936757023117452,
        6: 1449371784037142609,
        3: 1449371710368256172,
    }
    for inviter_id, invite_count in invite_data.items():
        inviter = guild.get_member(inviter_id)
        if not inviter:
            continue
        for threshold, role_id in sorted(invite_roles.items(), reverse=True):
            if invite_count >= threshold:
                role = guild.get_role(role_id)
                if role and role not in inviter.roles:
                    try:
                        await inviter.add_roles(role)
                    except:
                        pass
                break

# ── PERSONAL PREFIX COMMAND HANDLER ───────────────────────────────────────────

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_prefix = get_prefix(message.author.id)
    if not user_prefix:
        return

    content = message.content.strip()
    prefix_lower = user_prefix.lower()
    content_lower = content.lower()

    # Must start with their prefix followed by a space
    if not content_lower.startswith(prefix_lower + " "):
        return

    args = content[len(user_prefix):].strip().split()
    if not args:
        return

    cmd = args[0].lower()
    member = message.author

    # beg
    if cmd == "beg":
        amount = random.randint(50, 500)
        add_tokens(member.id, amount)
        if isinstance(member, discord.Member):
            await check_token_roles(member)
        embed = discord.Embed(
            description=f"🎁 {member.mention} begged and got **{amount}** tokens!",
            color=discord.Color(0x808080)
        )
        embed.set_footer(text=f"Total: {get_tokens(member.id)} tokens")
        await message.channel.send(embed=embed)

    # daily
    elif cmd == "daily":
        streak = get_daily_streak(member.id)
        if streak > 0:
            await message.channel.send(f"❌ {member.mention} You already claimed your daily! Come back tomorrow.")
            return
        new_streak = streak + 1
        amount = 100 + (new_streak - 1)
        add_tokens(member.id, amount)
        set_daily(member.id, new_streak)
        if isinstance(member, discord.Member):
            await check_token_roles(member)
        embed = discord.Embed(
            description=f"📅 {member.mention} claimed daily reward! **{amount}** tokens",
            color=discord.Color(0x808080)
        )
        embed.add_field(name="Streak", value=f"🔥 {new_streak} day(s)", inline=False)
        embed.set_footer(text=f"Total: {get_tokens(member.id)} tokens")
        await message.channel.send(embed=embed)

    # roll
    elif cmd == "roll":
        if len(args) < 2 or not args[1].isdigit():
            await message.channel.send(f"❌ Usage: `{user_prefix} roll <amount>`")
            return
        bet = int(args[1])
        tokens = get_tokens(member.id)
        if bet <= 0:
            await message.channel.send("❌ Bet must be more than 0!")
            return
        if tokens < bet:
            await message.channel.send(f"❌ You only have **{tokens}** tokens!")
            return
        if random.choice([True, False]):
            add_tokens(member.id, bet)
            embed = discord.Embed(description=f"🎲 {member.mention} **WON!** +**{bet}** tokens!", color=discord.Color(0x808080))
        else:
            remove_tokens(member.id, bet)
            embed = discord.Embed(description=f"🎲 {member.mention} **LOST!** -{bet} tokens!", color=discord.Color(0x808080))
        embed.set_footer(text=f"Total: {get_tokens(member.id)} tokens")
        await message.channel.send(embed=embed)
        if isinstance(member, discord.Member):
            await check_token_roles(member)

    # balance
    elif cmd in ("balance", "bal"):
        target = message.mentions[0] if message.mentions else member
        tokens = get_tokens(target.id)
        embed = discord.Embed(
            description=f"💰 {target.mention} has **{tokens}** tokens",
            color=discord.Color(0x808080)
        )
        await message.channel.send(embed=embed)

    # steal
    elif cmd == "steal":
        if not message.mentions:
            await message.channel.send(f"❌ Usage: `{user_prefix} steal @user`")
            return
        target = message.mentions[0]
        if target.id == member.id:
            await message.channel.send("❌ You can't steal from yourself!")
            return
        tokens = get_tokens(member.id)
        if tokens < 5000:
            await message.channel.send(f"❌ You need at least **5,000** tokens to steal! You have {tokens}.")
            return
        if random.randint(1, 100) <= 40:
            amount = random.randint(10, 200)
            remove_tokens(target.id, amount)
            add_tokens(member.id, amount)
            embed = discord.Embed(
                description=f"🔓 {member.mention} stole **{amount}** tokens from {target.mention}!",
                color=discord.Color(0x808080)
            )
        else:
            embed = discord.Embed(
                description=f"🔒 {member.mention} tried to steal but **FAILED!** {target.mention} caught them!",
                color=discord.Color(0x808080)
            )
        await message.channel.send(embed=embed)

    # prefix (show your own)
    elif cmd == "prefix":
        await message.channel.send(f"🏷️ {member.mention} Your personal prefix is **{user_prefix}**")

    # help
    elif cmd == "help":
        embed = discord.Embed(title=f"📖 {user_prefix} COMMANDS", color=discord.Color(0x808080))
        embed.add_field(name="Token Commands", value=f"`{user_prefix} beg`\n`{user_prefix} daily`\n`{user_prefix} roll <amount>`\n`{user_prefix} steal @user`\n`{user_prefix} balance`", inline=False)
        embed.add_field(name="Other", value=f"`{user_prefix} prefix` — show your prefix\n`{user_prefix} help` — show this menu", inline=False)
        await message.channel.send(embed=embed)

token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("DISCORD_TOKEN environment variable is not set. Please add your Discord bot token as a secret.")
bot.run(token)
