import discord
from discord.ext import commands
import argparse

# Use --token to specify the bot token
def parse_arguments():
    parser = argparse.ArgumentParser(description='Filename Parser')
    parser.add_argument('--token', default='SPECIFY YOUR TOKEN', help='Specify your token here')
    args = parser.parse_args()
    return args

args = parse_arguments()
token = args.token

bot = commands.Bot(command_prefix='!',intents=discord.Intents.default())

async def extract_image():
    channel = bot.get_channel(1129449736882114674)

    async for message in channel.history(limit=1):
        latest_message = message
        break  # Break the loop after retrieving the first message
    
    if latest_message:
        print( latest_message.id )
        print(f'Latest message content: {latest_message.content}')
        print(latest_message.attachments)
        image_attachments = [attachment for attachment in message.attachments if attachment.filename.endswith(('png', 'jpg', 'jpeg', 'gif'))]
        print( image_attachments )
        first_image = image_attachments[0]

        await first_image.save(fp='image.jpg')  # Replace 'image.jpg' with the desired file name and extension
        print(f'First image saved to disk: {first_image.filename}')
        return True

    return False

@bot.event
async def on_ready():
    print(f'Bot is connected as {bot.user.name}')

    channel = bot.get_channel(1129449736882114674)

    # async for message in channel.history(limit=1):
    #     latest_message = message
    #     break  # Break the loop after retrieving the first message
    
    # if latest_message:
    #     print( latest_message.id )
    #     print(f'Latest message content: {latest_message.content}')
    #     print(latest_message.attachments)
    #     image_attachments = [attachment for attachment in message.attachments if attachment.filename.endswith(('png', 'jpg', 'jpeg', 'gif'))]
    #     print( image_attachments )
    #     first_image = image_attachments[0]

    #     await first_image.save(fp='image.jpg')  # Replace 'image.jpg' with the desired file name and extension
    #     print(f'First image saved to disk: {first_image.filename}')
    # else:
    #     print('No messages found in the channel')


@bot.event
async def on_message(message):
    # if message.author == bot.user:
    #     return  # Ignore messages sent by the bot itself
    
    print( "GOT A MESSAGE" )
    print( message.content )

    if message.type == discord.MessageType.default:
        print( "Extracting image" )
        await extract_image()
        await bot.close()

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

# Add more commands and events as needed

# Run bot with specified token
bot.run( token )

