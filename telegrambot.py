from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


class TelegramBot:
    TOKEN: Final = '6786618013:AAFrqA_rxNX3wXNfAFmKLHbTqMKzIR1VjAM'
    BOT_USERNAME: Final = '@FlaskFlaskApiBot'

    def __init__(self):
        pass

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Hello! Thanks for chatting with me!')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Help command!')

    async def custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Custom command!')

    def handle_response(self, text: str) -> str:
        processed: str = text.lower()

        if 'hello' in processed:
            return 'Hey there!'

        if 'how are you' in processed:
            return 'I am good'

        return 'I do not understand'

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message_type: str = update.message.chat.type
        text: str = update.message.text

        print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

        if message_type == 'group':
            if self.BOT_USERNAME in text:
                new_text: str = text.replace(self.BOT_USERNAME, '').strip()
                response: str = self.handle_response(new_text)
            else:
                return
        else:
            response: str = self.handle_response(text)

        print('Bot: ', response)
        await update.message.reply_text(response)

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f'Update {update} caused error {context.error}')

    def start_bot(self):
        print('Starting bot...')
        app = Application.builder().token(TelegramBot.TOKEN).build()

        app.add_handler(CommandHandler('start', self.start_command))
        app.add_handler(CommandHandler('help', self.help_command))
        app.add_handler(CommandHandler('custom', self.custom_command))

        app.add_handler(MessageHandler(filters.TEXT, self.handle_message))

        app.add_error_handler(self.error)

        print('Polling...')

        app.run_polling(poll_interval=3)
