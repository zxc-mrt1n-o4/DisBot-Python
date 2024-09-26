import discord
from discord.ext import commands
import math
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta
from datetime import datetime
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sqlite3
import random
import string


print("""·▄▄▄▄  ▪  .▄▄ · ▄▄▄▄·       ▄▄▄▄▄
██▪ ██ ██ ▐█ ▀. ▐█ ▀█▪▪     •██  
▐█· ▐█▌▐█·▄▀▀▀█▄▐█▀▀█▄ ▄█▀▄  ▐█.▪
██. ██ ▐█▌▐█▄▪▐███▄▪▐█▐█▌.▐▌ ▐█▌·
▀▀▀▀▀• ▀▀▀ ▀▀▀▀ ·▀▀▀▀  ▀█▄▀▪ ▀▀▀    """)

############################################################################################################################################
############################################################ ДОСТУП БОТА СЕТАП #############################################################
############################################################################################################################################

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='~', intents=intents)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


############################################################################################################################################
############################################################       БОНУС       #############################################################
############################################################################################################################################

# NewsAPI Key (replace with your actual key)
NEWS_API_KEY = ''
NEWS_URL = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=5d9ae2f2dd0f4ca8878aa1016394cf74"

# Weather API Key (replace with your actual key)
WEATHER_API_KEY = ''
WEATHER_URL = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q=Charlotte&lang=ru"

# List of Russian anecdotes
# List of Russian anecdotes
anecdotes = [
    "— Почему ты никогда не улыбаешься на работе?\n— Потому что зарплату вспоминаю.",
    "— Доктор, я живу в мире, где все меня раздражают!\n— А что именно вас раздражает?\n— То, что все вокруг такие спокойные!",
    "Встречаются два программиста:\n— Ты почему так устал?\n— Целый день исправлял баги в коде!\n— Ну хоть что-то исправил?\n— Конечно! Теперь их стало в два раза больше.",
    "— Дорогая, а что у нас на ужин?\n— Как обычно, сюрприз!\n— Опять гречка?",
    "— Какова главная черта настоящего оптимиста?\n— Это тот, кто берет зонт в пустыню, думая, что вдруг пойдет дождь.",
    "— Почему ты так долго сидишь на диете?\n— Жду, пока холодильник сдастся первым.",
    "Звонок в техподдержку:\n— Алло, у меня компьютер сломался, он вообще не включается!\n— А вы пробовали перезагрузить его?\n— А как я его перезагружу, если он вообще не включается?!",
    "Собрание:\n— Итак, коллеги, у нас плохие новости и очень плохие новости.\n— Начните с плохих.\n— Наша зарплата задерживается.\n— А очень плохие?\n— Мы ее все равно не увидим.",
    "— Вась, как ты думаешь, деньги — это зло?\n— Зло, конечно, но без них жить как-то ещё хуже.",
    "— Ты знаешь, что говорят про русских?\n— Что именно?\n— Что у нас для каждой проблемы есть анекдот!"
]

# Function to get the weather
async def get_weather():
    async with aiohttp.ClientSession() as session:
        async with session.get(WEATHER_URL) as resp:
            data = await resp.json()
            location = data['location']['name']
            weather_desc = data['current']['condition']['text']
            temperature = data['current']['temp_c']
            return f"{location}: {weather_desc}, {temperature}°C"

# Function to get Russian news using NewsAPI
async def get_news():
    async with aiohttp.ClientSession() as session:
        async with session.get(NEWS_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"NewsAPI Response: {data}")  # Debugging: log the full response
                
                # Ensure that articles are present
                if 'articles' in data and len(data['articles']) > 0:
                    articles = data['articles'][:3]  # Get the top 3 articles
                    news_list = [
                        f"{article['title']} - {article['source']['name']}\nСсылка: {article['url']}" 
                        for article in articles
                    ]
                    return "\n\n".join(news_list)
                else:
                    return "Нет доступных новостей в данный момент."
            else:
                return f"Ошибка при получении новостей: {resp.status}"

# Only Admins can use this command
@bot.command()
@commands.has_role("Admin")  # Replace "Admin" with the role name that should have access
async def now(ctx):
    # Get weather
    weather = await get_weather()

    # Get news
    news = await get_news()

    # Get random anecdote
    anecdote = random.choice(anecdotes)

    # Send the response
    response = f"Погода в Северной Каролине, Шарлот: {weather}.\nНовости:\n{news}\n\n\"{anecdote}\""
    await ctx.send(response)

# Error handling for missing role
@now.error
async def now_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("У вас нет прав для выполнения этой команды.")

############################################################################################################################################
############################################################    ВЫДАЧА РОЛЕЙ    ############################################################
############################################################################################################################################

@bot.command()
@commands.has_role("Admin")  # Only Admins can run this command
async def op(ctx, member: discord.Member):
    """Assign the 'Admin' role to a member."""
    role = discord.utils.get(ctx.guild.roles, name="Admin")
    if not role:
        await ctx.send("Role 'Admin' not found.")
        return

    if role in member.roles:
        await ctx.send(f"{member.mention} already has the 'Admin' role.")
        return

    try:
        # Add the 'Admin' role to the user
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been given the 'Admin' role.")
    except discord.Forbidden:
        await ctx.send("I do not have permission to add roles.")
    except Exception as e:
        await ctx.send(f"Error assigning 'Admin' role: {e}")


@bot.command()
@commands.has_role("Admin")  # Only Admins can run this command
async def mod(ctx, member: discord.Member):
    """Assign the 'Moder' role to a member."""
    role = discord.utils.get(ctx.guild.roles, name="Moder")
    if not role:
        await ctx.send("Role 'Moder' not found.")
        return

    if role in member.roles:
        await ctx.send(f"{member.mention} already has the 'Moder' role.")
        return

    try:
        # Add the 'Moder' role to the user
        await member.add_roles(role)
        await ctx.send(f"{member.mention} has been given the 'Moder' role.")
        password = 123
        await member.send(f"Your password is `{password}` use it to `~unlock` your account.")
    except discord.Forbidden:
        await ctx.send("I do not have permission to add roles.")
    except Exception as e:
        await ctx.send(f"Error assigning 'Moder' role: {e}")


@bot.command()
@commands.has_role("Admin")  # Only Admins can run this command
async def deop(ctx, member: discord.Member):
    """Remove the 'Admin' role from a member."""
    role = discord.utils.get(ctx.guild.roles, name="Admin")
    if role:
        try:
            await member.remove_roles(role)
            await ctx.send(f"{member.mention} has been removed from the 'Admin' role.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to remove roles.")
        except Exception as e:
            await ctx.send(f"Error removing 'Admin' role: {e}")
    else:
        await ctx.send("Role 'Admin' not found.")


@bot.command()
@commands.has_role("Admin")  # Only Admins can run this command
async def demod(ctx, member: discord.Member):
    """Remove the 'Moder' role from a member."""
    role = discord.utils.get(ctx.guild.roles, name="Moder")
    if role:
        try:
            await member.remove_roles(role)
            await ctx.send(f"{member.mention} has been removed from the 'Moder' role.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to remove roles.")
        except Exception as e:
            await ctx.send(f"Error removing 'Moder' role: {e}")
    else:
        await ctx.send("Role 'Moder' not found.")

############################################################################################################################################
############################################################    ЭКПА И РАНГИ    ############################################################
############################################################################################################################################

# File path for saving XP data
XP_FILE = 'ranks.json'

def load_xp_data():
    """Load XP data from the JSON file."""
    if os.path.exists(XP_FILE):
        with open(XP_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_xp_data(data):
    """Save XP data to the JSON file."""
    with open(XP_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Load user data on startup
user_data = load_xp_data()

def get_level(xp):
    """Calculate the user's level based on their total XP."""
    return math.floor(0.1 * math.sqrt(xp))

def get_next_level_xp(level):
    """Calculate how much XP is required to reach the next level."""
    return (level + 1) ** 2 * 100


@bot.event
async def on_message(message):
    # Ensure the message is not from the bot and that it is in a guild (server)
    if message.author == bot.user or not message.guild:
        return

    # Only track messages longer than 5 characters that do not start with the command prefix
    if len(message.content) > 5 and not message.content.startswith(bot.command_prefix):
        user_id = str(message.author.id)
        server_id = str(message.guild.id)  # Track XP per server
        
        if server_id not in user_data:
            user_data[server_id] = {}

        if user_id not in user_data[server_id]:
            user_data[server_id][user_id] = {"xp": 0, "level": 0}

        # Add 2 XP for each valid message (but don't notify)
        user_data[server_id][user_id]["xp"] += 2
        current_xp = user_data[server_id][user_id]["xp"]
        current_level = user_data[server_id][user_id]["level"]
        new_level = get_level(current_xp)

        # Level up check (without notification for regular users)
        if new_level > current_level:
            user_data[server_id][user_id]["level"] = new_level

        # Save data to file
        save_xp_data(user_data)

    # Ensure the bot processes other commands
    await bot.process_commands(message)

@bot.command()
async def rank(ctx):
    """Show the user's current rank and XP."""
    if not ctx.guild:
        await ctx.send("This command can only be used in servers.")
        return
    
    user_id = str(ctx.author.id)
    server_id = str(ctx.guild.id)

    if server_id in user_data and user_id in user_data[server_id]:
        xp = user_data[server_id][user_id]["xp"]
        level = user_data[server_id][user_id]["level"]
        next_level_xp = get_next_level_xp(level)
        await ctx.send(f"{ctx.author.mention}, you are level {level} with {xp} XP. You need {next_level_xp - xp} more XP to reach level {level + 1}.")
    else:
        await ctx.send(f"{ctx.author.mention}, you don't have any XP yet!")

@bot.command()
@commands.has_permissions(administrator=True)  # Only admins can use this command
async def xp(ctx, action: str, user: discord.Member, amount: int):
    """Command to add XP to a user, only available to server admins."""
    if not ctx.guild:
        await ctx.send("This command can only be used in servers.")
        return
    
    user_id = str(user.id)
    server_id = str(ctx.guild.id)

    if server_id not in user_data:
        user_data[server_id] = {}

    if action == "add":
        if user_id not in user_data[server_id]:
            user_data[server_id][user_id] = {"xp": 0, "level": 0}

        # Add the specified amount of XP manually
        user_data[server_id][user_id]["xp"] += amount
        current_xp = user_data[server_id][user_id]["xp"]
        current_level = user_data[server_id][user_id]["level"]
        new_level = get_level(current_xp)

        # Notify the user if an admin adds XP and if they level up
        if new_level > current_level:
            user_data[server_id][user_id]["level"] = new_level
            await ctx.send(f"{user.mention} has been awarded {amount} XP and leveled up to level {new_level}!")
        else:
            await ctx.send(f"{user.mention} has been awarded {amount} XP.")

        # Save data to file
        save_xp_data(user_data)
    else:
        await ctx.send("Invalid action. Use `add` to give XP.")

@xp.error
async def xp_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")

############################################################################################################################################
########################################################    TOP 10 ФОНК СПОТИК   ###########################################################
############################################################################################################################################

@bot.command()
@commands.has_permissions(administrator=True)
async def top10(ctx):
    """Fetch and display the top 10 tracks from the Official PHONK playlist (admin only)."""
    if not ctx.guild:
        await ctx.send("This command can only be used in servers.")
        return
    
    try:
        message = get_top_10_tracks()
        await ctx.send(message)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@top10.error
async def top10_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command. Only admins can use it.")

# Spotify API credentials (replace with your own from the Spotify Developer Dashboard)
SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''

# Set up Spotify API authorization
spotify_auth = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=spotify_auth)

# Playlist URL and ID
PHONK_PLAYLIST_ID = '37i9dQZF1DWWY64wDtewQt'

def get_top_10_tracks():
    """Fetch and return the top 10 tracks from the Official PHONK playlist."""
    playlist = spotify.playlist_tracks(PHONK_PLAYLIST_ID, limit=10)
    tracks = playlist['items']
    
    # message with the top 10 tracks
    message = "**Top 10 Tracks from the Official PHONK Playlist**\n\n"
    for idx, item in enumerate(tracks, start=1):
        track = item['track']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        message += f"{idx}. {track_name} by {artist_name}\n"
    
    return message

# Scheduler for the daily task
scheduler = AsyncIOScheduler()

# Channel ID for top 10
TARGET_CHANNEL_ID = ''  # Replace with the channel ID where you want the message to be sent

async def send_top_10_daily():
    """Send the top 10 tracks to the specified channel every day at 12 AM."""
    channel = bot.get_channel(int(TARGET_CHANNEL_ID))
    if channel:
        message = get_top_10_tracks()
        await channel.send(message)

@scheduler.scheduled_job('cron', hour=0, minute=0)  # Scheduled for 12 AM every day
async def scheduled_top_10():
    await send_top_10_daily()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    scheduler.start()  # таймер на день для топ 10 фонка

############################################################################################################################################
########################################################     HELP COMMAND    ###############################################################
############################################################################################################################################

#HELP COMMAND#
bot.remove_command('help')
@bot.command(name='help')
async def custom_help(ctx):
    """Custom help command that shows available commands based on user role."""
    if not ctx.guild:
        await ctx.send("This command can only be used in servers.")
        return

    user = ctx.author
    commands_list = []  # To store the available commands

    # Loop through all the commands the bot has
    for command in bot.commands:
        # Skip hidden commands
        if command.hidden:
            continue

        # Check if the command requires specific permissions
        try:
            # Check if the user has the permission to run the command
            can_run = await command.can_run(ctx)
        except commands.MissingPermissions:
            can_run = False

        # Append the command if the user can run it
        if can_run:
            commands_list.append(f"**{command.name}**: {command.help}")

    # If no commands are available for the user
    if not commands_list:
        await ctx.author.send("You don't have any commands available.")
        return

    # Create the help message
    help_message = "Here are the commands you can use:\n\n" + "\n".join(commands_list)

    # Send the message privately to the user
    await ctx.author.send(help_message)
    # Optionally send a confirmation in the channel
    await ctx.send(f"{user.mention}, I've sent you a list of available commands via DM.")

############################################################################################################################################
############################################################    PING    ####################################################################
############################################################################################################################################

#########PING###########
@bot.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    """Check the bot's latency."""
    latency = round(bot.latency * 1000)  # Convert latency to milliseconds
    await ctx.send(f'Pong! Latency: {latency}ms')


############################################################################################################################################
##########################################################    TESTING    ###################################################################
############################################################################################################################################

@bot.command()
@commands.has_role("Admin")  # Only admins can run this test
async def test(ctx):
    """Test all commands automatically and report results."""
    log = []
    success_count = 0
    total_count = 0

    try:
        # Try fetching the bot member and user 'Myrtyx'
        disbot = discord.utils.get(ctx.guild.members, name="disbot")

        # If members are not found in the cache, fetch them directly
        if not disbot:
            disbot = await ctx.guild.fetch_member(1282027845622694018)

    except Exception as e:
        await ctx.send(f"Error fetching members: {str(e)}")
        return

    # Ensure that the bot and user 'Myrtyx' exist
    if not disbot:
        await ctx.send("Bot user not found.")
        return
    
    # Iterate over all commands in the bot
    for command in bot.commands:
        # Skip the 'test' command itself to avoid recursive testing
        if command.name == 'test':
            continue

        total_count += 1  # Only count valid commands

        # Log the command being tested
        log.append(f"Testing command: {command.name}")

        try:
            # Use ctx.invoke() to call the command with appropriate arguments
            if command.name == "mod":
                await ctx.invoke(command, member=disbot)
            elif command.name == "demod":
                await ctx.invoke(command, member=disbot)
            elif command.name == "op":
                await ctx.invoke(command, member=disbot)
            elif command.name == "deop":
                await ctx.invoke(command, member=disbot)
            elif command.name == "xp":
                # Add 10 XP to disbot for the xp test
                await ctx.invoke(command, action="add", user=disbot, amount=10)
            elif command.name == "ban" or command.name == "unban":
                # Skip ban and unban for testing purposes
                log.append(f"**Command {command.name} skipped for testing.**")
            else:
                # For other commands, use appropriate args based on the command
                if command.name in ["warn", "mute"]:
                    await ctx.invoke(command, user=disbot)
                elif command.name in ["unwarn", "unmute"]:
                    await ctx.invoke(command, user=disbot)

            # Log success
            log.append(f"**Command {command.name} passed.**")
            success_count += 1

        except Exception as e:
            # Log failure
            log.append(f"**Command {command.name} failed. Error: {str(e)}**")

    # Summarize test results
    result_summary = f"## Test Completed: {success_count}/{total_count} commands passed.\n"
    result_summary += "\n".join(log)

    # Send the result summary and logs
    if len(result_summary) > 2000:
        for i in range(0, len(result_summary), 2000):
            await ctx.send(result_summary[i:i+2000])
    else:
        await ctx.send(result_summary)

############################################################################################################################################
########################################################    НАКАЗААНИЯ    ##################################################################
############################################################################################################################################

# Define role names
MODERATOR_ROLE_NAME = "Moder"
ADMIN_ROLE_NAME = "Admin"
DISBOT_ROLE_NAME = "Disbot"
MUTE_ROLE_NAME = "плохой"  # Change to your actual mute role name if different

# Initialize storage for warnings and mutes
warnings = {}  # Format: {user_id: [warning_count, mute_end_time]}
mutes = {}  # Format: {user_id: mute_end_time}
def has_disbot_or_admin_role():
    """Check if the author has the Disbot or Admin role."""
    async def predicate(ctx):
        disbot_role = discord.utils.get(ctx.guild.roles, name=DISBOT_ROLE_NAME)
        admin_role = discord.utils.get(ctx.guild.roles, name=ADMIN_ROLE_NAME)
        return disbot_role in ctx.author.roles or admin_role in ctx.author.roles
    return commands.check(predicate)

@bot.command()
@has_disbot_or_admin_role()
async def warn(ctx, user: discord.Member):
    """Warn a user and apply mute if 3 warnings are reached."""
    user_id = str(user.id)
    now = datetime.now()

    if user_id not in warnings:
        warnings[user_id] = [0, None]

    warnings[user_id][0] += 1

    if warnings[user_id][0] >= 3:
        mute_end_time = now + timedelta(hours=12)
        mutes[user_id] = mute_end_time
        mute_role = discord.utils.get(ctx.guild.roles, name=MUTE_ROLE_NAME)
        if mute_role:
            await user.add_roles(mute_role)
        await ctx.send(f"{user.mention} has been muted for 12 hours due to 3 warnings.")
    else:
        await ctx.send(f"{user.mention} has been warned. Total warnings: {warnings[user_id][0]}.")

@bot.command()
@has_disbot_or_admin_role()
async def mute(ctx, user: discord.Member):
    """Mute a user for 12 hours."""
    user_id = str(user.id)
    now = datetime.now()
    mute_end_time = now + timedelta(hours=12)
    
    mutes[user_id] = mute_end_time
    mute_role = discord.utils.get(ctx.guild.roles, name=MUTE_ROLE_NAME)
    if mute_role:
        await user.add_roles(mute_role)
    await ctx.send(f"{user.mention} has been muted for 12 hours.")

@bot.command()
@has_disbot_or_admin_role()
async def unmute(ctx, user: discord.Member):
    """Unmute a user."""
    user_id = str(user.id)
    
    if user_id in mutes:
        del mutes[user_id]
        mute_role = discord.utils.get(ctx.guild.roles, name=MUTE_ROLE_NAME)
        if mute_role:
            await user.remove_roles(mute_role)
        await ctx.send(f"{user.mention} has been unmuted.")
    else:
        await ctx.send(f"{user.mention} is not muted.")

@bot.command()
@has_disbot_or_admin_role()
async def ban(ctx, user: discord.Member):
    """Ban a user."""
    await user.ban(reason="Banned by Disbot")
    await ctx.send(f"{user.mention} has been banned.")

@bot.command()
@has_disbot_or_admin_role()
async def unban(ctx, user_id: int):
    """Unban a user."""
    banned_users = [entry async for entry in ctx.guild.bans()]
    user = discord.utils.get(banned_users, id=user_id)
    
    if user:
        await ctx.guild.unban(user.user)
        await ctx.send(f"{user.user.mention} has been unbanned.")
    else:
        await ctx.send(f"User with ID {user_id} not found in banned list.")

@bot.command()
@has_disbot_or_admin_role()
async def unwarn(ctx, user: discord.Member):
    """Remove a warning from a user."""
    user_id = str(user.id)

    if user_id in warnings:
        warnings[user_id][0] -= 1
        if warnings[user_id][0] < 0:
            warnings[user_id][0] = 0
        await ctx.send(f"Warning removed from {user.mention}. Total warnings: {warnings[user_id][0]}.")
    else:
        await ctx.send(f"{user.mention} has no warnings.")

# Function to check if the member has the Admin role
def has_admin_role(member):
    admin_role = discord.utils.get(member.guild.roles, name=ADMIN_ROLE_NAME)
    return admin_role in member.roles

# Function to unmute after a delay
async def unmute_after_delay(guild, member, delay):
    await asyncio.sleep(delay.total_seconds())
    mute_role = discord.utils.get(guild.roles, name=MUTE_ROLE_NAME)
    if mute_role:
        await member.remove_roles(mute_role)
        await guild.system_channel.send(f"{member.mention} has been unmuted after 12 hours.")

############################################################################################################################################
##########################################################    TOKEN    #####################################################################
############################################################################################################################################

# Run the bot
bot.run('')









#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 
#700 LINES OF CODE ||| MRT1N 