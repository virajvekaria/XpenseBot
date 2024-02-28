import json
import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the Google Sheets API client
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
spreadsheet_key = os.getenv("SPREADSHEET_KEY")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def xp(ctx, category: str, amount: float):
    try:
        # Opening the Google Sheets spreadsheet
        sheet = client.open_by_key(spreadsheet_key).sheet1
        cats = sheet.col_values(2)
        sheet.append_row([ctx.author.name, category, amount])

        await ctx.send(f'Expense of Rupees {amount} in category "{category}" logged.')

    except Exception as e:
        print(e)
        await ctx.send('An error occurred while logging the expense.')

@bot.command()
async def xps(ctx):
    try:
        # Opening the Google Sheets spreadsheet
        sheet = client.open_by_key(spreadsheet_key).sheet1

        # Getting all rows as a list of lists
        data = sheet.get_all_values()
        for x, rows in enumerate(data):
            for y, i in enumerate(rows):
                if(i == ''):
                    data[x] [y] = '0'
        

        # Formatting and send the expenses data to Discord
        expenses_data = "\n".join([f"{row[0]}: Rupees {sum(map(int, row[2:]))} ({row[1]})" for row in data])
        print(expenses_data)

        await ctx.send(f'**Monthly Expenses:**\n{expenses_data}')

    except Exception as e:
        print(e)
        await ctx.send('An error occurred while retrieving expenses.')

@bot.command()
async def curr(ctx):
    try:
        sheet = client.open_by_key(spreadsheet_key).sheet1
        column_values = sheet.col_values(sheet.find('Amount').col)
        column_values = column_values[1:]
        column_sum = sum(map(float, column_values))
        await ctx.send(f'Your total spending this month is: {column_sum}')

    except gspread.exceptions.CellNotFound:
        await ctx.send(f'Column not found in the spreadsheet.')
    except Exception as e:
        print(e)
        await ctx.send('An error occurred while retrieving and calculating the sum.')

@bot.command()
async def clr(ctx):
    spreadsheet = client.open_by_key(spreadsheet_key)
    spreadsheet.sheet1.clear()
    await ctx.send('Successfully cleared the sheet')

@bot.command()
async def hlp(ctx):
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are the available commands:",
        color=0x00ff00
    )
    embed.add_field(name="!xp <category> <amount>", value="Log an expense", inline=False)
    embed.add_field(name="!xps", value="Display monthly expenses", inline=False)
    embed.add_field(name="!curr", value="Calculate the sum of values in a column", inline=False)
    embed.add_field(name="!clr", value="Clear all contents from the spreadsheet", inline=False)
    
    await ctx.send(embed=embed)

# possible further addition could be setting
# the current amount and then subtracting it
# as you go on spending

bot.run(os.getenv("DISCORD_TOKEN"))
