import discord
from discord.ext import commands
from cryptography.fernet import Fernet

intents = discord.Intents.all()
intents.messages = True
intents.dm_messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

passwords = {}
user_passwords = {}

def save_passwords():
    with open('password.txt', 'w') as file:
        for account, data in passwords.items():
            encrypted_password = data['password']
            user_id = data['user_id']
            file.write(f'{account}:{encrypted_password.decode()}:{user_id}\n')

def load_passwords():
    try:
        with open('password.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                account, encrypted_password, user_id = line.strip().split(':')
                passwords[account] = {
                    'password': encrypted_password.encode(),
                    'user_id': int(user_id)
                }
    except FileNotFoundError:
        print("Password file not found. Creating a new one.")

@bot.event
async def on_command(message):
    if isinstance(message.channel, discord.DMChannel):
        return
    try:
        await message.delete()
    except discord.Forbidden:
        print(f"Bot tidak memiliki izin untuk menghapus pesan di {message.channel.name}")

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name}')
    load_passwords()

@bot.command()
async def addpassword(ctx, account, password):
    encrypted_password = cipher_suite.encrypt(password.encode())
    user_id = ctx.author.id
    passwords[account] = {
        'password': encrypted_password,
        'user_id': user_id
    }
    save_passwords()
    await ctx.send('Password has been added successfully.')

@bot.command()
async def showpassword(ctx, account):
    if ctx.author.id in user_passwords:
        master_password = user_passwords[ctx.author.id]
        await ctx.send(f'Please enter your master password for {account}:')
        
        def check(message):
            return message.author == ctx.author and message.content == master_password
        
        try:
            response = await bot.wait_for('message', check=check, timeout=30)
            if account in passwords and ctx.author.id == passwords[account]['user_id']:
                password_data = passwords[account]
                encrypted_password = password_data['password']
                decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
                await ctx.send(f'Password for {account}: {decrypted_password}')
            else:
                await ctx.send(f'No password found for {account}.')
        except TimeoutError:
            await ctx.send('Timeout. Please try again.')
    else:
        await ctx.send('Please set your master password first using `!setmasterpassword`.')

@bot.command()
async def viewpasswords(ctx, master_password):
    if ctx.author.id in user_passwords:
        if user_passwords[ctx.author.id] == master_password:
            if ctx.author.id in user_passwords:
                password_list = []
                for account, data in passwords.items():
                    if ctx.author.id == data['user_id']:
                        encrypted_password = data['password']
                        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
                        password_list.append(f'{account}: {decrypted_password}')
                
                if password_list:
                    password_text = "\n".join(password_list)
                    await ctx.send(f'Your passwords:\n{password_text}')
                else:
                    await ctx.send('No passwords found.')
            else:
                await ctx.send('Please set your master password first using `!setmasterpassword`.')
        else:
            await ctx.send('Incorrect master password.')
    else:
        await ctx.send('Please set your master password first using `!setmasterpassword`.')

@bot.command()
async def setmasterpassword(ctx, master_password):
    user_passwords[ctx.author.id] = master_password
    await ctx.send('Master password set successfully.')

@bot.event
async def on_command(ctx):
    await ctx.message.delete()

bot.run('BOT_TOKEN')
