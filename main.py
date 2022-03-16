from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
import Constants as keys
import Answer as A

print("Bot iniciando...")

def StartCommand(Update, Context):
    Update.message.reply_text('Escribe algo para comenzar')

def HelpCommand(Update, Context):
    Update.message.reply_text('Necesitas mas ayuda? puedes consultar aqui->')

def HandleMessage(Update, Context):
    text = str(Update.message.text).lower()
    answer = A.PossibleAnswers(text)

    Update.message.reply_text(answer)

def Error(Update, Context):
    print(f"Update {Update}  Error causado {Context.error}")

def Main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", StartCommand))
    dp.add_handler(CommandHandler("help", HelpCommand))

    dp.add_handler(MessageHandler(Filters.text, HandleMessage))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    Main()

