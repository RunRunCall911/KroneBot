import multiprocessing
import Constants as keys
import logging
import sched
import time as time_module
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
from sklearn.tree import DecisionTreeClassifier

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

dictUsersContinue = {}
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
OTRO_CASO, \
PHOTO, \
CONTINUIDAD, \
FECHA, \
TRATAMIENTO = range(21)





# DATA BASE
def get_database():
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = '27017'
    MONGODB_TIMEOUT = 1000

    URI_CONNECTION = "mongodb://" + MONGODB_HOST + ":" + MONGODB_PORT + "/"

    try:
        client = pymongo.MongoClient(URI_CONNECTION, serverSelectionTimeoutMS=MONGODB_TIMEOUT)
        client.server_info()
        print('OK -- Connected to MongoDB at server %s' % MONGODB_HOST)
        db = client['kroneBot']
        col = db['persona']
        return col
    except pymongo.errors.ServerSelectionTimeoutError as error:
        print('Error with MongoDB connection: %s' % error)
        return -1
    except pymongo.errors.ConnectionFailure as error:
        print('Could not connect to MongoDB: %s' % error)
        return -1


# PREDICTOR
def predict_class(listFeatures):
    #DF = pd.read_csv(r'C:\Users\User\Desktop\kronebot\kroneBot.csv')
    DF = pd.DataFrame(list(get_database().find()))
    X = DF[features]
    y = DF['RESULTADO_LAB']
    X.astype('int64')
    y.astype('int64')

    dtree = DecisionTreeClassifier()
    dtree = dtree.fit(X, y)

    #NEW REGISTER
    predictAnswer = dtree.predict([[listFeatures[0], listFeatures[2], listFeatures[3], listFeatures[1],
                                    listFeatures[4], listFeatures[5], listFeatures[6],
                                    listFeatures[7], listFeatures[8], listFeatures[10],
                                    listFeatures[11], listFeatures[11], listFeatures[9],
                                    listFeatures[13], listFeatures[14], listFeatures[15]]])[0]

    return predictAnswer

# RESPUESTAS 1 = SI
# RESPUESTA  2 = No


# BOT TELEGRAM
def start(update: Update, context: CallbackContext, ) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    dictUsers[user.username] = []
    update.message.reply_text(
        "Hola " + str(user.first_name) + " " + str(user.last_name) + " (@" + str(
            user.username) + ")\nSoy Kronee Bot el cual te puede dar un pronostico de tener covid en base a unas preguntas," \
                             " Quieres continuar?" \
        + "\n\n" + "¿Necesitas ayuda?\nEscribe o pica aqui ==>'/help'" + " para obtener mas informacion" \
        + "\n\nSi deseas cancelar la encuesta solo escribe o pica aqui ==> /cancel"\
        + "\n\n© 2022 Ronaldo Nunez y Adan Palacios, Inc. Todos los derechos reservados."
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
        ),
    )

    return CONSENTIMIENTO


def sexo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Femenino', 'Masculino']]
    user = update.message.chat
    logger.info("acepto la conversacion %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        update.message.reply_text(
            "Cual es tu sexo " + str(user.first_name) + " " + str(user.last_name) + \
            "? \n\n¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
            ,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
            ),
        )
    elif update.message.text == "No":
        update.message.reply_text(
            "Gracias " + str(user.first_name) + " " + str(user.last_name) + \
            " por tomarte tu tiempo, que tengas buen dia\n\n" + "¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
        )
        return ConversationHandler.END

    return SEXO


def embarazo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("su sexo %s: %s", user.first_name, update.message.text)
    if update.message.text == 'Femenino':
        dictUsers[user.username].append(1)
        update.message.reply_text(
            "Estas embarazada " + str(user.first_name) + " " + str(user.last_name) + \
            "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
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
            " toca aqui por favor para avanzar ==> /skip." + "\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" \
                                                                     " para obtener mas informacion"
            ,
        )

    return EMBARAZO


def skip_embarazo(update: Update, context: CallbackContext) -> int:
    user = update.message.chat
    dictUsers[user.username].append(2)
    logger.info("tuvo embarazo %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        "Cual es tu edad " + str(user.first_name) + " " + str(user.last_name) + \
        "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
    )

    return EDAD


def edad(update: Update, context: CallbackContext) -> int:
    user = update.message.chat
    logger.info("tuvo embarazo %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Cual es tu edad " + str(user.first_name) + " " + str(user.last_name) + \
        "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
    )

    return EDAD


def neumonia(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo edad %s: %s", user.first_name, update.message.text)
    dictUsers[user.username].append(update.message.text)
    update.message.reply_text(
        "Tienes Neumonia " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return NEUMONIA


def indigena(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo neumonia %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Eres indigena " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return INDIGENA


def diabetes(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("pertenece a grupo indigena %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes Diabetes " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return DIABETES


def epoc(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tiene diabetes %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes Enfermedad Pulmonar Cronica " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return EPOC


def asma(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo epoc %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes Asma " + str(user.first_name) + " " + str(user.last_name) +
        "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" +
        " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return ASMA


def inmusuper(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo asma %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes inmunosupresión " + str(user.first_name) + " " + str(user.last_name) +
        "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'"
        + " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return INMUSUPR


def hipertension(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo inmunosupresión %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes Hipertension " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return HIPERTENSION


def otra_com(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo hipertension %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes otra complicacion " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return OTRA_COM


def cardiovascular(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo otra complicacion %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes alguna enfermedad Cardiovascular " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return CARDIOVASCULAR


def obesidad(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("Tiene alguna enfermedad Cardiovascular %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes Obesidad " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return OBESIDAD


def renal_cronica(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("Tiene obesidad %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Tienes insuficiencia renal cronica " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return RENAL_CRONICA


def tabaquismo(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo renal cronico %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    update.message.reply_text(
        "Fumas con frecuencia " + str(user.first_name) + " " + str(user.last_name)
        + "?\n\n" + "¿Necesitas ayuda?\nEscribe '/help'" + " para obtener mas informacion"
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return TABAQUISMO


def otro_caso(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    logger.info("tuvo tabaquismo %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    msg = "¿Has tenido contacto con alguien positivo a covid-19 recientemente? " + str(user.first_name) + " " + str(
        user.last_name) + \
          "\n\n" + "¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
    update.message.reply_text(
        msg,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
        ),
    )

    return OTRO_CASO


def final(update: Update, context: CallbackContext) -> int:
    user = update.message.chat
    logger.info("Ha tenido contacto con alguien positivo a covid-19 recientemente %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        dictUsers[user.username].append(1)
    elif update.message.text == "No":
        dictUsers[user.username].append(2)
    listFeatures = dictUsers.get(user.username)
    msg = ""
    prediction = predict_class(listFeatures)
    if prediction == "1":
        msg = "\nEl resultado dio positivo, esto no significa que tengas COVID-19, pero tienes altas probabilidades " \
              "dentro de mi sistema," \
              " te invito a que realices una cita al IMSS Digital portal web ==> (http://www.imss.gob.mx/cita-medica) ya sea " \
              "en su pagina web o descargando la app para iOS o Android " \
              "\n\nel link Android: https://play.google.com/store/apps/details?id=st.android.imsspublico" \
              "\n\nel link iOS: https://itunes.apple.com/us/app/imss-digital/id975273006?mt=8\n\nesto para que un medico realice las " \
              "pruebas pertinentes y asi te indique un tratamiento\n\nNOTA: para dar continuidad y mejorar el sistema te invitamos a picar aqui ==> /continue" \
              " esto ayudara bastante mi sistema para asi lograr tener mejores predicciones  "
    elif prediction == "2":
        msg = "\nEl resultado dio negativo, mi sistema indica que tienes altas probabilidades de no tener COVID-19," \
              " aunque si tienes sintomas" \
              "te invito a sacar una cita en IMSS Digital web (http://www.imss.gob.mx/cita-medica) para que un " \
              "medico te realice las pruebas pertinentes\n\nNOTA: para dar continuidad y mejorar el sistema te invitamos a picar aqui ==> /continue" \
              " esto ayudara bastante mi sistema para asi lograr tener mejores predicciones "
    update.message.reply_text("Gracias " + str(user.first_name) + " " + str(
        user.last_name) + " por tu participacion, estare al pendiente para ti,\n" + msg + " ")

    return ConversationHandler.END


def continue_covid(update: Update, context: CallbackContext, ) -> int:
    reply_keyboard = [['Si', 'No']]
    user = update.message.chat
    dictUsersContinue[user.username] = []
    update.message.reply_text(
        "Que tal " + str(user.first_name) + " " + str(user.last_name) + " (@" + str(
            user.username) + ")\nGracias por querer darle continuidad al proceso, el proceso de continuidad es"
                             " \n\n1) Fecha de tu Cita en el IMSS\n2) Resultado de IMSS en tener COVID\n"
                             "3) Foto de posible tratamiento\n\nDeseas continuar en este proceso?" \
        + "\n\n" + "¿Necesitas ayuda?\nEscribe o pica aqui ==>'/help'" + " para obtener mas informacion" \
        + "\n\nSi deseas cancelar la encuesta solo escribe o pica aqui ==> /cancel" \
        + "\n\n© 2022 Ronaldo Nunez y Adan Palacios, Inc. Todos los derechos reservados."
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Si o No?'
        ),
        )

    return CONTINUIDAD


def fecha(update: Update, context: CallbackContext) -> int:
    user = update.message.chat
    logger.info("Acepto Continuidad COVID %s: %s", user.first_name, update.message.text)
    if update.message.text == "Si":
        update.message.reply_text(
            "Cual es la fecha de tu cita en el IMSS  " + str(user.first_name) + " " + str(user.last_name) + \
            "?\n\nUtilizar el formato AAAA-MM-DD\n\n" + "¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
        )
    elif update.message.text == "No":
        update.message.reply_text(
            "Gracias " + str(user.first_name) + " " + str(user.last_name) + \
            " por tomarte tu tiempo, que tengas buen dia\n\n" + "¿Necesitas ayuda?\nEscribe '/help' para obtener mas informacion"
        )
        return ConversationHandler.END

    return FECHA


def my_function():
    print("Working")


def start_scheduler(date):
    scheduler = sched.scheduler(time_module.time, time_module.sleep)
    #date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    # date_obj = date_obj + datetime.timedelta(days=1)
    t = time_module.strptime(date + ' 16:30:00', '%Y-%m-%d %H:%M:%S')
    t = time_module.mktime(t)
    scheduler.enterabs(t, 1, my_function, ())
    scheduler.run()


def tratamiento(update: Update, context: CallbackContext, ) -> int:
    user = update.message.chat
    fecha_cita = update.message.text
    logger.info("Fecha de Cita IMSS %s: %s", user.first_name, fecha_cita)
    dictUsersContinue[user.username] = []
    process2 = multiprocessing.Process(target=start_scheduler, args=(fecha_cita,))
    process2.start()
    process2.join()
    update.message.reply_text(
        "Que tal " + str(user.first_name) + " " + str(
            user.last_name) + " me puedes compartir una fotografia de tu tratamiento "
                              "si no deseas compartir la fotografia pica aqui ==> /skip",
        reply_markup=ReplyKeyboardRemove(),
    )

    return TRATAMIENTO



def photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(str(user.username) + '.jpg')
    logger.info("Tratamiento de %s: %s", user.first_name, str(user.username) + '.jpg')

    reply_keyboard = [['Positivo', 'Negativo']]
    user = update.message.chat
    update.message.reply_text(
        "Ultima pregunta  " + str(user.first_name) + " " + str(
            user.last_name) + ")\n\nEn tu resultado fuiste positivo o negativo? "
                              "\n\n Selecciona la respuesta abajo",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Positivo o Negativo?'
        ),
    )

    return PHOTO


def skip_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s no envio la photo.", user.first_name)

    reply_keyboard = [['Positivo', 'Negativo']]
    user = update.message.chat
    update.message.reply_text(
        "Ultima pregunta  " + str(user.first_name) + " " + str(
            user.last_name) + ")\n\nEn tu resultado fuiste positivo o negativo? "
                              "\n\n Selecciona la respuesta abajo",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Positivo o Negativo?'
        ),
    )

    return PHOTO


def continue_fin(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s no envio la photo.", user.first_name)

    if update.message.text == "Positivo":
        update.message.reply_text(
            "Cuidate mucho " + str(user.first_name) + " " + str(user.last_name) + \
            "\n\nRecuerda que aun teniendo las vacunas puedes ponerte grave, resguardate y cuida a tus familiares\n"
            "Hasta pronto, tu amigo Kronee Bot\n"
            "Desarrollado por Ronaldo Nuñez y Adan Palacios."
        )

    elif update.message.text == "Negativo":
        update.message.reply_text(
            "Cuidate mucho " + str(user.first_name) + " " + str(user.last_name) + \
            "\n\nRecuerda que aun teniendo las vacunas puedes ponerte grave, cuida a tus familiares\n"
            "Hasta pronto, tu amigo Kronee Bot\n"
            "Desarrollado por Ronaldo Nuñez y Adan Palacios."
        )

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Adios, que tengas un buen dia .', reply_markup=ReplyKeyboardRemove()
    )
    dictUsers.pop(user.username)

    return ConversationHandler.END


def HelpCommand(Update, Context):
    Update.message.reply_text('Necesitas mas ayuda? puedes consultar aqui->\n\n'
                              'Aqui puedes consultar las noticias de covid-19:\n'
                              '1. http://www.imss.gob.mx/prensa/archivo/202203/105\n'
                              'Tramites que puedes realizar en el imss digital:\n'
                              '2. http://www.imss.gob.mx/covid-19/tramites\n'
                              '¿Tuviste covid?, aqui puedes consultar tratamientos post-covid en el imss digital:\n'
                              '3. http://www.imss.gob.mx/covid-19/rehabilitacion')


def mainFunc() -> None:
    updater = Updater(keys.API_KEY, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONSENTIMIENTO: [MessageHandler(Filters.regex('^(Si|No)$'), sexo)],
            SEXO: [MessageHandler(Filters.regex('^(Femenino|Masculino)$'), embarazo)],
            EMBARAZO: [MessageHandler(Filters.regex('^(Si|No)$'), edad), CommandHandler('skip', skip_embarazo)],
            EDAD: [MessageHandler(Filters.text & ~Filters.command, neumonia)],
            NEUMONIA: [MessageHandler(Filters.regex('^(Si|No)$'), indigena)],
            INDIGENA: [MessageHandler(Filters.regex('^(Si|No)$'), diabetes)],
            DIABETES: [MessageHandler(Filters.regex('^(Si|No)$'), epoc)],
            EPOC: [MessageHandler(Filters.regex('^(Si|No)$'), asma)],
            ASMA: [MessageHandler(Filters.regex('^(Si|No)$'), inmusuper)],
            INMUSUPR: [MessageHandler(Filters.regex('^(Si|No)$'), obesidad)],
            OBESIDAD: [MessageHandler(Filters.regex('^(Si|No)$'), hipertension)],
            HIPERTENSION: [MessageHandler(Filters.regex('^(Si|No)$'), otra_com)],
            OTRA_COM: [MessageHandler(Filters.regex('^(Si|No)$'), cardiovascular)],
            CARDIOVASCULAR: [MessageHandler(Filters.regex('^(Si|No)$'), renal_cronica)],
            RENAL_CRONICA: [MessageHandler(Filters.regex('^(Si|No)$'), tabaquismo)],
            TABAQUISMO: [MessageHandler(Filters.regex('^(Si|No)$'), otro_caso)],
            OTRO_CASO: [MessageHandler(Filters.regex('^(Si|No)$'), final)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    continue_handler = ConversationHandler(
        entry_points=[CommandHandler('continue', continue_covid)],
        states={
            CONTINUIDAD: [MessageHandler(Filters.regex('^(Si|No)$'), fecha)],
            FECHA: [MessageHandler(Filters.text & ~Filters.command, tratamiento)],
            TRATAMIENTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            PHOTO: [MessageHandler(Filters.regex('^(Positivo|Negativo)$'), continue_fin)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(CommandHandler("help", HelpCommand))

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(continue_handler)

    updater.start_polling()

    updater.idle()


process = multiprocessing.Process(target=mainFunc)

if __name__ == '__main__':
    process.start()
    process.join()
