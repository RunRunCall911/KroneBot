import Constants as keys

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import pymongo
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.tree import export_text, DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# features
features = ['SEXO', 'EDAD', 'NEUMONIA',
            'EMBARAZO', 'INDIGENA',
            'DIABETES', 'EPOC', 'ASMA',
            'INMUSUPR', 'HIPERTENSION',
            'OTRA_COM', 'CARDIOVASCULAR',
            'OBESIDAD', 'RENAL_CRONICA',
            'TABAQUISMO', 'OTRO_CASO']

dictUsers = {}

logger = logging.getLogger(__name__)

CONSENTIMIENTO, \
SEXO, \
EDAD, \
NEUMONIA, \
EMBARAZO, \
INDIGENA, \
DIABETES, \
EPOC, \
ASMA, \
INMUSUPR, \
HIPERTENSION, \
OTRA_COM, \
CARDIOVASCULAR, \
OBESIDAD, \
RENAL_CRONICA, \
TABAQUISMO, \
OTRO_CASO = range(17)


# DATA BASE
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


# PREDICTOR
def predict_class(listFeatures):
    DF = pd.read_csv(r'C:\Users\User\Desktop\kronebot\kroneBot.csv')
    X = DF[features]
    y = DF['RESULTADO_LAB']
    X.astype('int64')
    y.astype('int64')

    dtree = DecisionTreeClassifier()
    dtree = dtree.fit(X, y)
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
    # y_hat = dtree.predict(X_test)
    # print(classification_report(y_test, y_hat))
    # cm = confusion_matrix(y_test, y_hat)
    # print('Confusion matrix\n\n', cm)
    # print('\nTrue Positives(TP) = ', cm[0, 0])
    # print('\nTrue Negatives(TN) = ', cm[1, 1])
    # print('\nFalse Positives(FP) = ', cm[0, 1])
    # print('\nFalse Negatives(FN) = ', cm[1, 0])

    # r = export_text(dtree, feature_names=features)
    # print(r)
    print(f'El resultado es: {dtree.predict([[int(listFeatures[0]), 32, int(listFeatures[2]),int(listFeatures[3]), int(listFeatures[4]), int(listFeatures[5]), int(listFeatures[6]), int(listFeatures[7]), int(listFeatures[8]), int(listFeatures[9]), int(listFeatures[10]), int(listFeatures[11]), int(listFeatures[12]), int(listFeatures[13]), int(listFeatures[14]), int(listFeatures[15])]])[0]}')
    return 1


# BOT TELEGRAM
def start(update: Update, context: CallbackContext, ) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    dictUsers[user.username] = []
    update.message.reply_text(
        "Hola, como puedo ayudarte? " + str(user.first_name) + " " + str(user.last_name) + " (@" + str(
            user.username) + ")\nSoy Kronee Bot el cual te puede dar un pronostico de tener covid en base a unas preguntas," \
                             " Quieres continuar?\n\n" \
                             "1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                                         " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
        ),
    )

    return CONSENTIMIENTO


def sexo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("acepto la conversacion %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        "Me puedes decir tu sexo " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
        ),
    )
    return SEXO


def embarazo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("su sexo %s: %s", user.first_name, update.message.text)
    print(update.message.text)
    if update.message.text == 'Femenino':
        dictUsers[user.username].append(1)
        update.message.reply_text(
            "Me puedes decir si estas embarazada " + str(user.first_name) + " " + str(user.last_name) + \
            " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                             " para obtener mas informacion"
            ,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
            ),
        )
    elif update.message.text == 'Masculino':
        dictUsers[user.username].append(2)
        update.message.reply_text(
            " " + str(user.first_name) + " " + str(user.last_name) + \
            "toca aqui por favor para avanzar ==> /skip." + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                     " para obtener mas informacion"
            ,
        )

    return EMBARAZO



def edad(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo embarazo %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir tu edad " + str(user.first_name) + " " + str(user.last_name) + \
        "\n\n" + "¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
    )

    return EDAD


def neumonia(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo edad %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si cuentas con Neumonia " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return NEUMONIA


def indigena(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo neumonia %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si eres indigena " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return INDIGENA


def diabetes(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo indigena %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes Diabetes " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return DIABETES


def epoc(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo diabetes %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes Enfermedad Pulmonar Cronica " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return EPOC


def asma(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo epoc %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes Asma " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return ASMA


def inmusuper(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo asma %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes inmune supresion " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return INMUSUPR


def hipertension(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo inmune supresion %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes Hipertensionn " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return HIPERTENSION


def otra_com(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo hipertension %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes otra complicacion " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return OTRA_COM


def cardiovascular(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo otro complicacion %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes enfermedad Cardiovascular " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return CARDIOVASCULAR


def obesidad(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo cardiovascular %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes obesidad " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return OBESIDAD


def renal_cronica(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("es obeso el hdsptm %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si tienes insuficiencia renal cronica " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return RENAL_CRONICA


def tabaquismo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo renal cronico %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Me puedes decir si fumas con frecuencia " + str(user.first_name) + " " + str(user.last_name) + \
        " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                         " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return TABAQUISMO


def otro_caso(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['1', '2']]
    user = update.message.chat
    logger.info("tuvo tabaquismo %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    msg = "Me puedes decir si tuviste contacto con alguien diagnosticado con COVID " + str(user.first_name) + " " + str(
        user.last_name) + \
          " \n\n1) Si\n2) No\n\n " + "*Solo utiliza el numero*" + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                           " para obtener mas informacion"
    update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
        ),
    )

    return OTRO_CASO


def final(update: Update, context: CallbackContext) -> int:
    user = update.message.chat
    logger.info("tuvo contacto %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    listFeatures = dictUsers.get(user.username)
    update.message.reply_text("Gracias " + str(user.first_name) + " " + str(
        user.last_name) + " por tu participacion, estare al pendiente para ti, tu resultado es: " + str(
        predict_class(listFeatures)))

    return ConversationHandler.END


# def photo(update: Update, context: CallbackContext) -> int:
#     """Stores the photo and asks for a location."""
#     user = update.message.from_user
#     photo_file = update.message.photo[-1].get_file()
#     photo_file.download('user_photo.jpg')
#     logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
#     update.message.reply_text(
#         'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
#     )
#
#     return LOCATION
#
#
# def skip_photo(update: Update, context: CallbackContext) -> int:
#     """Skips the photo and asks for a location."""
#     user = update.message.from_user
#     logger.info("User %s did not send a photo.", user.first_name)
#     update.message.reply_text(
#         'I bet you look great! Now, send me your location please, or send /skip.'
#     )
#
#     return LOCATION


def bio(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def HelpCommand(Update, Context):
    Update.message.reply_text('Necesitas mas ayuda? puedes consultar aqui->\n\n'
                              'Aqui puedes consultar las noticias de covid-19:\n'
                              '1. http://www.imss.gob.mx/prensa/archivo/202203/105\n'
                              'Tramites que puedes realizar en el imss digital:\n'
                              '2. http://www.imss.gob.mx/covid-19/tramites\n'
                              '¿Tuviste covid?, aqui puedes consultar tratamientos post-covid en el imss digital:\n'
                              '3. http://www.imss.gob.mx/covid-19/rehabilitacion')


def main() -> None:
    updater = Updater(keys.API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONSENTIMIENTO: [MessageHandler(Filters.regex('^(1|2)$'), sexo)],
            SEXO: [MessageHandler(Filters.regex('^(Femenino|Masculino)$'), embarazo)],
            EMBARAZO: [MessageHandler(Filters.regex('^(1|2)$'), edad), CommandHandler('skip', skip_embarazo)],
            EDAD: [MessageHandler(Filters.text & ~Filters.command, neumonia)],
            NEUMONIA: [MessageHandler(Filters.regex('^(1|2)$'), indigena)],
            INDIGENA: [MessageHandler(Filters.regex('^(1|2)$'), diabetes)],
            DIABETES: [MessageHandler(Filters.regex('^(1|2)$'), epoc)],
            EPOC: [MessageHandler(Filters.regex('^(1|2)$'), asma)],
            ASMA: [MessageHandler(Filters.regex('^(1|2)$'), inmusuper)],
            INMUSUPR: [MessageHandler(Filters.regex('^(1|2)$'), obesidad)],
            OBESIDAD: [MessageHandler(Filters.regex('^(1|2)$'), hipertension)],
            HIPERTENSION: [MessageHandler(Filters.regex('^(1|2)$'), otra_com)],
            OTRA_COM: [MessageHandler(Filters.regex('^(1|2)$'), cardiovascular)],
            CARDIOVASCULAR: [MessageHandler(Filters.regex('^(1|2)$'), renal_cronica)],
            RENAL_CRONICA: [MessageHandler(Filters.regex('^(1|2)$'), tabaquismo)],
            TABAQUISMO: [MessageHandler(Filters.regex('^(1|2)$'), otro_caso)],
            OTRO_CASO: [MessageHandler(Filters.regex('^(1|2)$'), final)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(CommandHandler("help", HelpCommand))

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
