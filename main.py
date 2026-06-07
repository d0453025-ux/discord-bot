import discord
import os
import asyncio
import random
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import datetime
from discord import app_commands

# ── KEEP-ALIVE SERVER (satisfies Replit deployment health check) ───────────────
class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hood Conflict Bot is running!")
    def log_message(self, *args):
        pass  # silence request logs

def _run_health_server():
    server = HTTPServer(("0.0.0.0", 8080), _HealthHandler)
    server.serve_forever()

threading.Thread(target=_run_health_server, daemon=True).start()
# ──────────────────────────────────────────────────────────────────────────────

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

# ⬇️ SET YOUR DISCORD USER ID HERE (right-click yourself → Copy User ID) ⬇️
OWNER_ID = 1262338624402493460
# ⬆️ EDIT ABOVE ⬆️

def has_staff_role(interaction: discord.Interaction) -> bool:
    if isinstance(interaction.user, discord.Member):
        return any(r.name == STAFF_ROLE_NAME for r in interaction.user.roles)
    return False

# Warnings storage (resets on bot restart)
warnings_db = {}

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
🏠 **Small Turf** — 🆓 FREE | 📦 5 Crates | 📊 10 Available 🎉
┣ 2 Rooms: 🛋️ Main Area, 📦 Crate Room
┗ ⚠️ Limited — grab yours while they last!

🏠 **Mid Turf** — 800 Robux | 📦 8 Crates | 📊 6 Available
┗ 4 Rooms: 🏋️ Training Area, 🛋️ Main Area, 🎨 Custom Room, 📦 Crate Room

🏢 **Big Turf** — 1,000 Robux | 📦 12 Crates | 📊 10 Available
┗ 2 Levels: 🚪 Entry, 📦 Crates, 🎨 Custom Room, 😌 Chill Room, 🏋️ Training, 🥊 Boxing Arena

─────────────────────────
**🎯 AMMO CRATES (For Your Turf)**
📦 **1 Crate = 20 Mags** — **50 Robux**
┣ 1 Mag refills ALL your guns instantly
┣ Each mag lasts **5 uses** before it's gone
┗ Available for: 🔫 AR  •  🎯 Sniper  •  🔧 Pistol  •  💥 Shotgun

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
🪴 Extra Decorations — 50–150 Robux
💨 Animated Effects (smoke, sparkles) — 75–200 Robux
🎵 Exclusive Turf Music — 100–150 Robux
"""

GAME_AND_LINKS = """
### 🎯 GAME & LINKS

### 🎮 [Roblox Game](https://www.roblox.com/share?code=2ee1ff592f4e4843b7c6390da0f61844&type=ExperienceDetails&stamp=1771789166361)

### 👥 [Roblox Group](https://www.roblox.com/share/g/628331601)

### 🪙 [Discord Server](https://discord.gg/eC8XYa97qS)
"""

# ⬆️ EDIT ABOVE ⬆️

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot is ONLINE as {bot.user}")
    bot.loop.create_task(discount_expiry_loop())

async def discount_expiry_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        check_expired_discounts()
        await asyncio.sleep(1800)  # check every 30 minutes

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
    event = get_event()
    embed = discord.Embed(description=NORMAL_PRICES, color=discord.Color(0x808080))
    if event:
        embed.set_footer(text=f"🎉 Active Event: {event}")
    await interaction.response.send_message(embed=embed)

@tree.command(name="turf_prices", description="Show turf prices")
async def turf_prices(interaction: discord.Interaction):
    event = get_event()
    embed = discord.Embed(description=TURF_PRICES, color=discord.Color(0x808080))
    if event:
        embed.set_footer(text=f"🎉 Active Event: {event}")
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

@tree.command(name="giveaways", description="Start multiple giveaways at once, each with its own prize and winner count (Staff only)")
@app_commands.describe(
    minutes="How long all giveaways last (in minutes)",
    prize1="First prize",
    winners1="Winners for prize 1 (default: 1)",
    prize2="Second prize",
    winners2="Winners for prize 2 (default: 1)",
    prize3="Third prize (optional)",
    winners3="Winners for prize 3 (default: 1)",
    prize4="Fourth prize (optional)",
    winners4="Winners for prize 4 (default: 1)",
    prize5="Fifth prize (optional)",
    winners5="Winners for prize 5 (default: 1)"
)
async def giveaways(
    interaction: discord.Interaction,
    minutes: int,
    prize1: str,
    prize2: str,
    winners1: int = 1,
    winners2: int = 1,
    prize3: str = None,
    winners3: int = 1,
    prize4: str = None,
    winners4: int = 1,
    prize5: str = None,
    winners5: int = 1
):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return

    entries = [
        (prize1, winners1),
        (prize2, winners2),
    ]
    if prize3: entries.append((prize3, winners3))
    if prize4: entries.append((prize4, winners4))
    if prize5: entries.append((prize5, winners5))

    end_time = discord.utils.utcnow().timestamp() + (minutes * 60)
    await interaction.response.send_message(f"✅ Starting **{len(entries)}** giveaways!", ephemeral=True)

    messages = []
    for prize, win_count in entries:
        embed = discord.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**Prize:** {prize}\n\nReact with 🎉 to enter!\n\n**Winners:** {win_count}\n**Ends:** <t:{int(end_time)}:R>",
            color=discord.Color(0x808080)
        )
        embed.set_footer(text=f"Hosted by {interaction.user.display_name}")
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction("🎉")
        messages.append((msg, prize, win_count))

    await asyncio.sleep(minutes * 60)

    for msg, prize, win_count in messages:
        msg = await interaction.channel.fetch_message(msg.id)
        reaction = discord.utils.get(msg.reactions, emoji="🎉")

        if reaction is None or reaction.count <= 1:
            await interaction.channel.send(f"❌ Not enough people entered the giveaway for **{prize}**!")
            continue

        users = [u async for u in reaction.users() if not u.bot]
        pick_count = min(win_count, len(users))
        picked = random.sample(users, pick_count)
        winner_mentions = ", ".join(w.mention for w in picked)

        result_embed = discord.Embed(
            title="🎉 GIVEAWAY ENDED 🎉",
            description=f"**Prize:** {prize}\n\n🏆 **Winner(s):** {winner_mentions}\n\nCongratulations!",
            color=discord.Color(0x808080)
        )
        await interaction.channel.send(embed=result_embed)
        await interaction.channel.send(f"🎉 Congrats {winner_mentions}! You won **{prize}**!")

# ── SERVER INFO ──────────────────────────────────────────────────────────────


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
    embed.add_field(name="💰 Prices", value="`/prices` `/shop` `/turf_prices` `/game_links`", inline=False)
    embed.add_field(name="🎉 Giveaways (Staff only)", value="`/giveaway` `/giveaways`", inline=False)
    embed.add_field(name="📊 Polls (Staff only)", value="`/poll`", inline=False)
    embed.add_field(name="🛡️ Moderation (Staff only)", value="`/kick` `/ban` `/mute` `/unmute` `/warn` `/warnings` `/say`", inline=False)
    embed.add_field(name="🏷️ Nicknames", value="`/nick` `/setnick`", inline=False)
    embed.add_field(name="❓ Info", value="`/help` `/ping`", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ping", description="Check the bot's response speed")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: **{latency}ms**")


# ── NICKNAME COMMANDS ─────────────────────────────────────────────────────────

@tree.command(name="nick", description="Change your own nickname")
@app_commands.describe(nickname="Your new nickname (leave empty to reset)")
async def nick(interaction: discord.Interaction, nickname: str = None):
    member = interaction.user
    if not isinstance(member, discord.Member):
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    try:
        if nickname:
            await member.edit(nick=nickname)
            await interaction.response.send_message(f"✅ Your nickname has been changed to **{nickname}**.", ephemeral=True)
        else:
            await member.edit(nick=None)
            await interaction.response.send_message("✅ Your nickname has been reset.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to change your nickname.", ephemeral=True)

@tree.command(name="setnick", description="Change a member's nickname (Staff only)")
@app_commands.describe(member="The member to rename", nickname="Their new nickname (leave empty to reset)")
async def setnick(interaction: discord.Interaction, member: discord.Member, nickname: str = None):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    try:
        if nickname:
            await member.edit(nick=nickname)
            await interaction.response.send_message(f"✅ **{member.name}**'s nickname has been changed to **{nickname}**.")
        else:
            await member.edit(nick=None)
            await interaction.response.send_message(f"✅ **{member.name}**'s nickname has been reset.")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I can't change that member's nickname. They may have a higher role than me.", ephemeral=True)

# ── OWNER PANEL ───────────────────────────────────────────────────────────────

DISCOUNTABLE_ITEMS = [
    ("Custom Draco", "250"),
    ("Custom SG", "300"),
    ("Custom Golden Gun", "350"),
    ("Custom Name + Level Bundle", "150"),
    ("Ammo Crate (20 Mags)", "50"),
    ("Small Cash 10k", "50"),
    ("Medium Cash 25k", "120"),
    ("Large Cash 50k", "200"),
    ("Mid Turf", "800"),
    ("Big Turf", "1000"),
]

def get_discounts():
    data = get_data()
    return data.get("_discounts", {})

def save_discount(item, original, discounted, expiry_iso):
    data = get_data()
    if "_discounts" not in data:
        data["_discounts"] = {}
    data["_discounts"][item] = {"original": original, "discounted": discounted, "expiry": expiry_iso}
    save_data(data)

def remove_discount(item):
    data = get_data()
    if "_discounts" in data and item in data["_discounts"]:
        del data["_discounts"][item]
        save_data(data)

def check_expired_discounts():
    data = get_data()
    discounts = data.get("_discounts", {})
    changed = False
    now = datetime.datetime.now()
    for item in list(discounts.keys()):
        try:
            expiry = datetime.datetime.fromisoformat(discounts[item]["expiry"])
            if now >= expiry:
                del discounts[item]
                changed = True
        except:
            pass
    if changed:
        data["_discounts"] = discounts
        save_data(data)

def build_discounts_embed():
    discounts = get_discounts()
    embed = discord.Embed(title="💰 Active Discounts", color=discord.Color(0x808080))
    if not discounts:
        embed.description = "No active discounts right now."
    else:
        lines = []
        for item, d in discounts.items():
            try:
                expiry = datetime.datetime.fromisoformat(d["expiry"])
                ts = int(expiry.timestamp())
                lines.append(f"**{item}**: ~~{d['original']} Robux~~ → **{d['discounted']} Robux** | Expires <t:{ts}:R>")
            except:
                lines.append(f"**{item}**: **{d['discounted']} Robux**")
        embed.description = "\n".join(lines)
    return embed

# ── PANEL MODALS ──

class DiscountModal(discord.ui.Modal, title="Set Discount"):
    def __init__(self, item_name, original_price):
        super().__init__()
        self.item_name = item_name
        self.original_price = original_price

    price = discord.ui.TextInput(label="Discounted Price (Robux)", placeholder="e.g. 200", max_length=10)
    expiry = discord.ui.TextInput(label="Expiry Date (DD/MM/YYYY)", placeholder="e.g. 31/12/2025", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            day, month, year = self.expiry.value.strip().split("/")
            expiry_dt = datetime.datetime(int(year), int(month), int(day), 23, 59, 59)
        except:
            await interaction.response.send_message("❌ Invalid date format. Use DD/MM/YYYY.", ephemeral=True)
            return
        if expiry_dt <= datetime.datetime.now():
            await interaction.response.send_message("❌ Expiry date must be in the future.", ephemeral=True)
            return
        save_discount(self.item_name, self.original_price, self.price.value.strip(), expiry_dt.isoformat())
        ts = int(expiry_dt.timestamp())
        await interaction.response.send_message(
            f"✅ Discount set!\n**{self.item_name}**: ~~{self.original_price} Robux~~ → **{self.price.value} Robux**\nExpires <t:{ts}:F>",
            ephemeral=True
        )

class RemovePrefixModal(discord.ui.Modal, title="Remove User Prefix"):
    user_id = discord.ui.TextInput(label="User ID", placeholder="Right-click user → Copy User ID", max_length=25)

    async def on_submit(self, interaction: discord.Interaction):
        uid = self.user_id.value.strip().strip("<@!>")
        try:
            int(uid)
        except:
            await interaction.response.send_message("❌ Invalid user ID.", ephemeral=True)
            return
        delete_prefix(int(uid))
        await interaction.response.send_message(f"✅ Prefix removed for <@{uid}>.", ephemeral=True)

# ── PANEL VIEWS ──

class DiscountItemSelect(discord.ui.Select):
    def __init__(self, action):
        self.action = action
        if action == "add":
            options = [discord.SelectOption(label=f"{name} ({price} Rbx)", value=f"{name}|{price}") for name, price in DISCOUNTABLE_ITEMS]
            placeholder = "Choose an item to discount..."
        else:
            discounts = get_discounts()
            options = [discord.SelectOption(label=item, value=item) for item in discounts.keys()] or [discord.SelectOption(label="No active discounts", value="none")]
            placeholder = "Choose a discount to remove..."
        super().__init__(placeholder=placeholder, options=options[:25])

    async def callback(self, interaction: discord.Interaction):
        if self.action == "add":
            name, price = self.values[0].split("|", 1)
            await interaction.response.send_modal(DiscountModal(name, price))
        else:
            if self.values[0] == "none":
                await interaction.response.send_message("No discounts to remove.", ephemeral=True)
                return
            remove_discount(self.values[0])
            await interaction.response.send_message(f"✅ Discount removed for **{self.values[0]}**.", ephemeral=True)

class DiscountView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="➕ Add Discount", style=discord.ButtonStyle.green)
    async def add_discount(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View(timeout=60)
        view.add_item(DiscountItemSelect("add"))
        await interaction.response.send_message("Select an item to discount:", view=view, ephemeral=True)

    @discord.ui.button(label="🗑️ Remove Discount", style=discord.ButtonStyle.red)
    async def remove_discount_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        discounts = get_discounts()
        if not discounts:
            await interaction.response.send_message("No active discounts to remove.", ephemeral=True)
            return
        view = discord.ui.View(timeout=60)
        view.add_item(DiscountItemSelect("remove"))
        await interaction.response.send_message("Select a discount to remove:", view=view, ephemeral=True)

    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.grey)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=build_panel_embed(), view=PanelView())

class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="💰 Discounts", style=discord.ButtonStyle.green, row=0)
    async def discounts_tab(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=build_discounts_embed(), view=DiscountView())

    @discord.ui.button(label="🛒 Shop", style=discord.ButtonStyle.blurple, row=0)
    async def shop_tab(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description=NORMAL_PRICES, color=discord.Color(0x808080))
        await interaction.response.edit_message(embed=embed, view=PanelView())

    @discord.ui.button(label="📊 Server Info", style=discord.ButtonStyle.blurple, row=0)
    async def serverinfo_tab(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        total = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        roles = [r.mention for r in reversed(guild.roles) if r.name != "@everyone"]
        role_display = ", ".join(roles[:20]) + (f" (+{len(roles)-20} more)" if len(roles) > 20 else "") if roles else "None"
        embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color(0x808080))
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="👥 Total", value=total, inline=True)
        embed.add_field(name="🧑 Humans", value=total - bots, inline=True)
        embed.add_field(name="🤖 Bots", value=bots, inline=True)
        embed.add_field(name="💬 Text", value=len(guild.text_channels), inline=True)
        embed.add_field(name="🔊 Voice", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="🎭 Roles", value=len(roles), inline=True)
        embed.add_field(name="🎭 Role List", value=role_display, inline=False)
        await interaction.response.edit_message(embed=embed, view=PanelView())

    @discord.ui.button(label="🎉 Set Event", style=discord.ButtonStyle.green, row=1)
    async def set_event_tab(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetEventModal())

def build_panel_embed():
    discounts = get_discounts()
    event = get_event()
    embed = discord.Embed(title="⚙️ Owner Panel", description="Use the buttons below to manage your bot.", color=discord.Color(0x808080))
    embed.add_field(name="💰 Discounts", value=f"{len(discounts)} active discount(s)", inline=True)
    embed.add_field(name="🛒 Shop", value="View shop prices", inline=True)
    embed.add_field(name="📊 Server Info", value="View server details", inline=True)
    embed.add_field(name="🎉 Current Event", value=event if event else "None", inline=True)
    return embed

@tree.command(name="panel", description="Owner-only control panel")
async def panel(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ This panel is only accessible by the bot owner.", ephemeral=True)
        return
    await interaction.response.send_message(embed=build_panel_embed(), view=PanelView(), ephemeral=True)


# ── EVENT / SEASON NAME ────────────────────────────────────────────────────────

def get_event():
    data = get_data()
    return data.get('_event', None)

def set_event(name):
    data = get_data()
    data['_event'] = name
    save_data(data)

def clear_event():
    data = get_data()
    data.pop('_event', None)
    save_data(data)

class SetEventModal(discord.ui.Modal, title="Set Season / Event Name"):
    event_name = discord.ui.TextInput(
        label="Event Name (leave blank to clear)",
        placeholder="e.g. Christmas, Easter, Summer Event",
        required=False,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        name = self.event_name.value.strip()
        if name:
            set_event(name)
            await interaction.response.send_message(f"✅ Event set to **{name}**! It will now show in shop and turf prices.", ephemeral=True)
        else:
            clear_event()
            await interaction.response.send_message("✅ Event name cleared.", ephemeral=True)

token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("DISCORD_TOKEN environment variable is not set.")
bot.run(token)
