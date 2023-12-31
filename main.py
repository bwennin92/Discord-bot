from os import environ
from google.cloud import secretmanager
from discord.ext import commands
from discord.ui import Button, View
import discord

# Function to retrieve secrets from Google Secret Manager
def access_secret_version(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Use your Google Cloud Project ID and the secret name
project_id = "crocobotz"
secret_id = "discord_token"

# Retrieve your Discord bot token from Secret Manager
bot_token = access_secret_version(project_id, secret_id)

# Enable both the members and the message content intents
intents = discord.Intents.default()
intents.members = True  # Already set in your existing code
intents.message_content = True  # This is the line you need to add

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm a bot.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # Your custom on_message processing (if any) goes here
    if message.content == '!intro':
        intro_message = ( "Hello future CrocoDucks! 🐊🦆\n"
            "I'm here to help you select your roles.\n\n"
            "Here's how you can get started:\n"
            "1️⃣ Use the `!roles` command to see a list of available roles.\n"
            "2️⃣ Use the `!role <role_name>` command to assign yourself a role.\n"
            "3️⃣ If you need any help, type `!help`.\n\n"
            "Enjoy your time in CrocoDucks!")
        await message.channel.send(intro_message)
    # This line is necessary for commands to work alongside on_message
    await bot.process_commands(message)

class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Buttons will remain active indefinitely

    @discord.ui.button(label="The Initiated", style=discord.ButtonStyle.green, custom_id="initiated_role_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get the role by name
        role = discord.utils.get(interaction.guild.roles, name="the initiated")
        
        # Check if the role exists
        if role is None:
            await interaction.response.send_message("The role 'The Initiated' was not found. Please contact an administrator.", ephemeral=True)
            return
        
        # Check if the user already has the role
        if role in interaction.user.roles:
            await interaction.response.send_message(f"You already have {role.name} role!", ephemeral=True)
            return
        
        # Try to add the role
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"The {role.name} role has been assigned to you!", ephemeral=True)
        except discord.Forbidden:
            # If the bot does not have permission to add roles
            await interaction.response.send_message("I don't have permission to assign that role.", ephemeral=True)
        except Exception as e:
            # If any other exception occurs
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def assign_role(ctx):
    view = RoleView()
    await ctx.send("Click the button to assign yourself the role:", view=view)



#this starts the bot
bot.run(bot_token)

