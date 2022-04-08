from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
)
import Constants as keys
import Answer as A
import pandas as pd
from pymongo import MongoClient
from sklearn.tree import DecisionTreeClassifier
from sklearn import *
import matplotlib.pyplot as plt
import pymongo


print("Bot iniciando...")

features = ['SEXO', 'TIPO_PACIENTE', 'EDAD', 'NACIONALIDAD', 'INTUBADO', 'NEUMONIA',
            'EMBARAZO', 'INDIGENA', 'DIABETES', 'EPOC', 'ASMA', 'INMUSUPR', 'HIPERTENSION',
            'OTRA_COM', 'CARDIOVASCULAR', 'OBESIDAD', 'RENAL_CRONICA', 'TABAQUISMO', 'OTRO_CASO', 'MIGRANTE', 'UCI']

result = ['1', '2']


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


def get_database():
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = '27017'
    MONGODB_TIMEOUT = 1000

    URI_CONNECTION = "mongodb://" + MONGODB_HOST + ":" + MONGODB_PORT +  "/"

    try:
        client = pymongo.MongoClient(URI_CONNECTION, serverSelectionTimeoutMS=MONGODB_TIMEOUT)
        client.server_info()
        print('OK -- Connected to MongoDB at server %s' % (MONGODB_HOST))
        db = client['kroneBot']
        col = db['persona']
        DF = pd.DataFrame(list(col.find()))
        DF = DF.drop([0, 10])
        DF = DF.reset_index(drop=True)
        DF.drop('FECHA_SINTOMAS', inplace=True, axis=1)
        DF.drop('CLASIFICACION_FINAL', inplace=True, axis=1)
        DF.drop('_id', inplace=True, axis=1)
        DF = DF.iloc[95800:,]
        predict_class(DF)
    except pymongo.errors.ServerSelectionTimeoutError as error:
        print('Error with MongoDB connection: %s' % error)
    except pymongo.errors.ConnectionFailure as error:
        print('Could not connect to MongoDB: %s' % error)


def predict_class(DF):
    X = DF[features]
    y = DF['RESULTADO_LAB']

    y = y.astype("int")

    plt.figure(figsize=(15, 6))
    dtree = DecisionTreeClassifier()
    dtree = dtree.fit(X, y)
    tree.plot_tree(dtree, feature_names=features, class_names=result, filled=True)
    plt.show()
    plt.savefig('covid.pdf', bbox_inches="tight")
    # print(f'El resultado es: {result[dtree.predict([["2", "1", "1", "0.221805", "1", "97", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "2", "99", "97"]])[0]]}')


def Main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", StartCommand))
    dp.add_handler(CommandHandler("help", HelpCommand))

    dp.add_handler(MessageHandler(Filters.text, HandleMessage))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    get_database()
    exit()

