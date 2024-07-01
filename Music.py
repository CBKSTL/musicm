import discord
from discord.ext import commands
import Song as s
import asyncio


c1 = 0x47A7FF #positive
c2 = 0xFF3333 #negative

ffmpegopts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}




class Music(commands.Cog):
    botInfo = {}
    
    def reset(self):
        global botInfo
        botInfo = {
        'songQueue': [],
        'currentSong': None,
        'songPosition': 0,
        'botPaused': False,
        'loopSong': False,
        'loopQueue': False,
        'monitor': False
        }

    async def autoLeave(self,ctx):
        idleTime = 0
        while True:

            if ctx.voice_client is None:
                self.reset()
                break
            if len(ctx.voice_client.channel.members) < 2:
                embed=discord.Embed(description=f"Everyone left the voice channel, I'll take a break too, sayonara!~", color=c2)
                await ctx.send(embed=embed)
                await ctx.voice_client.disconnect()
                self.reset()
                break
            if not botInfo['monitor']:
                idleTime += 3
                if idleTime >= 300:
                    await ctx.voice_client.disconnect()
                    self.reset()
                    embed=discord.Embed(description=f"Seems like there's nothing I can play for you at the moment. I'm leaving the voice channel, call me back whenever you need!", color=c2)
                    await ctx.send(embed=embed)
                    break
            else:
                idleTime = 0
                #auto leave when idling too long
            await asyncio.sleep(3)

    async def musicMonitor(self,ctx):
        global botInfo
        
        while True:
            if ctx.voice_client is None:
                self.reset()
                break

            songQueue = botInfo['songQueue']
            if not botInfo['botPaused'] and not ctx.voice_client.is_playing():
                if len(songQueue) == 0:
                    botInfo['monitor'] = False
                    break
                if botInfo['loopQueue']:
                    playedSong = songQueue.pop(0)
                    songQueue.append(playedSong)
                elif not botInfo['loopSong'] and not botInfo['loopQueue']:
                    if len(songQueue) == 0:
                        botInfo['monitor'] = False
                        break
                    if botInfo['currentSong'] is not None:
                        songQueue.remove(botInfo['currentSong'])
                        del botInfo['currentSong']
                        botInfo['currentSong'] = None
                    
                try:
                    botInfo['currentSong'] = songQueue[0]
                    await self.playSong(ctx,botInfo['currentSong'])
                except:
                    botInfo['monitor'] = False
                    break
            #if bot finished playing, try play the next song in queue
            await asyncio.sleep(3)    

    async def playSong(self,ctx,song:s.Song):
        embed=discord.Embed(description=f"**Now playing:** [{song.title}]({song.videolink})  `[{song.duration}]`", color=c1)
        await ctx.send(embed=embed)
        # if not discord.opus.is_loaded():
        #     discord.opus.libopus_loader('/usr/local/lib/libopus.dylib')
        #for non-Window platforms
        try:
            source = discord.FFmpegPCMAudio(song.audio, **ffmpegopts)
            ctx.voice_client.play(source)
        except:
            embed=discord.Embed(description=f"Error occured while playing, please try again...", color=c2)
            




    def __init__(self, client):
        self.client = client
        self.reset()


    @commands.command(name='Ping')
    async def _ping(self,ctx):
        embed=discord.Embed(description=f'`{int(self.client.latency*1000)}` **ms**', color=c1)
        await ctx.send(embed=embed)


    @commands.command(name='Play', aliases=['pl', 'p'])
    async def _play(self,ctx, *, url):
        global botInfo

        if ctx.author.voice is None:
            embed=discord.Embed(description=f"Please join a voice channel first", color=c2)
            await ctx.send(embed=embed)        
            return
        
        if ctx.voice_client is None and ctx.author.voice is not None:
            voice_channel = ctx.author.voice.channel
            await voice_channel.connect()
            ctx.voice_client.stop()
        #Join a voice channel

        if ctx.voice_client.channel == ctx.author.voice.channel:
            embed=discord.Embed(description=f"<a:loading:1255665507831386152> Loading entry...", color=c1)
            loadingMessage = await ctx.send(embed=embed)

            try:
                song = s.Song(url)
            except:
                await loadingMessage.edit(embed=discord.Embed(description=f"Invalid keyword/link...", color=c2))
                return
            
            botInfo['songQueue'].append(song)
            await loadingMessage.edit(embed=discord.Embed(description=f"**Queued:** [{song.title}]({song.videolink})  `[{song.duration}]`", color=c1))

            if not botInfo['monitor']:
                self.client.loop.create_task(self.musicMonitor(ctx))
                self.client.loop.create_task(self.autoLeave(ctx))
                botInfo['monitor'] = True

        else:
            embed=discord.Embed(description=f"I'm already in a voice channel", color=c2)
            await ctx.send(embed=embed)


    @commands.command(name='LoopSong', aliases=['lps', 'lpsong', 'ls', 'loop'])
    async def _loopsong(self,ctx):
        global botInfo
        if botInfo['loopSong']:
            botInfo['loopSong'] = False
            embed=discord.Embed(description=f"Loop Song: **DISABLED**", color=c1)
            await ctx.send(embed=embed)
        else:
            botInfo['loopSong'] = True
            embed=discord.Embed(description=f"Loop Song: **ENABLED**", color=c1)
            await ctx.send(embed=embed)

        if botInfo['loopQueue']:
            botInfo['loopQueue'] = False


    @commands.command(name='LoopQueue', aliases=['lpq', 'lpqueue', 'lq'])
    async def _loopqueue(self,ctx):
        global botInfo
        if botInfo['loopQueue']:
            botInfo['loopQueue'] = False
            embed=discord.Embed(description=f"Loop Queue: **DISABLED**", color=c1)
            await ctx.send(embed=embed)
        else:
            botInfo['loopQueue'] = True
            embed=discord.Embed(description=f"Loop Queue: **ENABLED**", color=c1)
            await ctx.send(embed=embed)

        if botInfo['loopSong']:
            botInfo['loopSong'] = False


    @commands.command(name='Queue', aliases=['q','playlist'])
    async def _queue(self, ctx, page=1):
        global botInfo
        songQueue = botInfo['songQueue']
        embed=discord.Embed(color=c2)
        if len(songQueue) == 0:
            embed.description="Queue is empty"
            await ctx.send(embed=embed)
            return
        if (page*10) - len(songQueue) >= 10:
            embed.description="Invalid page"
            await ctx.send(embed=embed)
            return
        else: 
            try:
                queueList = str("")
                if page == 1:
                    queueList += f'`↓↓↓ Now playing... ↓↓↓`'
                    queueList += f'\n1)  {songQueue[0].title}        [{songQueue[0].duration}]({songQueue[0].videolink})\n'
                    queueList += f'`↑↑↑ Now playing... ↑↑↑`'
                    for i in range(1, 10):
                        queueList += f'\n{i+1})  {songQueue[i].title}        [{songQueue[i].duration}]({songQueue[i].videolink})'
                else:
                    for i in range((page-1)*10, (page*10)):
                        queueList += f'\n{i+1})  {songQueue[i].title}        [{songQueue[i].duration}]({songQueue[i].videolink})'
            except:
                pass
            embed=discord.Embed(color=c1)
            embed.title='**Queue:**'
            embed.description=queueList
            embed.set_footer(text=f'Renny by ren.xxx • Page {page}', icon_url='https://cdn.discordapp.com/avatars/887915339294318633/836a28ee2d030dab64661a8154c0de61.png?size=160')
        await ctx.send(embed=embed)
        
            
    @commands.command(name='Leave', aliases=['disconnect','dc'])
    async def _leave(self, ctx):
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        self.reset()
        embed=discord.Embed(description=f"Voice channel disconnected", color=c1)
        await ctx.send(embed=embed)


    @commands.command(name='Pause')
    async def _pause(self, ctx):
        global botInfo
        if ctx.voice_client.is_playing() == True:
            ctx.voice_client.pause()
            botInfo['botPaused'] = True
            embed=discord.Embed(description=f"Music paused ⏸", color=c1)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(description=f"Nothing is playing...", color=c2)
            await ctx.send(embed=embed)


    @commands.command(name='Resume', aliases=['rs'])
    async def _resume(self, ctx):
        global botInfo
        if botInfo['botPaused'] == True:
            ctx.voice_client.resume()
            embed=discord.Embed(description=f"**Resuming music...** ▶️", color=c1)
            await ctx.send(embed=embed)


    @commands.command(name='Skip', aliases=['next', 'fs'])
    async def _skip(self, ctx):
        global botInfo
        ctx.voice_client.stop()
        embed=discord.Embed(description=f"Song skipped", color=c1)
        await ctx.send(embed=embed)

    @commands.command(name='Remove', aliases=['delete','rm','dl'])
    async def _remove(self,ctx,position:int):
        global botInfo
        songQueue = botInfo['songQueue']

        if ctx.voice_client.is_playing and botInfo['songPosition'] == position - 1:
            ctx.voice_client.stop()
        else:
            if len(songQueue) >= position:
                song = songQueue[position-1]
                songQueue.remove(song)
            else:
                embed=discord.Embed(description=f"Invalid index...", color=c2)
                await ctx.send(embed=embed)

    @commands.command(name='Jump', aliases = ['j'])
    async def _jump(self,ctx,position:int):
        global botInfo
        songQueue = botInfo['songQueue']

        if len(songQueue) >= position > 0:
            if position == 1:
                song = botInfo['currentSong']
            else: 
                song = botInfo['songQueue'][position-1]
            songQueue.remove(song)    
            songQueue.insert(1, song)
            ctx.voice_client.stop()
        else:
            embed=discord.Embed(description=f"Invalid index...", color=c2)
            await ctx.send(embed=embed)

    @commands.command(name='SongInfo',aliases=['si','songinformation','np','nowplaying'])
    async def _songInfo(self,ctx):
        global botInfo
        song = botInfo['currentSong']
        if song is None or len(botInfo['songQueue']) == 0:
            embed=discord.Embed(description=f"Nothing is currently playing...", color=c2)
            await ctx.send(embed=embed)
            return
        
        embed=discord.Embed(title=song.title,url=song.videolink, color=c1)
        try:
            embed.set_image(url = song.thumbnail)
            embed.add_field(name = 'Publisher:', value=song.uploader, inline=True)
            embed.add_field(name = 'Publish date:', value=song.date, inline=True)
            embed.add_field(name = 'Duration:', value=song.duration,inline=True)
            embed.add_field(name = 'Views:', value=song.views,inline=True)
            embed.add_field(name = 'Likes:', value=song.likes,inline=True)
            embed.add_field(name = 'Dislikes:', value=song.dislikes,inline=True)
            embed.set_footer(text='Renny by ren.xxx', icon_url = 'https://cdn.discordapp.com/avatars/887915339294318633/836a28ee2d030dab64661a8154c0de61.png?size=160')
        except:
            pass
        await ctx.send(embed=embed)
        

async def setup(client):
    await client.add_cog(Music(client))

