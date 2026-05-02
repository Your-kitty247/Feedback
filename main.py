import discord
from discord.ext import commands
from discord import app_commands
import json
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

FILE = "feedback.json"

# Load data
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        feedback_db = json.load(f)
else:
    feedback_db = {}

# Save function
def save_data():
    with open(FILE, "w") as f:
        json.dump(feedback_db, f, indent=4)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# 🔒 Set feedback (ADMIN ONLY)
@bot.tree.command(name="setfeedback", description="Set feedback for a user")
@app_commands.describe(user="User", message="Feedback message")
async def setfeedback(interaction: discord.Interaction, user: discord.Member, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No permission!", ephemeral=True)
        return

    feedback_db[str(user.id)] = message
    save_data()

    await interaction.response.send_message(f"✅ Feedback set for {user.mention}", ephemeral=True)

# 📩 View feedback (DM EMBED)
@bot.tree.command(name="feedback", description="View your feedback")
async def feedback(interaction: discord.Interaction):
    msg = feedback_db.get(str(interaction.user.id))

    try:
        if msg:
            embed = discord.Embed(
                title="📋 Your Application Feedback",
                description=msg,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Thank you for applying!")

        else:
            embed = discord.Embed(
                title="📋 Feedback",
                description="No feedback yet.",
                color=discord.Color.red()
            )

        await interaction.user.send(embed=embed)
        await interaction.response.send_message("📩 Check your DMs!", ephemeral=True)

    except:
        await interaction.response.send_message("❌ I can't DM you. Please enable DMs.", ephemeral=True)

import os
bot.run(os.getenv("TOKEN"))
