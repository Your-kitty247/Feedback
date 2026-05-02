import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

FILE = "feedback.json"
LOG_CHANNEL_ID = 1499436270198325439  # replace this

# Load data
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        feedback_db = json.load(f)
else:
    feedback_db = {}

def save_data():
    with open(FILE, "w") as f:
        json.dump(feedback_db, f, indent=4)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# 🔒 Set feedback
@bot.tree.command(name="setfeedback", description="Set feedback for a user")
@app_commands.describe(user="User", message="Feedback message")
async def setfeedback(interaction: discord.Interaction, user: discord.Member, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No permission!", ephemeral=True)
        return

    feedback_db[str(user.id)] = {
        "message": message,
        "by": str(interaction.user),
        "time": str(datetime.utcnow())
    }
    save_data()

    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if log_channel:
        await log_channel.send(f"📝 Feedback set for {user} by {interaction.user}")

    await interaction.response.send_message(f"✅ Feedback set for {user.mention}", ephemeral=True)

# 📩 User feedback
@bot.tree.command(name="feedback", description="View your feedback")
async def feedback(interaction: discord.Interaction):
    data = feedback_db.get(str(interaction.user.id))
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    try:
        if data:
            embed = discord.Embed(
                title="📋 Your Application Feedback",
                description=data["message"],
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Given by {data['by']}")

            await interaction.user.send(embed=embed)
            await interaction.response.send_message("📩 Check your DMs!", ephemeral=True)

            if log_channel:
                await log_channel.send(f"✅ {interaction.user} checked their feedback")

        else:
            await interaction.response.send_message("❌ No feedback yet.", ephemeral=True)

            if log_channel:
                await log_channel.send(f"⚠️ {interaction.user} tried /feedback but none exists")

    except:
        await interaction.response.send_message("❌ Cannot DM you.", ephemeral=True)

        if log_channel:
            await log_channel.send(f"❌ DM failed for {interaction.user}")

# 👁️ Admin view feedback
@bot.tree.command(name="feedback-view", description="View someone else's feedback")
@app_commands.describe(user="User")
async def feedback_view(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No permission!", ephemeral=True)
        return

    data = feedback_db.get(str(user.id))

    if data:
        embed = discord.Embed(
            title=f"📋 Feedback for {user}",
            description=data["message"],
            color=discord.Color.green()
        )
        embed.add_field(name="Given by", value=data["by"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("❌ No feedback found.", ephemeral=True)

# 📊 Logs command
@bot.tree.command(name="feedback-logs", description="See all submitted feedback logs")
async def feedback_logs(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No permission!", ephemeral=True)
        return

    if not feedback_db:
        await interaction.response.send_message("No feedback stored.", ephemeral=True)
        return

    msg = ""
    for user_id, data in feedback_db.items():
        msg += f"<@{user_id}> → by {data['by']}\n"

    await interaction.response.send_message(msg)

import os
bot.run(os.getenv("TOKEN"))
