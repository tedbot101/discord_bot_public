# music_bot.py
import os

from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from pytube import Search


# Start ups
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
tedbot = commands.Bot(command_prefix="~")

#### queue init ###
queue = {}
queue_title = {}


def get_yt_info(name):
    return Search(name).results[0].watch_url


def get_source(url):
    with YoutubeDL({"format": "bestaudio", "noplaylist": "True"}) as ydl:
        info = ydl.extract_info(url, download=False)
    return (
        FFmpegPCMAudio(
            info["url"],
            **{
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn",
            },
        ),
        info["title"],
    )


def check_queue(ctx, id):
    if queue[id] != []:
        voice = get(tedbot.voice_clients, guild=ctx.guild)
        queue[id].pop(0)
        queue_title[id].pop(0)
        try:
            if queue[id][0][0:4] == "https":
                # play with url
                source, title = get_source(queue[id][0])
            else:
                # youtube search engine
                source, title = get_source(get_yt_info(queue[id][0]))
            voice.play(source)
            print(queue_title[id])
        except IndexError:
            print("[bot] Empty queue")


@tedbot.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(tedbot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"[bot] The bot has left {channel}")
        await ctx.send(f"***Tedbot left {channel}***")
    else:
        print("***Tedbot not in channel***")
        await ctx.send("***Tedbot not in channel***")


# command to resume
@tedbot.command()
async def resume(ctx):
    voice = get(tedbot.voice_clients, guild=ctx.guild)
    if not voice.is_playing():
        voice.resume()
        await ctx.send("***Resuming***", delete_after=5)


# command to pause
@tedbot.command()
async def pause(ctx):
    voice = get(tedbot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("***Paused***", delete_after=5)


# command to stop voice
@tedbot.command()
async def stop(ctx):
    voice = get(tedbot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.send("***Stopping***", delete_after=5)


@tedbot.command(pass_context=True)
async def play(ctx, *argv):
    channel = ctx.message.author.voice.channel
    voice = get(tedbot.voice_clients, guild=ctx.guild)
    guild_id = ctx.message.guild.id

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    # prepare url
    url = ""
    for arg in argv:
        url += arg + " "

    if url[0:4] == "https":
        # play with url
        source, title = get_source(url)
    else:
        # youtube search engine
        source, title = get_source(get_yt_info(url))

    if not voice.is_playing():
        queue[guild_id].append(url)
        queue_title[guild_id].append(title)
        url = ""
        voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))
        await ctx.send("***Playing*** : " + title)
    else:
        # added to queue
        queue[guild_id].append(url)
        queue_title[guild_id].append(title)
        await ctx.send("***Added to queue*** : " + title)
        print(queue_title[guild_id])


@tedbot.command(pass_context=True)
async def skip(ctx):
    voice = get(tedbot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    check_queue(ctx, ctx.message.guild.id)


# command to stop voice
@tedbot.command()
async def q(ctx):
    msg = ""
    for n, song in enumerate(queue_title[ctx.guild.id]):
        msg += str(n + 1) + ". " + song + "\n"
    print(msg)
    await ctx.send("***Queue*** : \n" + msg)


# Admin command
@tedbot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.bot.logout()


@tedbot.command()
@commands.is_owner()
async def takeover_server(ctx):
    await ctx.send("Taking over server ....")


#### EVENTS #####
@tedbot.event
async def on_ready():
    server_count = len(tedbot.guilds)
    print(
        f"[bot]Status = [Online]\n[bot]Connected Server List , Total : {server_count}"
    )
    for no, server in enumerate(tedbot.guilds):
        queue[server.id] = []
        queue_title[server.id] = []
        print(f"{no+1}. Name: {server.name} , ID : {server.id}")
    print("[bot] Events :")


tedbot.run(TOKEN, bot=True)
