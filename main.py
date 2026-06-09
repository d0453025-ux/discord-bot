import discord
import os
import asyncio
import random
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from discord import app_commands

# ── STARTUP BANNER ────────────────────────────────────────────────────────────
_BANNERS = [
    r"""
  ██╗  ██╗ ██████╗  ██████╗ ██████╗
  ██║  ██║██╔════╝ ██╔════╝ ██╔══██╗
  ███████║██║      ██║      ██║  ██║
  ██╔══██║██║      ██║      ██║  ██║
  ██║  ██║╚██████╗ ╚██████╗ ██████╔╝
  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝
   ██████╗ ██████╗ ███╗  ██╗███████╗
  ██╔════╝██╔═══██╗████╗ ██║██╔════╝
  ██║     ██║   ██║██╔██╗██║█████╗
  ██║     ██║   ██║██║╚████║██╔══╝
  ╚██████╗╚██████╔╝██║ ╚███║██║
   ╚═════╝ ╚═════╝ ╚═╝  ╚══╝╚═╝
    """,
    r"""
  /##   /## /######   /######  /######
 | ##  | ##| ##__  ## /##__  ##| ##__  ##
 | ##  | ##| ##  \ ##| ##  \__/| ##  \ ##
 | ########| ##  | ##| ##      | ##  | ##
 | ##__  ##| ##  | ##| ##      | ##  | ##
 | ##  | ##| ##  | ##| ##    ##| ##  | ##
 | ##  | ##| ######/ |  ######/| ######/
 |__/  |__/|_____/   \______/ |_____/
   /######   /######  /##   /## /########### /##    /## /##
  /##__  ## /##__  ##| ### | ##| ##_____/| ##   | ##|_/
 | ##  \__/| ##  \ ##| ####| ##| ##      | ##   | ##  /##
 | ##      | ##  | ##| ## ## ##| #####   | ##   | ## | ##
 | ##      | ##  | ##| ##  ####| ##__/   | ##   | ## | ##
 | ##    ##| ##  | ##| ##\  ###| ##      | ##   | ## | ##
 |  ######/|  ######/| ## \  ##| ##      |  ######/ | ##
  \______/  \______/ |__/  \__/|__/       \______/ |__/
    """,
    r"""
  +-------------------------------+
  |   H O O D   C O N F L I C T  |
  |   ~~~  Discord Bot  ~~~       |
  |   [ Protecting the block ]   |
  +-------------------------------+
    """,
    r"""
  ┌─────────────────────────────────┐
  │  🔫  HOOD CONFLICT BOT  🔫      │
  │  ─────────────────────────────  │
  │  Territory. Respect. Power.     │
  │  Status: ONLINE & ARMED 💪      │
  └─────────────────────────────────┘
    """,
    r"""
   _   _  ___   ___  ____     ____ ___  _   _ _____ _     ___ ____ _____
  | | | |/ _ \ / _ \|  _ \   / ___/ _ \| \ | |  ___| |   |_ _/ ___|_   _|
  | |_| | | | | | | | | | | | |  | | | |  \| | |_  | |    | | |     | |
  |  _  | |_| | |_| | |_| | | |__| |_| | |\  |  _| | |___ | | |___  | |
  |_| |_|\___/ \___/|____/   \____\___/|_| \_|_|   |_____|___\____| |_|
    """,
]

def _print_banner():
    banner = random.choice(_BANNERS)
    print("\033[96m" + banner + "\033[0m")
    print("\033[93m  Bot starting up...\033[0m\n")

_print_banner()

# ── KEEP-ALIVE SERVER (satisfies Replit deployment health check) ───────────────
class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hood Conflict Bot is running!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
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
bot = discord.Client(
    intents=intents,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True)
)
tree = app_commands.CommandTree(bot)

# ── RATE LIMITING ─────────────────────────────────────────────────────────────
_cmd_cooldowns: dict[int, float] = {}
_CMD_COOLDOWN_SECS = 2.0

def _check_rate_limit(user_id: int) -> bool:
    now = time.monotonic()
    last = _cmd_cooldowns.get(user_id, 0)
    if now - last < _CMD_COOLDOWN_SECS:
        return False
    _cmd_cooldowns[user_id] = now
    return True

OWNER_ID = 1262338624402493460

def get_staff_users():
    data = get_data()
    return data.get("_staff_users", [])

def save_staff_users(users):
    data = get_data()
    data["_staff_users"] = users
    save_data(data)

def has_staff_role(interaction: discord.Interaction) -> bool:
    uid = interaction.user.id
    if uid == OWNER_ID:
        return True
    return uid in get_staff_users()


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
🔫 **Tec 9 SG** — 200Robux
┣ 20 Base Spawns
┗ Name, Level, Laser/Glow Effects, Trails

🔫 **Custom SG** — 370 Robux
┣ 25 Base Spawns
┗ Name, Level, Laser/Glow Effects

🔫 **Custom Golden Gun SG** — 400 Robux
┣ 25 Base Spawns
┗ Name, Level, Laser/Glow Effects, Golden Finish

─────────────────────────
**🔧 BUNDLES & ADD-ONS**
none
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
    for guild in bot.guilds:
        await tree.sync(guild=guild)
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



# ── HELP / INFO ───────────────────────────────────────────────────────────────

@tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 BOT COMMANDS", color=discord.Color(0x808080))
    embed.add_field(name="💰 Prices", value="`/prices` `/shop` `/turf_prices` `/game_links`", inline=False)
    embed.add_field(name="🎉 Giveaways (Staff only)", value="`/giveaway` `/giveaways`", inline=False)
    embed.add_field(name="📊 Polls (Staff only)", value="`/poll`", inline=False)
    embed.add_field(name="❓ Info", value="`/help` `/ping`", inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ping", description="Check the bot's response speed")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: **{latency}ms**")

@tree.command(name="rules", description="Show the server rules")
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📋 SERVER RULES",
        description="These rules are intended to keep the server in-order and are always subject to change. They are enforced at moderator discretion, failure to comply will result in punishment.",
        color=discord.Color(0x808080)
    )
    embed.add_field(name="🤝 Stay civil and treat users with respect", value=(
        "➤ Treat others the way you want to be treated.\n"
        "➤ Trolling, Doxxing, Personal Attacks, Racism, Homophobia, Death threats and similar actions will not be tolerated. (This includes jokes)\n"
        "➤ Attacking users through DMs is also prohibited.\n"
        "➤ Don't be toxic and use common sense."
    ), inline=False)
    embed.add_field(name="💬 Keep chat tidy and appropriate", value=(
        "➤ Keep channels to their dedicated languages.\n"
        "➤ No spamming or mindless posting, stay on topic and use the correct channels.\n"
        "➤ No advertising Discord/Roblox groups in server or DMs.\n"
        "➤ Refrain from discussing Politics, Religion, and other controversial topics.\n"
        "➤ Severe arguments and outbursts will not be tolerated.\n"
        "➤ Refrain from sensitive topics such as depression, self-harm, suicide, etc.\n"
        "➤ Create reports with evidence rather than public callouts."
    ), inline=False)
    embed.add_field(name="🔞 Inappropriate content is prohibited", value=(
        "➤ This includes extreme violence, sexual content, gore, and other sensitive content.\n"
        "➤ Heavy NSFW jokes and comments are not allowed.\n"
        "➤ You may be asked to change your bio, avatar, or name if deemed unfit."
    ), inline=False)
    embed.add_field(name="🚫 No discussion or distribution of exploits", value=(
        "➤ Discussion of exploits is prohibited.\n"
        "➤ Attempting to buy/sell exploiting software will result in an immediate ban in server and in game."
    ), inline=False)
    embed.add_field(name="📢 Only contact the moderation team when necessary", value=(
        "➤ Only ping staff if it is completely necessary.\n"
        "➤ Pinging mods without reason will be considered trolling.\n"
        "➤ Understand that mods may not always be available, refrain from harassing staff."
    ), inline=False)
    embed.add_field(name="⚠️ Other rules", value=(
        "➤ No gambling for items with owners.\n"
        "➤ No bringing arguments from other Discord servers to this one."
    ), inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="ing_rules", description="Show the in-game rules")
async def ing_rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎮 HOOD CONFLICT — IN-GAME RULES",
        color=discord.Color(0x808080)
    )
    embed.add_field(name="✅ Allowed", value=(
        "➤ FPS Unlockers/Shaders ARE allowed. They will not get you banned."
    ), inline=False)
    embed.add_field(name="🚫 Chat & Behaviour", value=(
        "➤ Excessive spam, bypassing swears, discriminatory remarks, threats and NSFW remarks are not allowed under any circumstances.\n"
        "➤ Misusing car radios to play bypassed audios or extremely loud sounds at spawn is disallowed and may result in a temporary ban."
    ), inline=False)
    embed.add_field(name="📢 No Advertising", value=(
        "➤ Advertising other groups or games (including Roblox groups that require Discords) is not allowed.\n"
        "➤ Advertising in direct messages is also not allowed."
    ), inline=False)
    embed.add_field(name="⚠️ Miscellaneous Rules", value=(
        "➤ Impersonation of Staff is an offense and can result in kicks or temporary bans.\n"
        "➤ Using alternate accounts to evade bans will result in an unappealable ban of your alt and possibly your main.\n"
        "➤ All actions taken on your account are assumed to be your own — keep your account secure."
    ), inline=False)
    await interaction.response.send_message(embed=embed)

@tree.command(name="staffcheck", description="Check if you have staff access")
async def staffcheck(interaction: discord.Interaction):
    uid = interaction.user.id
    is_owner = uid == OWNER_ID
    in_list = uid in get_staff_users()
    result = is_owner or in_list
    lines = [
        f"**User ID:** `{uid}`",
        f"**Owner:** {'✅ Yes' if is_owner else '❌ No'}",
        f"**In staff list:** {'✅ Yes' if in_list else '❌ No'}",
        f"**Access:** {'✅ GRANTED' if result else '❌ DENIED'}"
    ]
    await interaction.response.send_message("\n".join(lines), ephemeral=True)

@tree.command(name="staff_add", description="Give someone staff access (Owner only)")
@app_commands.describe(user="The user to give staff access to")
async def staff_add(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Only the bot owner can use this.", ephemeral=True)
        return
    users = get_staff_users()
    if user.id in users:
        await interaction.response.send_message(f"⚠️ {user.mention} already has staff access.", ephemeral=True)
        return
    users.append(user.id)
    save_staff_users(users)
    await interaction.response.send_message(f"✅ **{user.name}** has been given staff access.", ephemeral=True)

@tree.command(name="staff_remove", description="Remove someone's staff access (Owner only)")
@app_commands.describe(user="The user to remove staff access from")
async def staff_remove(interaction: discord.Interaction, user: discord.User):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Only the bot owner can use this.", ephemeral=True)
        return
    users = get_staff_users()
    if user.id not in users:
        await interaction.response.send_message(f"⚠️ {user.mention} doesn't have staff access.", ephemeral=True)
        return
    users.remove(user.id)
    save_staff_users(users)
    await interaction.response.send_message(f"✅ **{user.name}**'s staff access has been removed.", ephemeral=True)

@tree.command(name="staff_list", description="Show all users with staff access")
async def staff_list(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Only the bot owner can use this.", ephemeral=True)
        return
    users = get_staff_users()
    embed = discord.Embed(title="👥 Staff Access List", color=discord.Color(0x808080))
    embed.add_field(name="👑 Owner", value=f"<@{OWNER_ID}>", inline=False)
    if users:
        embed.add_field(name="✅ Staff Users", value="\n".join([f"<@{uid}>" for uid in users]), inline=False)
    else:
        embed.add_field(name="✅ Staff Users", value="None added yet", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ── RECYCLE TURFS ─────────────────────────────────────────────────────────────

def get_recycleturfs():
    data = get_data()
    return data.get("_recycleturfs", [])

def save_recycleturf(name, price, description):
    data = get_data()
    if "_recycleturfs" not in data:
        data["_recycleturfs"] = []
    data["_recycleturfs"].append({"name": name, "price": price, "description": description})
    save_data(data)

@tree.command(name="recycleturf", description="Show all available recycled turfs for sale")
async def recycleturf(interaction: discord.Interaction):
    turfs = get_recycleturfs()
    embed = discord.Embed(
        title="♻️ RECYCLE TURFS",
        description="Turfs that have already been built and are available to buy:",
        color=discord.Color(0x808080)
    )
    if not turfs:
        embed.description = "♻️ **No recycled turfs available right now.**\nCheck back later!"
    else:
        for i, turf in enumerate(turfs, 1):
            embed.add_field(
                name=f"🏠 {i}. {turf['name']} — {turf['price']} Robux",
                value=turf['description'],
                inline=False
            )
        embed.set_footer(text=f"{len(turfs)} turf(s) available | DM staff to buy")
    await interaction.response.send_message(embed=embed)

@tree.command(name="recycleturf_add", description="Add a recycled turf to the list (Staff only)")
@app_commands.describe(
    name="Name/type of the turf (e.g. Mid Turf)",
    price="Price in Robux",
    description="Description of the turf (rooms, extras, etc.)"
)
async def recycleturf_add(interaction: discord.Interaction, name: str, price: str, description: str):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    if len(name) > 50:
        await interaction.response.send_message("❌ Name too long (max 50 characters).", ephemeral=True)
        return
    if len(description) > 300:
        await interaction.response.send_message("❌ Description too long (max 300 characters).", ephemeral=True)
        return
    save_recycleturf(name, price, description)
    embed = discord.Embed(
        title="✅ Recycle Turf Added",
        color=discord.Color(0x808080)
    )
    embed.add_field(name="🏠 Turf", value=name, inline=True)
    embed.add_field(name="💰 Price", value=f"{price} Robux", inline=True)
    embed.add_field(name="📝 Description", value=description, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="recycleturf_remove", description="Remove a recycled turf from the list (Staff only)")
@app_commands.describe(number="The number of the turf to remove (use /recycleturf to see the numbers)")
async def recycleturf_remove(interaction: discord.Interaction, number: int):
    if not has_staff_role(interaction):
        await interaction.response.send_message(f"❌ You need the **{STAFF_ROLE_NAME}** role to use this command.", ephemeral=True)
        return
    data = get_data()
    turfs = data.get("_recycleturfs", [])
    if not turfs:
        await interaction.response.send_message("❌ No recycled turfs to remove.", ephemeral=True)
        return
    if number < 1 or number > len(turfs):
        await interaction.response.send_message(f"❌ Invalid number. There are **{len(turfs)}** turfs listed.", ephemeral=True)
        return
    removed = turfs.pop(number - 1)
    data["_recycleturfs"] = turfs
    save_data(data)
    await interaction.response.send_message(f"✅ Removed **{removed['name']}** from the recycle turf list.", ephemeral=True)

token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("DISCORD_TOKEN environment variable is not set.")
bot.run(token)
