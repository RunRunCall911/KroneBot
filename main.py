from sklearn.model_selection import train_test_split
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import Constants as keys
import pandas as pd
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from sklearn.tree import DecisionTreeClassifier
import pymongo
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.tree import export_text

print("Bot iniciando...")

features = ['SEXO', 'TIPO_PACIENTE', 'EDAD', 'NEUMONIA',
            'EMBARAZO', 'INDIGENA', 'DIABETES', 'EPOC', 'ASMA', 'INMUSUPR', 'HIPERTENSION',
            'OTRA_COM', 'CARDIOVASCULAR', 'OBESIDAD', 'RENAL_CRONICA', 'TABAQUISMO', 'OTRO_CASO']


def StartCommand(Update, Context):
    Update.message.reply_text('Escribe algo para comenzar')


def HelpCommand(Update, Context):
    Update.message.reply_text('Necesitas mas ayuda? puedes consultar aqui->\n\n'
                              'Aqui puedes consultar las noticias de covid-19:\n'
                              '1. http://www.imss.gob.mx/prensa/archivo/202203/105\n'
                              'Tramites que puedes realizar en el imss digital:\n'
                              '2. http://www.imss.gob.mx/covid-19/tramites\n'
                              '¿Tuviste covid?, aqui puedes consultar tratamientos post-covid en el imss digital:\n'
                              '3. http://www.imss.gob.mx/covid-19/rehabilitacion')


def HandleMessage(Update, Context):
    text = str(Update.message.text).lower()
    answer = MenuKroneBot(text, Update)


    Update.message.reply_text(answer, parse_mode='Markdown')


def ImageHandler(Update, Context):
    file = Update.message.photo[0].file_id
    obj = Context.bot.get_file(file)
    obj.download()

    Update.message.reply_text("Image received")


def Error(Update, Context):
    print(f"Update {Update}  Error causado {Context.error}")


def get_database():
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = '27017'
    MONGODB_TIMEOUT = 1000

    URI_CONNECTION = "mongodb://" + MONGODB_HOST + ":" + MONGODB_PORT + "/"

    try:
        client = pymongo.MongoClient(URI_CONNECTION, serverSelectionTimeoutMS=MONGODB_TIMEOUT)
        client.server_info()
        print('OK -- Connected to MongoDB at server %s' % (MONGODB_HOST))
        db = client['kroneBot']
        col = db['persona']
    except pymongo.errors.ServerSelectionTimeoutError as error:
        print('Error with MongoDB connection: %s' % error)
    except pymongo.errors.ConnectionFailure as error:
        print('Could not connect to MongoDB: %s' % error)


def predict_class():
    DF = pd.read_csv(r'C:\Users\User\Desktop\kronebot\kroneBot.csv')
    X = DF[features]
    y = DF['RESULTADO_LAB']
    X.astype('int64')
    y.astype('int64')

    dtree = DecisionTreeClassifier()
    dtree = dtree.fit(X, y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
    y_hat = dtree.predict(X_test)
    print(classification_report(y_test, y_hat))
    cm = confusion_matrix(y_test, y_hat)
    print('Confusion matrix\n\n', cm)
    print('\nTrue Positives(TP) = ', cm[0, 0])
    print('\nTrue Negatives(TN) = ', cm[1, 1])
    print('\nFalse Positives(FP) = ', cm[0, 1])
    print('\nFalse Negatives(FN) = ', cm[1, 0])
    exit()

    r = export_text(dtree, feature_names=features)
    print(r)

    print(f'El resultado es "1" : {dtree.predict([[1, 2, 35, 2, 2, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2]])[0]}')
    print(f'El resultado es "2" : {dtree.predict([[2, 2, 52, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2]])[0]}')
    print(f'El resultado es "1" : {dtree.predict([[2, 1, 36, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 2, 2]])[0]}')
    print(f'El resultado es "2" : {dtree.predict([[2, 2, 45, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2]])[0]}')


def MenuKroneBot(input_text, Update):
    message = str(input_text).lower()
    answers = []
    user = Update.message.chat
    if message in ("ola", "hola", "h0la", "hol4", "ho1a", "kronee bot", "hola, como estas?"):

        return "Hola, como puedo ayudarte? " + str(user.first_name) + " " + str(user.last_name) + " (@" + str(
            user.username) + ")\nSoy Kronee Bot el cual te puede dar un pronostico de tener covid en base a unas preguntas," \
                             " Quieres continuar?\n\n" \
                             "1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                                         " para obtener mas informacion"


    if message in ("Krone Bot", "como estas?", "1", "2"):
        return "Soy Krone Bot"

    return "No te entiendo"


def QuestionCovid(input_text):
    message = str(input_text).lower()
    if message == "1":
        print("hola1")
        return "hola"
    if message == "2":
        print("hola2")
        return "hola"
    else:
        print("Solo Numeros")
        return "hola"


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
