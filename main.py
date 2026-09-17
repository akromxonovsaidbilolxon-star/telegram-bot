import json
import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
BASE_DIR = Path(__file__).resolve().parent


def get_sheet():
    """Create a Google Sheets connection using either a JSON env var or a local file."""
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    try:
        if credentials_json:
            credentials_info = json.loads(credentials_json)
            creds = Credentials.from_service_account_info(
                credentials_info,
                scopes=SCOPES,
            )
        else:
            credentials_file = os.getenv(
                "GOOGLE_CREDENTIALS_FILE",
                str(BASE_DIR / "credentials.json"),
            )
            credentials_path = Path(credentials_file)
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Google credentials file not found: {credentials_path}. "
                    "Set GOOGLE_CREDENTIALS_JSON or add credentials.json."
                )
            creds = Credentials.from_service_account_file(
                str(credentials_path),
                scopes=SCOPES,
            )

        client = gspread.authorize(creds)
        spreadsheet_name = os.getenv("GOOGLE_SHEET_NAME", "Policy Pulse")
        return client.open(spreadsheet_name).sheet1
    except Exception as exc:
        raise RuntimeError(
            "Could not connect to Google Sheets. Check the credentials, "
            "spreadsheet name, and sharing permissions."
        ) from exc


def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_TOKEN is not set. Configure it as an environment variable."
        )

    sheet = get_sheet()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Ready to log driver statuses and equipment swaps."
        )

    async def log_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message is None or update.message.text is None:
            return

        log_text = update.message.text
        sheet.append_row([log_text])
        await update.message.reply_text("Event securely logged to the spreadsheet.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_event))
    app.run_polling()


if __name__ == "__main__":
    main()
