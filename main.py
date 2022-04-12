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

features = ['SEXO', 'TIPO_PACIENTE', 'EDAD', 'NEUMONIA',
            'EMBARAZO', 'INDIGENA', 'DIABETES', 'EPOC', 'ASMA', 'INMUSUPR', 'HIPERTENSION',
            'OTRA_COM', 'CARDIOVASCULAR', 'OBESIDAD', 'RENAL_CRONICA', 'TABAQUISMO', 'OTRO_CASO']


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

    #plt.figure(figsize=(15, 6))
    dtree = DecisionTreeClassifier()
    dtree = dtree.fit(X, y)
    #tree.plot_tree(dtree, feature_names=features, class_names=result, filled=True)
    #plt.show()
    #plt.savefig('covid.pdf', bbox_inches="tight")
    from sklearn.tree import export_text
    r = export_text(dtree, feature_names=features)
    print(r)

    print(f'El resultado es "1" : {dtree.predict([[1, 2, 35, 2, 2, 2, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2]])[0]}')
    print(f'El resultado es "2" : {dtree.predict([[2, 2, 52, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2]])[0]}')
    print(f'El resultado es "1" : {dtree.predict([[2, 1, 36, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 2, 2]])[0]}')
    print(f'El resultado es "2" : {dtree.predict([[2, 2, 45, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2]])[0]}')


def Main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", StartCommand))
    dp.add_handler(CommandHandler("help", HelpCommand))

    dp.add_handler(MessageHandler(Filters.text, HandleMessage))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    predict_class()
    exit()