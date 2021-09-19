# bot.py
import os
import aiml

from dotenv import load_dotenv
from discord.ext import commands


# Start ups
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# AI
kernel = aiml.Kernel()
kernel.learn("std-startup.xml")
kernel.respond("load aiml")

tedbot = commands.Bot()

#### EVENTS #####
@tedbot.event
async def on_ready():
    server_count = len(tedbot.guilds)
    print(f"BOT [Online]\nConnected Server List , Total : {server_count}")
    for no, server in enumerate(tedbot.guilds):
        print(f"{no+1}. Name: {server.name} , ID : {server.id}")


# discord bot event watching
@tedbot.event
async def on_message(message):
    # Ignore the message if the mesagge is from the bot itself
    if message.author == tedbot.user:
        return
    elif message.content == "who is hooman":
        await message.channel.send("I am HOOMAN!!!!!")
    elif message.content == "tag me":
        await message.channel.send("<@" + str(message.author.id) + ">")
    elif message.content[0] == ";":
        res = kernel.respond(message.content[1:])
        if res != "":
            await message.channel.send(res)
        else:
            await message.channel.send("I haven't learn that yet")

    else:
        return


tedbot.run(TOKEN, bot=True)
