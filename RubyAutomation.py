# Most of the code made by Java#9999 -  Modified by silver
import pip 
try:
    import discord
    from discord.ext import commands
    import json 
    import aiohttp 
    from discord import Embed, Colour
    from discord import Game
    from robloxapi import Client
    import httpx 
    import asyncio 
    import os 
    import time 
    import subprocess 
    from io import BytesIO 
    import sys 
    import requests 
    import psutil
    import signal
    import platform 
    from typing import Union 
    from discord import Webhook 
    from urllib.parse import urlparse
    import threading 
except ModuleNotFoundError:
    invalidModuleInput = input("A module was not found. Do you want to try launch install on all the modules? (y/n): ")  
    if invalidModuleInput.lower() == "y":
        pip.main(['install', "psutil"])
        pip.main(['install', "discord.py"])
        pip.main(['install', "robloxapi"])
        pip.main(['install', "aiohttp"])
        pip.main(['install', "pillow"])
        ask = input("Installed all the modules. Please restart the script to try again. Installation finished.")
        exit()
    else:
        ask = input("Installation finished.")
        exit()

scriptVersion = 5
def whichPythonCommand():
    LocalMachineOS = platform.system()
    if (
        LocalMachineOS == "win32"
        or LocalMachineOS == "win64"
        or LocalMachineOS == "Windows"
        # or LocalMachineOS == "Linux" # temporarily removed, cba to fix
        # or LocalMachineOS == "macOS" # temporarily removed, cba to fix
        or LocalMachineOS == "Android"
    ):
        return "python"

if whichPythonCommand() == "python":
    os.system("cls")

def versionChecker():
    embed_count = 0
    while True:
        response = requests.get(
            "https://pastebin.com/raw/NMkCvD90"
        )
        if response:
            response1 = response.text
            final = int(response1)
            if scriptVersion == final:
                print("Extension is on the latest version :)")
            else:
                print("Extension has a new update! Sending webhook!")

                # Read the settings.json file right before sending the embed
                with open('settings.json', 'r') as f:
                    settings = json.load(f)

                authorized_ids = settings["MISC"]["DISCORD"]["AUTHORIZED_IDS"]
                pings = ""
                for random_idwoahh in authorized_ids:
                    pings = pings + f"<@{random_idwoahh}> "
                webhook_url = settings["MISC"]["WEBHOOK"]["URL"]
                newJSONData = {
                    "content": pings,
                    "embeds": [
                        {
                            "title": "New version!",
                            "description": f" ```Detected new update in https://github.com/epicofcats/RubyAutomation ```",
                            "color": 16758465,
                            "footer": {
                                "text": "The current version will still work."
                            }
                        }
                    ]
                }

                embed_webhook_response = requests.post(webhook_url, json=newJSONData)
                if embed_webhook_response.status_code != 204:
                    print(
                        f"Failed to send the embed to the webhook. HTTP status: {embed_webhook_response.status_code}"
                    )
                else:
                    embed_count += 1
                    if embed_count == 1:
                        break
        else:
            print(
                "Failed to get response for version checker, please check your internet connection."
            )
        time.sleep(60*10)

def get_thumbnail(item_id) -> str:
    res = requests.get(f'https://thumbnails.roblox.com/v1/assets?assetIds={item_id}&size=420x420&format=Png').json()
    return res['data'][0]['imageUrl']

#Load Settings
with open('settings.json') as f:
    settings = json.load(f)

print("Welcome to Ruby Extension")
print("Device OS: " + platform.system())
print("Python Version: " + sys.version)


#Variables
ROBLOX_API_URL = "https://users.roblox.com/v1/users/authenticated"   
webhook_url = settings['MISC']['WEBHOOK']['URL']
autorestart_notify_enabled = True
intents = discord.Intents.default()
intents.message_content = True    
intents.messages = True
autorestart_task = None
autorestart_minutes = None
notify_on_restart = False
start_time = None
print_cache = {}
discord_ids = settings['MISC']['DISCORD']['AUTHORIZED_IDS'][0]
discord_id = discord_ids

#Class
class MyBot(commands.AutoShardedBot):
    async def on_socket_response(self, msg):
        self._last_socket_response = time.time()

    async def close(self):
        if self._task:
            self._task.cancel()
        await super().close()

    async def on_ready(self):
        if not hasattr(self, "_task"):
            self._task = self.loop.create_task(self.check_socket())

    async def check_socket(self):
        while not self.is_closed():
            if time.time() - self._last_socket_response > 60:
                await self.close()
                await self.start(bot_token)
            await asyncio.sleep(5)


bot = MyBot(command_prefix='!', intents=intents)
bot._last_socket_response = time.time()

#Functions
def bot_login(token, ready_event):
    intents = discord.Intents.default()
    intents.message_content = True  
    bot = commands.Bot(command_prefix="!",
                       intents=intents)

def is_owner(): 
    async def predicate(ctx):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        authorized_ids = [int(x) for x in settings['MISC']['DISCORD']['AUTHORIZED_IDS']]
        return ctx.author.id in authorized_ids
    return commands.check(predicate)

def load_settings():
    with open("settings.json") as f:
        return json.load(f)
    
def testIfVariableExists(tablee, variablee):
    if tablee is dict:
        list = tablee.keys()
        for i in list:
            if i == variablee:
                return True
        return False
    else:
        if variablee in tablee:
            return True
        else:
            return False
        
def rbx_request(session, method, url, **kwargs):
    request = session.request(method, url, **kwargs)
    method = method.lower()
    if (method == "post") or (method == "put") or (method == "patch") or (method == "delete"):
        if "X-CSRF-TOKEN" in request.headers:
            session.headers["X-CSRF-TOKEN"] = request.headers["X-CSRF-TOKEN"]
            if request.status_code == 403:  # Request failed, send it again
                request = session.request(method, url, **kwargs)
    return request
    
def restart_main_py():
    global mewtSession
    if mewtSession:
        for proc in psutil.process_iter():
            name = proc.name()
            if name == "python.exe":
                cmdline = proc.cmdline()
                if "main.py" in cmdline[1]:
                    pid = proc.pid
                    os.kill(pid, signal.SIGTERM)
        mewtSession = subprocess.Popen([sys.executable, "main.py"])
    else:
        print("WARNING! Mewt Process was not found! Using old restarter!")
        for proc in psutil.process_iter():
            name = proc.name()
            if name == "python.exe":
                cmdline = proc.cmdline()
                if "main.py" in cmdline[1]:
                    pid = proc.pid
                    os.kill(pid, signal.SIGTERM)
        mewtSession = subprocess.Popen([sys.executable, "main.py"])

async def restart_bot(ctx):
    try:
        restart_main_py()
    except Exception as e:
        pass

async def autorestart_task_fn(minutes, ctx):
    global notify_on_restart
    while True:
        await asyncio.sleep(minutes * 60)

        ## Item check
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
            watchlist = settings["MISC"]["WATCHER"]["ITEMS"]

            cookieToUse = settings["AUTHENTICATION"]["DETAILS_COOKIE"]
            dataToUse = {
                "items": [] 
            }

            for item in watchlist:
                dataToUse["items"].append(
                    {"itemType": 1,"id": item}
                )

            session = requests.Session()
            session.cookies[".ROBLOSECURITY"] = cookieToUse
            session.headers["accept"] = "application/json"
            session.headers["Content-Type"] = "application/json"
            listRemoved = ""

            request = rbx_request(session=session, method="POST", url="https://catalog.roblox.com/v1/catalog/items/details", data=json.dumps(dataToUse))
            item = request.json()

            if request.status_code == 200 and item.get("data"):
                for item_data in item["data"]:
                    if testIfVariableExists(item_data, "unitsAvailableForConsumption") and testIfVariableExists(item_data, "totalQuantity"): 
                        if item_data["unitsAvailableForConsumption"] == 0:
                            settings["MISC"]["WATCHER"]["ITEMS"].remove(item_data["id"])
                            listRemoved = listRemoved + f"`{str(item_data['id'])}` ({str(item_data['name'])}) \n"
                    elif testIfVariableExists(item_data, "price"):
                        settings["MISC"]["WATCHER"]["ITEMS"].remove(item_data["id"])
                        listRemoved = listRemoved + f"`{str(item_data['id'])}` \n"

                if listRemoved == "":
                    listRemoved = "No items found to be removed!"
                else:
                    with open("settings.json", "w") as f:
                        json.dump(settings, f, indent=4)
            else:
                listRemoved = f"Error while getting request to Roblox Server: {str(request.status_code)}"
        except Exception as e:
            print("Error while updating watchlist:" + e)
            listRemoved = "Error while updating watchlist"
        ## Main

        if notify_on_restart:
            embed = Embed(
                title="Restart Success!",
                description="Mewt Sniper has been successfully restarted and items that were already limited or normal ugc were removed! Items Removed: \n" + listRemoved, 
                color=0xFFB6C1
            )
            await ctx.send(embed=embed)
        restart_main_py()

async def send_cookie_invalid_webhook(cookie_name, command_name):
    webhook_url = settings['MISC']['WEBHOOK']['URL']
    embed = discord.Embed(
        title="Cookie check notification!",
        description=f" ``` The {cookie_name} has become invalid. Please update it by using the command !{command_name}. ```",
        color=discord.Color.red()
    )
    embed_dict = embed.to_dict()

    async with aiohttp.ClientSession() as session:
        async with session.post(
            webhook_url,
            json={
                "embeds": [embed_dict],
                "username": bot.user.name,
                "avatar_url": str(bot.user.avatar.url) if bot.user.avatar else None,
            },
        ) as response:
            if response.status != 204:
                print(f"Failed to send the embed to the webhook. HTTP status: {response.status}")

async def check_cookie(cookie):
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        return True, username
    else:
        return False, None

def update_settings(new_settings):
    with open("settings.json", "w") as file:
        json.dump(new_settings, file, indent=4)

async def get_user_id_from_cookie(cookie):
    api_url = "https://www.roblox.com/mobileapi/userinfo"
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data["UserID"]
    else:
        return None




#Events
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = Embed(title="Error", description=" ```Only the owner can use such commands. ```", color=Colour.red())
        return
        # await ctx.send(embed=embed)

@bot.event
async def on_ready():
    global start_time
    start_time = time.time()
    os.system("cls" if os.name == "nt" else "clear")

    print("Ruby Extension is now running in background!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Free UGC lims, !info for more"))
    print(f"Logged in as bot: {bot.user.name}")

    cookies = settings["AUTHENTICATION"]["COOKIES"]
    details_cookie = settings["AUTHENTICATION"]["DETAILS_COOKIE"]

    versionCheck = threading.Thread(target=versionChecker)
    versionCheck.start()

    # checkValueThread = threading.Thread(target=checkValue)
    # checkValueThread.start()

    checks = 0
    while True:
        checks += 1

        # Check all cookies
        for i, cookie in enumerate(cookies, start=1):
            cookie_valid, username = await check_cookie(cookie)
            if not cookie_valid:
                await send_cookie_invalid_webhook(f"COOKIE_{i}", f"cookie{i}")

        # Check DETAILS_COOKIE
        details_cookie_valid, details_username = await check_cookie(details_cookie)
        if not details_cookie_valid:
            await send_cookie_invalid_webhook("DETAILS_COOKIE", "altcookie")

        # Wait for 5 minutes before checking again
        await asyncio.sleep(300)





#Commands:

#prefix command
@bot.command()
@is_owner()
async def prefix(ctx, new_prefix: str):
    bot.command_prefix = new_prefix
    await bot.change_presence(activity=Game(name=f"{new_prefix}info"))
    embed = discord.Embed(
        title="Prefix Update",
        description=f"```Successfully changed the command prefix to: {new_prefix}```\n \nNote that for a better user experience the prefix dosen't save, so if you close the sniper the prefix will go back to !",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    await ctx.send(embed=embed)

#screenshot
@bot.command()
@is_owner()
async def screenshot(ctx):
    # Capture the screenshot
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
    except ImportError:
        await ctx.send("Failed to capture screenshot. Please make sure you have the Pillow library installed.")
        return

    # Convert the image to bytes
    image_bytes = BytesIO()
    screenshot.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # Read the webhook URL from the settings
    webhook_url = settings['MISC']['WEBHOOK']['URL']

    # Create a Discord file object from the image bytes
    file = discord.File(image_bytes, filename='screenshot.png')

    # Send the screenshot as an embed to the webhook
    embed = discord.Embed()
    embed.set_image(url='attachment://screenshot.png')

    async with ctx.typing():
        try:
            await ctx.send(file=file, embed=embed)
        except discord.HTTPException:
            await ctx.send("Failed to send the screenshot to the webhook.")

#webhook command
@bot.command() 
@is_owner()
async def webhook(ctx, webhook_url: str):
    
    with open('settings.json', 'r') as f:
        settings = json.load(f)


    
    settings['MISC']['WEBHOOK']['URL'] = webhook_url

    
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    
    embed = discord.Embed(
        title="Success!",
        description=" ``` This webhook has been succesfully set and will be used for the next notifications! ```",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    
    embed_dict = embed.to_dict()

    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            webhook_url,
            json={
                "embeds": [embed_dict],
                "username": bot.user.name,
                "avatar_url": str(bot.user.avatar.url) if bot.user.avatar else None,
            },
        ) as response:
            if response.status != 204:
                await ctx.send(f"Failed to send the embed to the webhook. HTTP status: {response.status}")
                return
            
            if await restart_main_py():
               print("Succesfully restarted mewt after updating the webhook")
            else:
               print("Error while trying to restart mewt after updating the webhook.")


#ping
@bot.command()
async def ping(ctx):
    message = f"Pong! {round(bot.latency * 1000)}ms"
    await ctx.send(message)

#onlyfree command
@bot.command(name='onlyfree')  
@is_owner()
async def onlyfree(ctx, status: str):
    if status.lower() not in ['on', 'off']:
        embed = Embed(title='Error', description='```Please use !onlyfree on or !onlyfree off```', color=Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        return

  
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    
    if status.lower() == 'on':
        settings['MISC']['WATCHER']['ONLY_FREE'] = True
        description = 'Mewt sniper will now only snipe free items. Run !onlyfree off to deactivate this setting.'
    else:
        settings['MISC']['WATCHER']['ONLY_FREE'] = False
        description = 'Mewt sniper will now snipe paid items too. Run !onlyfree on to activate this setting.'

    
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = Embed(title='Success!', description=f'```{description}```', color=Colour.from_rgb(255, 182, 193))
    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Succesfully restarted mewt after updating the onlyfree option")
    else:
            print("Error while trying to restart mewt after updating the onlyfree option.")

#speed command
@bot.command(name='speed')  
@is_owner()
async def speed(ctx, new_speed: str):
    try:
        new_speed_float = float(new_speed)
    except ValueError:
        embed = Embed(title=' ```The scan speed must be a number. ```', color=Colour.from_rgb(255, 0, 0))
        await ctx.send(embed=embed)
        return

    
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    
    if new_speed_float.is_integer():
        new_speed_str = str(int(new_speed_float))
        new_speed_value = int(new_speed_float)
    else:
        new_speed_str = str(new_speed_float)
        new_speed_value = new_speed_float

   
    settings['MISC']['WATCHER']['SCAN_SPEED'] = new_speed_value

    
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = Embed(title='Success!', description=f'```New scan speed: {new_speed_str}```', color=Colour.from_rgb(255, 182, 193))
    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Succesfully restarted mewt after updating the speed")
    else:
            print("Error while trying to restart mewt after updating the speed.")

# buy debounce command
@bot.command(name="buy_debounce")
@is_owner()
async def buy_debounce(ctx, new_debounce: str):
    try:
        new_debounce_float = float(new_debounce)
    except ValueError:
        embed = Embed(
            title=" ```The buy debounce must be a number. ```",
            color=Colour.from_rgb(255, 0, 0),
        )
        await ctx.send(embed=embed)
        return

    with open("settings.json", "r") as f:
        settings = json.load(f)

    if new_debounce_float.is_integer():
        new_debounce_str = str(int(new_debounce_float))
        new_debounce_value = int(new_debounce_float)
    else:
        new_debounce_str = str(new_debounce_float)
        new_debounce_value = new_debounce_float

    settings["MISC"]["BUY_DEBOUNCE"] = new_debounce_value

    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

    embed = Embed(
        title="Success!",
        description=f"```New buy debounce: {new_debounce_str}```",
        color=Colour.from_rgb(255, 182, 193),
    )
    await ctx.send(embed=embed)

    if await restart_main_py():
        print("Succesfully restarted mewt after updating the buy debounce")
    else:
        print("Error while trying to restart mewt after updating the buy debounce.")

#info command
@bot.command()
@is_owner()
async def info(ctx):
    prefix = bot.command_prefix
    embed = discord.Embed(
        title="Ruby Extension Commands:",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    embed.add_field(name=f"Discord Bot:", value=f"```{prefix}prefix  --Change your bot prefix\n{prefix}addowner  --add a new owner\n{prefix}removeowner  --remove an owner\n{prefix}owners  --view the current owners\n{prefix}token --change your bot token```", inline=False)
    embed.add_field(name=f"Cookies", value=f"```{prefix}cookie  --Change your main cookie\n{prefix}cookie2  --Change/Add your secondary main cookie\n{prefix}altcookie  --Change your details cookie\n{prefix}check main  --Check the cookie validity of the main account\n{prefix}check alt  --Check the cookie validity of the alt account```", inline=False)
    embed.add_field(
        name=f"Mewt Sniper:",
        value=f"```{prefix}add_link  --Add an item ID from its link [LINK SHOULD NOT HAVE A SLASH AT THE END OR IN THE ITEM'S NAME]\n{prefix}webhook  --Change your webhook\n{prefix}speed  --Change your scan speed\n{prefix}onlyfree on  --Only snipe free limiteds\n{prefix}onlyfree off  --Snipe paid limiteds too\n!add  --Add an item ID to the searcher\n!remove --Remove an item from the searcher\n!watching --Shows the list of items you are watching\n!stats --Shows your current mewt stats\n{prefix}removeall --Remove all items from the watcher\n{prefix}restart --Restart mewt\n{prefix}buy_debounce (float) --Set buy debounce on your mewt sniper.\n{prefix}autorestart (minutes) --Autorestart mewt every tot. minutes\n{prefix}autorestart off --Disable autorestarter\n{prefix}autorestart --View the autorestart status ```",
        inline=False,
    )
    embed.add_field(
        name=f"Mewt Sniper (2nd Part):",
        value=f"```{prefix}autosearch on --Enable autosearch\n{prefix}autosearch off --Disable autosearch\n{prefix}viewWatching --View all data of the items inside your watchlist.\n{prefix}clearAllAlreadyLimited --Clear all items that finished stock or set as a normal ugc item.\n{prefix}addwl --Add a whitelisted creator\n{prefix}removewl  --Remove a whitelisted creator\n{prefix}whitelist --View the whitelisted creators\n{prefix}paid_on --Set the paid autosearch on\n{prefix}paid_off --Set the autosearch paid off\n{prefix}maxstock --Set the max stock for the paid autosearch\n{prefix}maxprice --Set the max price for the paid autosearch ```",
        inline=False,
    )
    embed.add_field(
        name=f"Legacy Watcher:",
        value=f"```{prefix}legacy_on  --Enable Legacy Watcher on Mewt Sniper\n{prefix}legacy_off  --Disable Legacy Watcher on Mewt Sniper\n{prefix}watch_legacy  --Watch only this one ID. IDS CANNOT BE REVERTED AFTER COMMAND RAN\n{prefix}add_legacy  --Add an ID to your legacy watcher \n{prefix}link_legacy  --Watch only this one ID from a link. [LINK SHOULD NOT HAVE A SLASH AT THE END OR IN THE ITEM'S NAME, IDS CANNOT BE REVERTED AFTER COMMAND RAN]  ```",
        inline=False,
    )
    embed.add_field(name=f"Utilitys", value=f"```{prefix}more  --Look at some general information\n{prefix}ping  --Check the bot response time\n{prefix}screenshot --Screenshot your mewt```", inline=False)   
    embed.set_footer(text="Originally by Java#9999 - Modified by silver")
    await ctx.author.send(embed=embed)

#remove all command
@bot.command()
@is_owner()
async def removeall(ctx):
    settings = load_settings()
    settings["MISC"]["WATCHER"]["ITEMS"] = []
    update_settings(settings)

    embed = Embed(title="Items Removed", description="All items have been removed.", color=discord.Color.from_rgb(255, 182, 193))
    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Bot restarted after updating the cookie.")
    else:
            print("Error while trying to restart the bot after updating the cookie.")

#add owner
@bot.command()
@is_owner()
async def addowner(ctx, user_id: int):
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    
    authorized_ids = settings["MISC"]["DISCORD"]["AUTHORIZED_IDS"]
    
    if str(user_id) not in authorized_ids:
        authorized_ids.append(str(user_id))
        settings["MISC"]["DISCORD"]["AUTHORIZED_IDS"] = authorized_ids
        
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)
        
        embed = discord.Embed(
            title="Owner Added",
            description=f"```User ID {user_id} has been added as an owner.```",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error",
            description=f"```User ID {user_id} is already an owner.```",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        await ctx.send(embed=embed)
#remove owner
@bot.command()
@is_owner()
async def removeowner(ctx, user_id: int):
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    authorized_ids = settings["MISC"]["DISCORD"]["AUTHORIZED_IDS"]
    if str(user_id) in authorized_ids:
        authorized_ids.remove(str(user_id))
        settings["MISC"]["DISCORD"]["AUTHORIZED_IDS"] = authorized_ids
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)
        embed = discord.Embed(
            title="Owner Removed",
            description=f"```User ID {user_id} has been removed as an owner.```",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error",
            description=f"```User ID {user_id} is not an owner.```",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        await ctx.send(embed=embed)

#owners
@bot.command()
@is_owner()
async def owners(ctx):
    with open('settings.json', 'r') as file:
        settings = json.load(file)
    authorized_ids = settings["MISC"]["DISCORD"]["AUTHORIZED_IDS"]

    # Create an embed with the specified color
    embed = discord.Embed(
        title="Current Owners",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    # Add a field for the owners
    owners_str = "\n".join(authorized_ids)
    embed.add_field(name="Owners", value=owners_str, inline=False)

    # Send the embed message
    await ctx.send(embed=embed)

#restart command
@bot.command()
@is_owner()
async def restart(ctx):
    try:
        restart_main_py()
        embed = Embed(title="Success!", description="Successfully restarted the bot.", color=Colour.from_rgb(255, 182, 193))
        await ctx.send(embed=embed)
    except Exception as e:
        embed = Embed(title="Error", description="An error occurred while trying to restart the bot: {}".format(str(e)), color=Colour.red())
        await ctx.send(embed=embed)

#More command
@bot.command(pass_context = True)
@is_owner()
async def more(ctx):
    settings = load_settings()

    
    main_cookie = settings["AUTHENTICATION"]["COOKIES"][0]
    details_cookie = settings["AUTHENTICATION"]["DETAILS_COOKIE"]
    owner_id = settings['MISC']['DISCORD']['AUTHORIZED_IDS']
    onlyfree = settings['MISC']['WATCHER']['ONLY_FREE']
    autorestart_status = "Off" if autorestart_task is None or autorestart_task.cancelled() else f"{autorestart_minutes} minutes"
    scan_speed = settings['MISC']['WATCHER']['SCAN_SPEED']
    prefix = bot.command_prefix
    items = settings["MISC"]["WATCHER"]["ITEMS"]
    watching = ', '.join(str(item) for item in items)

    main_cookie_valid, main_username = await check_cookie(main_cookie)
    details_cookie_valid, details_username = await check_cookie(details_cookie)

    if start_time is not None:
        runtime = int(time.time() - start_time)
        minutes, seconds = divmod(runtime, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        runtime = f"{days} days, {hours} hours, {minutes} minutes and {seconds} seconds"
    else:
        runtime = "Unknown"


    embed = discord.Embed(title=f"Hi, {ctx.message.author.name}! 👋", color=discord.Color.from_rgb(255, 182, 193))
    embed.add_field(name="Prefix:", value=prefix, inline=False)
    embed.add_field(name="Roblox main:", value=main_username if main_cookie_valid else "Invalid cookie", inline=False)
    embed.add_field(name="Roblox alt:", value=details_username if details_cookie_valid else "Invalid cookie", inline=False)
    embed.add_field(name="Current owner id:", value=owner_id, inline=False)
    embed.add_field(name="Onlyfree:", value="On" if onlyfree else "Off", inline=False)
    embed.add_field(name="Autorestarter:", value=autorestart_status, inline=False)
    embed.add_field(name="Scan speed:", value=scan_speed, inline=False)
    embed.add_field(name="Watching:", value=watching if watching else "No items", inline=False)
    embed.add_field(name="Runtime:", value=runtime, inline=False)
    embed.set_footer(text="Originally by Java#9999 - Modified by silver")
    await ctx.reply(embed=embed)

#cookie command
@bot.command()
@is_owner()
async def cookie(ctx, new_cookie: str):
    
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={new_cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        user_id = user_data["id"]

        
        avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        async with httpx.AsyncClient() as client:
            avatar_response = await client.get(avatar_api_url)
        avatar_data = avatar_response.json()
        avatar_url = avatar_data["data"][0]["imageUrl"]

        
        with open('settings.json', 'r') as f:
            settings = json.load(f)

        
        settings["AUTHENTICATION"]["COOKIES"][0] = new_cookie

        
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

        
        embed = discord.Embed(
            title="MAIN Cookie Update",
            description=f" ```The MAIN cookie was valid for the username: {username}```\n  \n **If the bot dosen't react to !stats it means that either your main/alt cookie was invalid. In this case update them.** ",
            color=discord.Color.from_rgb(255, 182, 193)
        )

       
        embed.set_thumbnail(url=avatar_url)

        
        await ctx.send(embed=embed)

        
        if await restart_main_py():
            print("Bot restarted after updating the cookie.")
        else:
            print("Error while trying to restart the bot after updating the cookie.")

    else:
        
        embed = discord.Embed(
            title="Error",
            description=" ```The cookie you have input was invalid. ```",
            color=discord.Color.red()
        )

        
        await ctx.send(embed=embed)

#cookie2 command
@bot.command()
@is_owner()
async def cookie2(ctx, new_cookie: str):
    
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={new_cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        user_id = user_data["id"]

        
        avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        async with httpx.AsyncClient() as client:
            avatar_response = await client.get(avatar_api_url)
        avatar_data = avatar_response.json()
        avatar_url = avatar_data["data"][0]["imageUrl"]

        
        with open('settings.json', 'r') as f:
            settings = json.load(f)

        
        if len(settings["AUTHENTICATION"]["COOKIES"]) >= 2:
            settings["AUTHENTICATION"]["COOKIES"][1] = new_cookie
        else:
            settings["AUTHENTICATION"]["COOKIES"].append(new_cookie)

        
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

        
        embed = discord.Embed(
            title="SECONDARY Cookie Update",
            description=f" ```The SECONDARY cookie was valid for the username: {username}```\n  \n **If the bot doesn't react to !stats it means that either your main/alt cookie was invalid. In this case update them.** ",
            color=discord.Color.from_rgb(255, 182, 193)
        )

       
        embed.set_thumbnail(url=avatar_url)

        
        await ctx.send(embed=embed)

        
        if await restart_main_py():
            print("Bot restarted after updating the cookie.")
        else:
            print("Error while trying to restart the bot after updating the cookie.")

    else:
        
        embed = discord.Embed(
            title="Error",
            description=" ```The cookie you have input was invalid. ```",
            color=discord.Color.red()
        )

        
        await ctx.send(embed=embed)

#altcookie command
@bot.command() 
@is_owner()
async def altcookie(ctx, new_cookie: str):
    
    async with httpx.AsyncClient() as client:
        headers = {"Cookie": f".ROBLOSECURITY={new_cookie}"}
        response = await client.get(ROBLOX_API_URL, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        username = user_data["name"]
        user_id = user_data["id"]

        
        avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
        async with httpx.AsyncClient() as client:
            avatar_response = await client.get(avatar_api_url)
        avatar_data = avatar_response.json()
        avatar_url = avatar_data["data"][0]["imageUrl"]

        
        with open('settings.json', 'r') as f:
            settings = json.load(f)

        
        settings["AUTHENTICATION"]["DETAILS_COOKIE"] = new_cookie

        
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

       
        embed = discord.Embed(
            title="ALT Cookie Update",
            description=f" ```The ALT cookie was valid for the username: {username} ```\n  \n **If the bot dosen't react to !stats it means that either your main/alt cookie was invalid. In this case update them.** '",
            color=discord.Color.from_rgb(255, 182, 193)
        )

        
        embed.set_thumbnail(url=avatar_url)

        
        await ctx.send(embed=embed)

         
        if await restart_main_py():
            print("Bot restarted after updating the ALT cookie.")
        else:
            print("Error while trying to restart the bot after updating the cookie.")


    else:
        
        embed = discord.Embed(
            title="Error",
            description=" ```The cookie you have input was invalid. ```",
            color=discord.Color.red()
        )

       
        await ctx.send(embed=embed)

#token command
@bot.command()  
@is_owner()
async def token(ctx, new_token: str):
    
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    
    settings['MISC']['DISCORD']['TOKEN'] = new_token

    
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    
    embed = discord.Embed(
        title="Token Update",
        description=" ``` Successfully changed the discord bot TOKEN, make sure that you have invited the new bot to the server. ```",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Bot restarted after updating the token.")
    else:
            print("Error while trying to restart the bot after updating the token.")

#autosearch command
@bot.command()
@is_owner()
async def autosearch(ctx, status: str):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    if status.lower() == "on":
        settings['MISC']['AUTOSEARCH']['ENABLE'] = True
        message = "Autosearch has been turned on."
    elif status.lower() == "off":
        settings['MISC']['AUTOSEARCH']['ENABLE'] = False
        message = "Autosearch has been turned off."
    else:
        await ctx.send("Invalid status. Please use 'on' or 'off'.")
        return

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="Autosearch Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Bot restarted after updating the autosearch")
    else:
            print("Error while trying to restart the bot after updating the autosearch")


#whitelist
@bot.command()
@is_owner()
async def addwl(ctx, creator: str):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    if creator not in settings['MISC']['AUTOSEARCH']['WHITELISTED_CREATORS']:
        settings['MISC']['AUTOSEARCH']['WHITELISTED_CREATORS'].append(creator)
        message = f"{creator} has been added to the whitelist."
    else:
        message = f"{creator} is already in the creators whitelist."

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="Whitelist Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    await ctx.send(embed=embed)

    if await restart_main_py():
            print("Bot restarted after updating the autosearch")
    else:
            print("Error while trying to restart the bot after updating the autosearch")

#unwhitelist
@bot.command()
@is_owner()
async def removewl(ctx, creator: str):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    if creator in settings['MISC']['AUTOSEARCH']['WHITELISTED_CREATORS']:
        settings['MISC']['AUTOSEARCH']['WHITELISTED_CREATORS'].remove(creator)
        message = f"{creator} has been removed from the creators whitelist."
    else:
        message = f"{creator} is not in the creators whitelist."

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="Whitelist Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    await ctx.send(embed=embed)
    if await restart_main_py():
            print("Bot restarted after updating the autosearch")
    else:
            print("Error while trying to restart the bot after updating the autosearch")

#view whitelist
@bot.command()
@is_owner()
async def whitelist(ctx):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    whitelisted_creators = settings['MISC']['AUTOSEARCH']['WHITELISTED_CREATORS']
    if len(whitelisted_creators) > 0:
        message = "The current whitelisted creators are:\n" + "\n".join(whitelisted_creators)
    else:
        message = "There are no whitelisted creators."

    embed = discord.Embed(
        title="Whitelist Status",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )

    await ctx.send(embed=embed)

#Autorestart command
@bot.command()
@is_owner()
async def autorestart(ctx, minutes: Union[int, str] = None):
    global autorestart_task, autorestart_minutes, notify_on_restart

    async def wait_for_response(ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await bot.wait_for("message", check=check, timeout=60)
            return response.content.lower()
        except asyncio.TimeoutError:
            return None

    if minutes is None:
        if autorestart_task is not None and not autorestart_task.cancelled():
            embed = Embed(title="Autorestart Status", color=Colour.from_rgb(255, 182, 193))
            embed.add_field(name="Status", value="Autorestart is currently enabled.")
            embed.add_field(name="Minutes", value=f"Restarting every {autorestart_minutes} minutes.")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Autorestart Status", color=Colour.from_rgb(255, 182, 193))
            embed.add_field(name="Status", value="Autorestart is currently disabled.")
            await ctx.send(embed=embed)
    elif isinstance(minutes, str) and minutes.lower() == "off":
        if autorestart_task is not None and not autorestart_task.cancelled():
            autorestart_task.cancel()
            autorestart_task = None
            autorestart_minutes = None
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(255, 182, 193))
            embed.add_field(name="Status", value="Autorestart has been disabled.")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(255, 182, 193))
            embed.add_field(name="Status", value="Autorestart is already disabled.")
            await ctx.send(embed=embed)
    elif isinstance(minutes, int) and minutes == 0:
        if autorestart_task is not None and not autorestart_task.cancelled():
            autorestart_task.cancel()
            autorestart_task = None
            autorestart_minutes = None
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(255, 182, 193))
            embed.add_field(name="Status", value="Autorestart has been disabled.")
            await ctx.send(embed=embed)
        else:
            embed = Embed(title="Autorestart Disabled", color=Colour.from_rgb(255, 182, 193))
            embed.add_field(name="Status", value="Autorestart is already disabled.")
            await ctx.send(embed=embed)
    else:
        if autorestart_task is not None and not autorestart_task.cancelled():
            autorestart_task.cancel()

        await ctx.send("Would you like to receive notifications on every restart? (yes/no)")
        response = await wait_for_response(ctx)

        if response == "yes":
            notify_on_restart = True
            success_msg = "Enabled"
        else:
            notify_on_restart = False
            success_msg = "Disabled"

        autorestart_task = bot.loop.create_task(autorestart_task_fn(minutes, ctx))
        autorestart_minutes = minutes

        embed = Embed(title="Autorestart Enabled", color=Colour.from_rgb(255, 182, 193))
        embed.add_field(name="Status", value="Autorestart has been enabled.")
        embed.add_field(name="Minutes", value=f"Restarting every {minutes} minutes.")
        embed.add_field(name="Notification", value=success_msg)
        await ctx.send(embed=embed)

# legacy watcher on
@bot.command()
@is_owner()
async def legacy_on(ctx):
    with open("settings.json", "r") as f:
        settings = json.load(f)

    settings["MISC"]["WATCHER"]["USE_LEGACY_WATCHER"] = True
    message = "The USE_LEGACY_WATCHER option has been turned on."

    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="USE_LEGACY_WATCHER Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193),
    )
    restart_main_py()

    await ctx.send(embed=embed)

# legacy watcher watch
@bot.command()
@is_owner()
async def watch_legacy(ctx, id: int):
    print("Adding legacy id")
    with open("settings.json", "r") as f:
        settings = json.load(f)

    settings["MISC"]["WATCHER"]["ITEMS"] = [id]
    settings["MISC"]["WATCHER"]["USE_LEGACY_WATCHER"] = True

    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

    restart_main_py()
    embed = discord.Embed(
        title="LEGACY_WATCHER Update",
        description=f"```All items that were previously added on the JSON were removed and replaced with following id. If legacy watcher was off, it has been enabled automatically.```",
        color=discord.Color.from_rgb(255, 182, 193),
    )

    await ctx.send(embed=embed)

# legacy watcher watch (but with link :O)
@bot.command()
@is_owner()
async def link_legacy(ctx, *, link: str):
    id_from_link = urlparse(link).path.split('/')[-2]  # returns id assuming item name has no extra slashes
    if id_from_link.isdigit() == False:
        embed = discord.Embed(
        title="Error",
        description=f"```Link format is invalid. Check if link format matches the following: https://www.roblox.com/catalog/12345678901/Item-Name```",
        color=discord.Color.from_rgb(255, 182, 193),
        )     
    else:
        print("Adding legacy id")

        with open("settings.json", "r") as f:
            settings = json.load(f)
        
        settings["MISC"]["WATCHER"]["ITEMS"] = [int(id_from_link)]
        settings["MISC"]["WATCHER"]["USE_LEGACY_WATCHER"] = True

        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)

        restart_main_py()   
        embed = discord.Embed(
        title="LEGACY_WATCHER Update",
        description=f"```All items that were previously added on the JSON were removed and replaced with ID {id_from_link}. If legacy watcher was off, it has been enabled automatically.```",
        color=discord.Color.from_rgb(255, 182, 193),
        )   

    await ctx.send(embed=embed)

# legacy watcher add
@bot.command()
@is_owner()
async def add_legacy(ctx, id: int):
    print("Adding legacy id")
    with open("settings.json", "r") as f:
        settings = json.load(f)

    settings["MISC"]["WATCHER"]["ITEMS"].append(id)
    settings["MISC"]["WATCHER"]["USE_LEGACY_WATCHER"] = True

    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

    restart_main_py()
    embed = discord.Embed(
        title="LEGACY_WATCHER Update",
        description=f"```Item has been added with following id. If legacy watcher was off, it has been enabled automatically.```",
        color=discord.Color.from_rgb(255, 182, 193),
    )

    await ctx.send(embed=embed)

#add link
@bot.command()
@is_owner()
async def add_link(ctx, *, link: str):
    id_from_link = urlparse(link).path.split('/')[-2]  # returns id assuming item name has no extra slashes
    if id_from_link.isdigit() == False:
        embed = discord.Embed(
        title=f"Error",
        description=f"```Link format is invalid. Check if link format matches the following: https://www.roblox.com/catalog/12345678901/Item-Name```",
        color=discord.Color.from_rgb(255, 182, 193),
        ) 
    else:
        with open("settings.json", "r") as f:
            settings = json.load(f)

        settings["MISC"]["WATCHER"]["ITEMS"].append(int(id_from_link))

        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)

        restart_main_py()   
        embed = discord.Embed(
        title=f"Item ID {id_from_link} has been added.",
        color=discord.Color.from_rgb(255, 182, 193),
        )

    await ctx.send(embed=embed)


# legacy watcher on
@bot.command()
@is_owner()
async def legacy_off(ctx):
    with open("settings.json", "r") as f:
        settings = json.load(f)

    settings["MISC"]["WATCHER"]["USE_LEGACY_WATCHER"] = False
    message = "The USE_LEGACY_WATCHER option has been turned off."

    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="USE_LEGACY_WATCHER Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193),
    )
    restart_main_py()

    await ctx.send(embed=embed)

# clear all already limiteds
@bot.command()
@is_owner()
async def clearAllAlreadyLimited(ctx):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    watchlist = settings["MISC"]["WATCHER"]["ITEMS"]

    try:
        listRemoved = "Removed these already out of stock, or normal ugc items: \n"

        cookieToUse = settings["AUTHENTICATION"]["DETAILS_COOKIE"]
        dataToUse = {
            "items": [] 
        }

        for item in watchlist:
            dataToUse["items"].append(
                {"itemType": 1,"id": item}
            )

        session = requests.Session()
        session.cookies[".ROBLOSECURITY"] = cookieToUse
        session.headers["accept"] = "application/json"
        session.headers["Content-Type"] = "application/json"

        request = rbx_request(session=session, method="POST", url="https://catalog.roblox.com/v1/catalog/items/details", data=json.dumps(dataToUse))
        item = request.json()

        if request.status_code == 200 and item.get("data"):
            for item_data in item["data"]:
               if testIfVariableExists(item_data, "unitsAvailableForConsumption") and testIfVariableExists(item_data, "totalQuantity"): 
                   if item_data["unitsAvailableForConsumption"] == 0:
                       settings["MISC"]["WATCHER"]["ITEMS"].remove(item_data["id"])
                       listRemoved = listRemoved + f"`{str(item_data['id'])}` ({str(item_data['name'])}) \n"
               elif testIfVariableExists(item_data, "price"):
                   settings["MISC"]["WATCHER"]["ITEMS"].remove(item_data["id"])
                   listRemoved = listRemoved + f"`{str(item_data['id'])}` \n"

            if listRemoved == "Removed these already out of stock, or normal ugc items: \n":
                embed = discord.Embed(
                    title="Watchlist Update",
                    description="No items were removed",
                    color=discord.Color.from_rgb(255, 182, 193),
                )
            else:
                embed = discord.Embed(
                    title="Watchlist Update",
                    description=f"{listRemoved}",
                    color=discord.Color.from_rgb(255, 182, 193),
                )
                with open("settings.json", "w") as f:
                    json.dump(settings, f, indent=4)
                restart_main_py()

            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to get list and error has been received: " + item["errors"][0]["message"])
    except Exception as e:
        embed = Embed(
            title="Error",
            description="An error occurred while trying to update your watch list: {}".format(
                str(e)
            ),
            color=Colour.red(),
        )
        await ctx.send(embed=embed)

# view all watching items
@bot.command()
@is_owner()
async def viewWatching(ctx):
    with open("settings.json", "r") as f:
        settings = json.load(f)
    watchlist = settings["MISC"]["WATCHER"]["ITEMS"]

    try:
        cookieToUse = settings["AUTHENTICATION"]["DETAILS_COOKIE"]
        dataToUse = {
            "items": [] 
        }

        for item in watchlist:
            dataToUse["items"].append(
                {"itemType": 1,"id": item}
            )

        session = requests.Session()
        session.cookies[".ROBLOSECURITY"] = cookieToUse
        session.headers["accept"] = "application/json"
        session.headers["Content-Type"] = "application/json"

        request = rbx_request(session=session, method="POST", url="https://catalog.roblox.com/v1/catalog/items/details", data=json.dumps(dataToUse))
        item = request.json()
        listOfEmbeds = []

        if request.status_code == 200 and item.get("data"):
            for item_data in item["data"]:
               if testIfVariableExists(item_data, "unitsAvailableForConsumption") and testIfVariableExists(item_data, "totalQuantity"): 
                    embedToAdd =  discord.Embed(
                         title=item_data["name"],
                         url=f"https://www.roblox.com/catalog/{str(item_data['id'])}/",
                         color=discord.Color.from_rgb(255, 182, 193),
                         description=f"Description: {item_data['description']} \nUnits Left: `{str(item_data['unitsAvailableForConsumption'])}/{str(item_data['totalQuantity'])}` \nPrice: `{str(item_data['price'])}` \nCreator: `{item_data['creatorName']}` \nID: {str(item_data['id'])}"
                    )
                    embedToAdd.set_thumbnail(url=get_thumbnail(str(item_data['id'])))
                    listOfEmbeds.append(embedToAdd)
               elif testIfVariableExists(item_data, "price"):
                   embedToAdd =  discord.Embed(
                         title=item_data["name"],
                         url=f"https://www.roblox.com/catalog/{str(item_data['id'])}/",
                         color=discord.Color.from_rgb(255, 182, 193),
                         description=f"Description: {item_data['description']} \nUnits Left: `Item detected not a limited.` \nPrice: `{str(item_data['price'])}` \nCreator: `{item_data['creatorName']}` \nID: {str(item_data['id'])}"
                    )
                   embedToAdd.set_thumbnail(url=get_thumbnail(str(item_data['id'])))
                   listOfEmbeds.append(embedToAdd)
               else:
                   embedToAdd =  discord.Embed(
                         title=item_data["name"],
                         url=f"https://www.roblox.com/catalog/{str(item_data['id'])}/",
                         color=discord.Color.from_rgb(255, 182, 193),
                         description=f"Description: {item_data['description']} \nPrice: `Not for sale` \nCreator: `{item_data['creatorName']}` \nID: {str(item_data['id'])}"
                    )
                   embedToAdd.set_thumbnail(url=get_thumbnail(str(item_data['id'])))
                   listOfEmbeds.append(embedToAdd)
            if listOfEmbeds == []:
                listOfEmbeds.append(discord.Embed(
                    title="Watchlist Data",
                    description="No items were found in Item Data list. Please update your watchlist if you have nothing in your watchlist.",
                    color=discord.Color.from_rgb(255, 182, 193),
                ))
            await ctx.send(embeds=listOfEmbeds)
        else:
            await ctx.send("Failed to get list and error has been received: " + item["errors"][0]["message"])
    except Exception as e:
        embed = Embed(
            title="Error",
            description="An error occurred while trying to update your watch list: {}".format(
                str(e)
            ),
            color=Colour.red(),
        )
        await ctx.send(embed=embed)

#paid on
@bot.command()
@is_owner()
async def paid_on(ctx):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    settings['MISC']['AUTOSEARCH']['BUY_PAID']['ENABLE'] = True
    message = "The BUY_PAID option has been turned on."

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="BUY_PAID Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    restart_main_py()

    await ctx.send(embed=embed)
#paid off
@bot.command()
@is_owner()
async def paid_off(ctx):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    settings['MISC']['AUTOSEARCH']['BUY_PAID']['ENABLE'] = False
    message = "The BUY_PAID option has been turned off."

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="BUY_PAID Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    restart_main_py()

    await ctx.send(embed=embed)
#maxprice
@bot.command()
@is_owner()
async def maxprice(ctx, price: int):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    settings['MISC']['AUTOSEARCH']['BUY_PAID']['MAX_PRICE'] = price
    message = f"The MAX_PRICE value has been set to {price}."

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="MAX_PRICE Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    restart_main_py()

    await ctx.send(embed=embed)
#maxstock
@bot.command()
@is_owner()
async def maxstock(ctx, stock: int):
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    settings['MISC']['AUTOSEARCH']['BUY_PAID']['MAX_STOCK'] = stock
    message = f"The MAX_STOCK value has been set to {stock}."

    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

    embed = discord.Embed(
        title="MAX_STOCK Status Update",
        description=f"```{message}```",
        color=discord.Color.from_rgb(255, 182, 193)
    )
    restart_main_py()

    await ctx.send(embed=embed)
#cookie check
@bot.command()
@is_owner()
async def check(ctx, cookie_type: str):
    if cookie_type.lower() not in ['main', 'alt']:
        await ctx.send('Invalid cookie type. Must be `main` or `alt`.')
        return
    
    with open('settings.json') as f:
        settings = json.load(f)
        
    if cookie_type.lower() == 'main':
        cookies = settings["AUTHENTICATION"]["COOKIES"]
    else: 
        cookies = [settings["AUTHENTICATION"]["DETAILS_COOKIE"]]
    
    for cookie in cookies:
        valid, username = await check_cookie(cookie)

        if valid:
            user_id = await get_user_id_from_cookie(cookie)  # Get the user ID from the cookie
            avatar_api_url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=420x420&format=Png&isCircular=false"
            async with httpx.AsyncClient() as client:
                avatar_response = await client.get(avatar_api_url)
            avatar_data = avatar_response.json()
            avatar_url = avatar_data["data"][0]["imageUrl"]

            embed = Embed(title="Cookie check result:", color=Colour.from_rgb(255, 182, 193))
            embed.add_field(name="Username", value=username)
            embed.add_field(name="Cookie type", value=cookie_type.title())
            embed.set_thumbnail(url=avatar_url)
            await ctx.send(embed=embed)

        else:
            embed = Embed(title="Cookie check result:", description="The {} cookie in your settings was invalid".format(cookie_type), color=Colour.red()) 
            await ctx.send(embed=embed)
    
mewtSession = subprocess.Popen([sys.executable, "main.py"])
bot_token = settings['MISC']['DISCORD']['TOKEN']
bot.run(bot_token)
