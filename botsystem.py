import __main__ as main
import discord, asyncio, json, time, subprocess, timedelta
import multiprocessing as mp

owner = 728289161563340881

ping = []
p_test = []

def set_client():
    global client
    client = main.client

#便利かなぁと作った関数
def p_check(member,channel,permission):
    bool = member.id == owner or member.permissions_in(channel) >= permission
    return bool

async def no_embed(message):
    global p_test
    if message in p_test:
        await message.channel.send('謎だぁ')
        dev = await main.client.fetch_user(owner)
        await dev.send(f'謎現象：{message.content}')
        p_test.remove(message)
    g_owner = await main.client.fetch_user(message.guild.owner_id)
    try:
        await message.channel.send('おや？これは埋め込みリンク使えないパターンか？？')
    except discord.errors.Forbidden:
        pass
    try:
        await message.channel.send(embed=discord.Embed(description='テストｫｫｫ',colour=0x00bfff))
        await message.channel.send('いや、使えるなぁ………。一応もう一度試そう。')
        test = await message.channel.send(message.content)
        p_test.append(test)
    except discord.errors.Forbidden:
        await message.channel.send(f'おい{g_owner}埋め込み送れないじゃねーかアホじゃねーのか(盛大な暴言)')
        try:
            dev = await message.guild.fetch_member(owner)
            await dev.send(f'おーい、{message.guild}で権限不足なってるー')
        except:
            pass

#サブプロセス用
def screenfetch():
    result = subprocess.run('screenfetch',capture_output=True).stdout.decode()

#メイン
async def commands(message):
    #if message.content == '@test':
    #    await message.channel.send('@reply')

    if message.content.startswith('@search user'):
        id = int(message.content[13:])
        user = await main.client.fetch_user(id)
        colour = str(user.default_avatar)
        if colour == 'blurple':
            colour = discord.Colour.blurple()
        elif colour == 'grey':
            colour = discord.Colour.greyple()
        elif colour == 'green':
            colour = discord.Colour.green()
        elif colour == 'orange':
            colour = discord.Colour.orange()
        elif colour == 'red':
            colour = discord.Colour.red()
        if user.bot:
            u_b = 'BOT'
        else:
            u_b = 'ユーザー'
        with open('user_data.json',mode='r') as file:
            user_dict = json.loads(file.read())
        data = discord.Embed(title=f'{u_b}情報',colour=colour)
        data.add_field(name='名前',value=user)
        data.add_field(name='作成日時',value=timedelta.utc2jst(user.created_at).strftime('%Y/%m/%d %H:%M:%S'))
        if user_dict.get(str(user.id)):
            data.add_field(name='メモ',value=user_dict[str(user.id)])
        data.add_field(name='アイコン',value='\u200c')
        data.set_image(url=user.avatar_url)
        mes = None
        try:
            mes = await message.channel.send(embed=data)
        except discord.errors.Forbidden:
            await no_embed(message)
        if mes:
            if message.author == user:
                await mes.add_reaction('🖋️')
                def check(reaction, author):
                    return author == user and str(reaction.emoji) == '🖋️'

                try:
                    reaction, user = await client.wait_for('reaction_add',timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    await mes.clear_reaction('🖋️')
                else:
                    def check(m):
                        return m.author == user and m.channel == message.channel
                    await message.channel.send('メモを入力してください。(60秒以内)')

                    try:
                        msg = await client.wait_for('message', timeout=60.0, check=check)
                    except asyncio.TimeoutError:
                        await mes.clear_reaction('🖋️')
                        await message.channel.send('タイムアウトしました。')
                    else:
                        user_dict[str(user.id)] = msg.content
                        with open('user_data.json',mode='w') as file:
                            user_json = json.dumps(user_dict,ensure_ascii=False, indent=2)
                            file.write(user_json)
                        await message.channel.send('メモを設定しました。')


    if message.content.startswith('@search server'):
        id = int(message.content[15:])
        server = main.client.get_guild(id)
        owner = await main.client.fetch_user(server.owner_id)
        data = discord.Embed(title='サーバー情報',colour=0x00bfff)
        data.add_field(name='名前',value=server.name)
        data.add_field(name='オーナー',value=f'{owner}({owner.id})')
        data.add_field(name='ブーストレベル',value=server.premium_tier)
        data.add_field(name='作成日時',value=timedelta.utc2jst(server.created_at).strftime('%Y/%m/%d %H:%M:%S'))
        data.add_field(name='BOT導入日時',value=timedelta.utc2jst(server.me.joined_at).strftime('%Y/%m/%d %H:%M:%S'))
        data.add_field(name='アイコン',value='\u200c')
        data.set_image(url=server.icon_url)
        try:
            await message.channel.send(embed=data)
        except discord.errors.Forbidden:
            await no_embed(message)

    if message.content == '@clear':
        if p_check(message.author,message.channel,discord.Permissions().update(manage_messages=True)):
            kakunin = await message.channel.send('削除しますか？')
            await kakunin.add_reaction('⭕')
            await kakunin.add_reaction('❌')
            def check(reaction, user):
                return user == message.author

            ask = True
            while ask:
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)

                except:
                    await kakunin.edit(content='削除しますか？\n取り消しました。')
                    ask = False
                else:
                    if str(reaction) == '❌':
                        await kakunin.edit(content='削除しますか？\n取り消しました')
                        ask = False
                    if str(reaction) == '⭕':
                        await message.channel.purge(limit=10000)
                        ask = False

    if message.content == '@help':
        embed=discord.Embed(title='コマンド',colour=0x00bfff)
        embed.add_field(name='@search [user|server] <ID>',value='サーバー情報|ユーザー情報を表示します。')
        embed.add_field(name='@clear',value='チャンネル内のメッセージを一括削除します。\n[メッセージの管理]の権限が必要です。')
        embed.add_field(name='@ping',value='BOTの応答速度を計測します。')
        try:
            await message.channel.send(embed=embed)
        except discord.errors.Forbidden:
            await no_embed(message)

    if message.content == '@ping':
        global ping
        mes = await message.channel.send('Testing now...')
        ping.append(mes)

    now = time.time()
    await asyncio.sleep(5)
    if message in ping:
        delta = str((now - message.created_at.timestamp())/1000)
        latency = str(main.client.latency*1000)
        await message.edit(content=f'Ping : {delta[:6]}ms\n'
                                f'Latency : {latency[:6]}ms')
        ping.remove(message)
