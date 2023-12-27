import discord
from discord.ext import commands
import json
from cryptography.fernet import Fernet
import string
import random

from credential_generator import generate_password, generate_nickname, write_credentials_to_file

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Config file not found.")
        return None

def save_config(token, encryption_key):
    with open('config.json', 'w') as f:
        json.dump({"token": token, "encryption_key": encryption_key.decode()}, f)

def load_user_keys():
    try:
        with open('user_keys.json', 'r') as f:
            user_keys = json.load(f)
        return user_keys
    except FileNotFoundError:
        print("User keys file not found.")
        return {}

def save_user_key(user_id, encryption_key):
    user_keys = load_user_keys()
    user_keys[user_id] = encryption_key.decode()

    with open('user_keys.json', 'w') as f:
        json.dump(user_keys, f)

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # archive.txt
    with open('archive.txt', 'a') as archive_file:
        archive_file.write(f"{message.author.name}: {message.content}\n")

    await bot.process_commands(message)

@bot.command(name='password')
async def password_command(ctx):
    nickname = generate_nickname()
    password = generate_password()

    response = f'Generated credentials:\nNickname: {nickname}\nPassword: {password}'
    await ctx.send(response)

@bot.command(name='encrypt')
async def encrypt(ctx, *, message=""):
    config = load_config()
    if not config:
        await ctx.send("Config file not found.")
        return

    user_id = str(ctx.author.id)
    user_keys = load_user_keys()

    if user_id not in user_keys:
        await ctx.send("You need to create a key first using !key.")
        return

    encryption_key = user_keys[user_id].encode()
    cipher_suite = Fernet(encryption_key)

    if not message:
        await ctx.send("Please provide a message to encrypt.")
        return

    encrypted_message = cipher_suite.encrypt(message.encode())
    response = f'Encrypted message: {encrypted_message.decode()}'

    # archive.txt
    with open('archive.txt', 'a') as archive_file:
        archive_file.write(f"{bot.user.name}: {response}\n")

    await ctx.send(response)

@bot.command(name='decrypt')
async def decrypt(ctx, *, encrypted_message=""):
    config = load_config()
    if not config:
        await ctx.send("Config file not found.")
        return

    user_id = str(ctx.author.id)
    user_keys = load_user_keys()

    if user_id not in user_keys:
        await ctx.send("You need to create a key first using !key.")
        return

    encryption_key = user_keys[user_id].encode()
    cipher_suite = Fernet(encryption_key)

    if not encrypted_message:
        await ctx.send("Please provide an encrypted message to decrypt.")
        return

    try:
        decrypted_message = cipher_suite.decrypt(encrypted_message.encode())
        response = f'Decrypted message: {decrypted_message.decode()}'

        # archive.txt
        with open('archive.txt', 'a') as archive_file:
            archive_file.write(f"{bot.user.name}: {response}\n")

        await ctx.send(response)
    except Exception as e:
        await ctx.send(f'Error decrypting message: {str(e)}')

@bot.command(name='key')
async def create_key(ctx):
    user_id = str(ctx.author.id)
    user_keys = load_user_keys()

    if user_id in user_keys:
        await ctx.send(f"You already have a key: {user_keys[user_id]}")
        return

    encryption_key = Fernet.generate_key()
    save_user_key(user_id, encryption_key)

    await ctx.send(f"Key created successfully: {encryption_key.decode()}. Use !use to set this key.")

@bot.command(name='use')
async def use_key(ctx, key=None):
    user_id = str(ctx.author.id)
    user_keys = load_user_keys()

    if user_id not in user_keys:
        await ctx.send("You need to create a key first using !key.")
        return

    if key is None:
        await ctx.send("Please enter the key you want to use. Example: !use <key>")
        return

    save_config(load_config()['token'], key.encode())
    await ctx.send("Key set successfully.")

    @bot.command(name='help')
    async def help_command(ctx):
        # Define the list of commands and their explanations
        commands_info = [
            {'name': '!password', 'description': 'Generate a random nickname and password for you.'},
            {'name': '!encrypt', 'description': 'Encrypt a message using your personal encryption key.'},
            {'name': '!decrypt', 'description': 'Decrypt an encrypted message using your personal encryption key.'},
            {'name': '!key', 'description': 'Generate a new personal encryption key for you.'},
            {'name': '!use', 'description': 'Set your personal encryption key for encrypting and decrypting messages.'},
        ]

        # Construct the help message
        help_message = '```Available Commands:\n'
        for cmd in commands_info:
            help_message += f"{cmd['name']}: {cmd['description']}\n"
        help_message += '```'



        # Send the help message to the user
        await ctx.send(help_message)


# Run the bot
bot.run(load_config()['token'])
