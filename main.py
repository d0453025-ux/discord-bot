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

STAFF_ROLE_NAME = "HCBotacces"
STAFF_ROLE_ID = 1513285028606640250


def has_staff_role(interaction: discord.Interaction) -> bool:
    member = interaction.user
    if interaction.guild and not isinstance(member, discord.Member):
        member = interaction.guild.get_member(interaction.user.id)
    if isinstance(member, discord.Member):
        return any(r.id == STAFF_ROLE_ID for r in member.roles)
    return False


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

@tree.command(name="staffcheck", description="Debug: show your roles and IDs")
async def staffcheck(interaction: discord.Interaction):
    user = interaction.user
    user_type = type(user).__name__
    lines = [f"**User type:** `{user_type}`", f"**User ID:** `{user.id}`"]

    member = user if isinstance(user, discord.Member) else None
    if interaction.guild and not member:
        member = interaction.guild.get_member(user.id)

    if member:
        roles = member.roles
        if roles:
            lines.append(f"**Roles ({len(roles)}):**")
            for r in roles:
                lines.append(f"`{r.id}` — {r.name}")
        else:
            lines.append("**Roles:** none found")
    else:
        lines.append("❌ Could not fetch Member object")

    staff_found = member and any(r.id == STAFF_ROLE_ID for r in member.roles)
    lines.append(f"\n**Looking for ID:** `{STAFF_ROLE_ID}`")
    lines.append(f"**Result:** {'✅ PASS' if staff_found else '❌ FAIL'}")
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


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
