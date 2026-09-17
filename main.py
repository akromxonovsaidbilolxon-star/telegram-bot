import os
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Authenticate with Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

# 2. Connect to the workbook (update the name if your sheet is called something else)
sheet = client.open("Policy Pulse").sheet1 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ready to log driver statuses and equipment swaps.")

async def log_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_text = update.message.text
    # Appends the incoming log to the next available row in the sheet
    sheet.append_row([log_text]) 
    await update.message.reply_text("Event securely logged to the spreadsheet.")

def main():
    # Render will automatically inject your token here later
    token = os.environ.get("TELEGRAM_TOKEN")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_event))
    
    app.run_polling()

if __name__ == '__main__':
    main()
