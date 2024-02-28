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
async def expense(ctx, category: str, amount: float):
    try:
        # Opening the Google Sheets spreadsheet
        sheet = client.open_by_key(spreadsheet_key).sheet1
        cats = sheet.col_values(2)
        data = sheet.get_all_values()

        i = 0
        while i<len(cats):
            if(cats[i] == category):
                index = i
                break
            i+=1

        # Adding a new row with expense details
        if i == len(cats):
            sheet.append_row([ctx.author.name, category, amount])
        else:
            cell = len(data[index])
            sheet.update_cell(index+1, cell+1, amount)

        await ctx.send(f'Expense of Rupees {amount} in category "{category}" logged.')

    except Exception as e:
        print(e)
        await ctx.send('An error occurred while logging the expense.')

@bot.command()
async def expenses(ctx):
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

bot.run('')
