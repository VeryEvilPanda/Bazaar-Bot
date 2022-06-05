import os
from dotenv import load_dotenv
import disnake
from disnake.ext import commands, tasks
import requests
import json

load_dotenv()

#Defines the two APIs used in this bot
bazaarResponse = requests.get('https://api.slothpixel.me/api/skyblock/bazaar')
bazaarData = json.loads(bazaarResponse.text)

itemsResponse = requests.get('https://api.hypixel.net/resources/skyblock/items')
itemsData = json.loads(itemsResponse.text)

#Function used later simply to check that the price is a number
def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

#Functions to get data from the APIs
def getID(itemName):
    for item in itemsData['items']:
       if item['name'].lower() == itemName.lower():
           return item['id']

def getName(itemID):
    for item in itemsData['items']:
       if item['id'] == itemID:
           return item['name']

def getBazaar(itemID):
    #This can be used to check if a Skyblock item is available in the bazaar
    if itemID not in bazaarData:
        return None
    sellPrice = round(bazaarData[itemID]['quick_status']['sellPrice'], 1)
    buyPrice = round(bazaarData[itemID]['quick_status']['buyPrice'], 1)
    return sellPrice, buyPrice

#Define intents for bot
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

#Define the bot
bot = commands.Bot(
    command_prefix='-',
    test_guilds=[777652457059647498, 982360255973449789],
    sync_commands_debug=True,
    intents=intents,
    activity = disnake.Streaming(name="/notify", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
)


#Outputs a mesage when bot is online
@bot.event
async def on_ready():
    print("------")
    print(f"Logged in as {bot.user}")
    print("------")
    await notifyTask.start()


#Task to check price of all items in the notifier list
@tasks.loop(seconds=60.0)
async def notifyTask():
    with open('bazaar_bot.txt', 'r') as notifyList:
        for line in notifyList:
            line = line.split()
            if getBazaar(line[1])[1] > float(line[2]):
                notifyEmbed = disnake.Embed(
            title=f"Notifier triggered",
            description=f"The insta-buy price of '{getName(line[1])}' rose above your specified price of {line[2]}!",
            color=0x00ff22)
                panda = await bot.fetch_user(554343055029698571)
                notifyEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
                notifyEmbed.set_thumbnail(url="https://evilpanda.me/files/alert.png")
                user = await bot.fetch_user(line[0])
                await user.send(embed=notifyEmbed)
                print(f"[LOG] Notifier triggered: {user.name} ({user.id}), {line[1]}")


#Slash command for checking the price of items in bazaar
@bot.slash_command()
async def item(inter, name):
    """
    Get the bazaar data for an item

    Parameters
    ----------
    name: The exact item name in Skyblock
    """
    itemID = getID(name)
    if itemID == None:
        errorEmbed = disnake.Embed(
            title=f"Skyblock Item Error",
            description=f"Could not find the item '{name}'. Please make sure this is the exact Skyblock item name.",
            color=0xff0000)
        panda = await bot.fetch_user(554343055029698571)
        errorEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
        await inter.response.send_message(embed=errorEmbed)
    elif getBazaar(itemID) == None:
        name = getName(itemID)
        errorEmbed = disnake.Embed(
            title=f"Bazaar Item Error",
            description=f"The item '{name}' is not available in the bazaar.",
            color=0xff0000)
        panda = await bot.fetch_user(554343055029698571)
        errorEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
        await inter.response.send_message(embed=errorEmbed)
    else:
        name = getName(itemID)
        itemEmbed = disnake.Embed(
            title=f"Bazaar data for {name}",
            description=f"Insta-sell price: {getBazaar(itemID)[0]}\nInsta-buy price: {getBazaar(itemID)[1]}",
            color=0x00ff22)
        panda = await bot.fetch_user(554343055029698571)
        itemEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        try:
            itemEmbed.set_thumbnail(url=f"https://sky.shiiyu.moe/item/{itemID}")
        except: 
            itemEmbed.set_thumbnail(url=f"https://evilpanda.me/files/data.png")
        await inter.response.send_message(embed=itemEmbed)

#Main slash command for notifiers
@bot.slash_command()
async def notify(inter):
    pass

#Sub command for creating a notifier
@notify.sub_command()
async def add(inter, name, price):
    """
    Notifies you in DMs when an an item's insta-buy price goes above a fixed price

    Parameters
    ----------
    name: The exact item name in Skyblock
    price: The price threshold
    """
    itemID = getID(name)
    if itemID == None:
        errorEmbed = disnake.Embed(
            title=f"Skyblock Item Error",
            description=f"Could not find the item '{name}'. Please make sure this is the exact Skyblock item name.",
            color=0xff0000)
        panda = await bot.fetch_user(554343055029698571)
        errorEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
        await inter.response.send_message(embed=errorEmbed)
    elif getBazaar(itemID) == None:
        name = getName(itemID)
        errorEmbed = disnake.Embed(
            title=f"Bazaar Item Error",
            description=f"The item '{name}' is not available in the bazaar.",
            color=0xff0000)
        panda = await bot.fetch_user(554343055029698571)
        errorEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
        await inter.response.send_message(embed=errorEmbed)
    elif not isFloat(price):
        errorEmbed = disnake.Embed(
            title=f"Price Error",
            description=f"The price '{price}' is not a valid number.",
            color=0xff0000)
        panda = await bot.fetch_user(554343055029698571)
        errorEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
        await inter.response.send_message(embed=errorEmbed)
    else:
        name = getName(itemID)
        with open('bazaar_bot.txt', 'a') as notifyList:
            notifyList.write(str(inter.user.id) + ' ' + itemID + ' ' + price + '\n')
        successEmbed = disnake.Embed(
            title="Notifier Created",
            description=f"Success! You will now be notified in DMs when the price of '{name}' goes above {price}.",
            color=0x00ff22)
        panda = await bot.fetch_user(554343055029698571)
        successEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        successEmbed.set_thumbnail(url='https://evilpanda.me/files/notify.png')
        await inter.response.send_message(embed=successEmbed)

#Sub command for removing a notifier
@notify.sub_command()
async def remove(inter, name):
    """
    Removes a notifier with the given name

    Parameters
    ----------
    name: The exact item name in Skyblock
    """
    itemID = getID(name)
    if itemID == None:
        errorEmbed = disnake.Embed(
            title=f"Skyblock Item Error",
            description=f"Could not find the item '{name}'. Please make sure this is the exact Skyblock item name.",
            color=0xff0000)
        panda = await bot.fetch_user(554343055029698571)
        errorEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
        await inter.response.send_message(embed=errorEmbed)
    else:
        removeEmbed = disnake.Embed(
    title=f"No matching notifier",
    description=f"Could not find a notifier with the name '{name}' to remove.'",
    color=0xff0000)
        removeEmbed.set_thumbnail(url="https://evilpanda.me/files/notfound.png")
        with open("bazaar_bot.txt", "r") as f:
            lines = f.readlines()
        with open("bazaar_bot.txt", "w") as f:
            for line in lines:
                if line.split()[0] == str(inter.user.id) and line.split()[1] == itemID:
                    removeEmbed = disnake.Embed(
                title=f"Removed Notify",
                description=f"Your notifier for '{name}' was removed.",
                color=0x00ff22)
                    removeEmbed.set_thumbnail(url="https://evilpanda.me/files/bin.png")
                else:
                    f.write(line)
        panda = await bot.fetch_user(554343055029698571)
        removeEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        await inter.response.send_message(embed=removeEmbed)

#Sub command for listing all notifiers
@notify.sub_command()
async def list(inter):
    """
    Lists all of your notifiers
    """
    with open("bazaar_bot.txt", "r") as f:
        lines = f.readlines()
    
    listEmbed = disnake.Embed(
            title=f"No notifiers found",
            description=f"Could not find any notifiers for this discord account. Try creating one with `/notify add`!",
            color=0xff0000)
    listEmbed.set_thumbnail(url="https://evilpanda.me/files/notfound.png")
    with open("bazaar_bot.txt", "r") as f:
        lines = f.readlines()
        listEmbed = disnake.Embed(
                title=f"Notifier List",
                description=f"Here is a list of all your notifiers: ",
                color=0x00ff22)
        listEmbed.set_thumbnail(url="https://evilpanda.me/files/list.png")
        count = 0
        for line in lines:
            if line.split()[0] == str(inter.user.id):
                count = count + 1
                listEmbed.add_field(name=getName(line.split()[1]), value=line.split()[2])
        if count == 0:
            listEmbed = disnake.Embed(
                    title=f"No notifiers found",
                    description=f"Could not find any notifiers for this discord account. Try creating one with `/notify add`!",
                    color=0xff0000)
            listEmbed.set_thumbnail(url="https://evilpanda.me/files/notfound.png")
            #We do a little trolling
            listEmbed.set_image(url="https://evilpanda.me/files/no_notifiers.jpg")
        panda = await bot.fetch_user(554343055029698571)
        listEmbed.set_footer(text="Bazaar Bot • EvilPanda#7288", icon_url=panda.avatar)
        await inter.response.send_message(embed=listEmbed)

#Runs the bot using token from .env file
bot.run(os.getenv("TOKEN"))