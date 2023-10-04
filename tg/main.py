import telebot
from bd import *
from telebot import types
from newsapi import NewsApiClient

bot = telebot.TeleBot("6464555572:AAFtDre4jQ_cHbK2PVC28NPV51y4EaVHUqU", parse_mode=None)
newsapi = NewsApiClient(api_key="918d79b4f4414700a31f1471621f38f8")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id=[message.chat.id]
    connect = sqlite3.connect("bd.db")
    cursor = connect.cursor()
    user = cursor.execute("SELECT * from users where tg_id = ?;",(user_id)).fetchone()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_news = types.KeyboardButton('Новости')
    button_categories = types.KeyboardButton('Категории')
    button_sub = types.KeyboardButton('Посмотреть подписки')
    markup.add(button_news,button_categories,button_sub)
    if not user:
        cursor.execute("insert into users ('tg_id') values (?);", user_id)
        connect.commit()
        bot.reply_to(message, "Регистрация прошла успешна",reply_markup=markup)
    else:
        bot.reply_to(message, "Вы уже зарегистрированы",reply_markup=markup)

@bot.message_handler(content_types=['text'])
def bot_message(message):
    connect = sqlite3.connect("bd.db")
    cursor = connect.cursor()
    if message.chat.type=='private':
        def catAllAndDel():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            user_id = [message.chat.id]
            categories = cursor.execute('''SELECT name from categories 
        where categories.id not in (SELECT categories.id from categories
                                   inner JOIN subscribes on categories.id=subscribes.id_category
        INNER join users on subscribes.id_user=users.id
                                   where users.tg_id=?)''', (user_id)).fetchall()
            i = 0
            while i < len(categories):
                categor = types.KeyboardButton(categories[i][0])
                i = i + 1
                back = types.KeyboardButton('Назад')
                markup.add(categor)
            markup.add(back)
            bot.reply_to(message, 'Категории', reply_markup=markup)

        if message.text=='Категории':
            catAllAndDel()

    if message.chat.type == 'private':
        if message.text.startswith('+'):
            user_id = [message.chat.id]
            id=cursor.execute('''SELECT id FROM users WHERE tg_id = ?''', (user_id)).fetchone()
            id=str(id[0])
            subs =cursor.execute('''SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.id_category WHERE id_user = ? ;''', (id)).fetchall()
            mass = []
            i = 0
            while i < len(subs):
                mass.append(subs[i][3])
                i=i+1
            i = 0
            count = 0
            name_sub = message.text[2:]
            while i < len(mass):
                if name_sub == mass[i]:
                    count = count + 1
                i = i + 1
            if count == 0:
                cat_id = cursor.execute('''SELECT id FROM categories WHERE name = ? ; ''', (name_sub,)).fetchall()
                cursor.execute('''INSERT INTO subscribes ('id_user', 'id_category') VALUES (?, ?) ''',(id,cat_id[0][0]))
                connect.commit()
                catAllAndDel()
                bot.reply_to(message, 'Вы подписались')

    connect = sqlite3.connect("bd.db")
    cursor = connect.cursor()

    def subAllAndDel():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        subscribes = cursor.execute(
            '''SELECT name FROM categories INNER JOIN subscribes ON categories.id=subscribes.id_category''').fetchall()
        i = 0
        while i < len(subscribes):
            # print(subscribes[i])
            sub = types.KeyboardButton('- ' + subscribes[i][0])
            i = i + 1
            back = types.KeyboardButton('Назад')
            markup.add(sub)
        markup.add(back)
        bot.reply_to(message, 'Подписки', reply_markup=markup)

    if message.chat.type == 'private':
        if message.text == 'Подписки':
            subAllAndDel()
    if message.chat.type == 'private':
        if message.text.startswith('-'):
            user_id = [message.chat.id]
            id = cursor.execute('''SELECT id FROM users WHERE tg_id = ?''', (user_id)).fetchone()
            id = str(id[0])
            subs = cursor.execute(
                '''SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.id_category WHERE id_user = ? ;''',
                (id)).fetchall()
            mass = []
            i = 0

            count = 0
            name_sub = message.text[2:]
            while i < len(mass):
                if name_sub == mass[i]:
                    count = count + 1
                i = i + 1
            cat_id = cursor.execute('''SELECT id FROM categories WHERE name = ? ; ''', (name_sub,)).fetchall()
            cursor.execute('''DELETE FROM subscribes 
               WHERE id_user = ? AND id_category = ?''',
                           (id, cat_id[0][0]))
            connect.commit()
            subAllAndDel()
            bot.reply_to(message, 'Вы отписались')
        elif message.text == 'Новости':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tg_id = message.from_user.id
            user_id = str(findUserId(tg_id)[0])
            userSub = findUserSubscribes(user_id)
            i = 0
            while i < len(userSub):
                name = types.KeyboardButton("Новости"+" ".join(userSub[i]))
                markup.add(name)
                i = i + 1
                back = types.KeyboardButton('Назад')
            markup.add(back)
            bot.reply_to(message, "Новости про:", reply_markup=markup)

        elif message.text.startswith("Посмотреть"):
            tg_id = message.from_user.id
            user_id = str(findUserId(tg_id)[0])
            subscribes = searchUserCategory(user_id)
            arr = []
            i = 0
            while i < len(subscribes):
                arr.append(subscribes[i])
                i = i + 1
            i = 0
            count = 0
            text = message.text[23:]
            while i < len(arr):
                if text == arr[i][0]:
                    count = count + 1
                i = i + 1
            if count > 0:
                category_id = findCategory(text)[0]
                category_name = findCategoryName(category_id)[0]
                top_headlines = newsapi.get_top_headlines(category=category_name, language='ru')
                bot.send_message(message.from_user.id,
                                 f'{top_headlines["articles"][0]["title"]}\n {top_headlines["articles"][0]["url"]}')

        elif message.text == 'Назад':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_news = types.KeyboardButton('Новости')
            button_categories = types.KeyboardButton('Категории')
            button_sub = types.KeyboardButton('Подписки')
            markup.add(button_news, button_categories, button_sub)
            bot.reply_to(message, "Назад", reply_markup=markup)

bot.infinity_polling(none_stop=True)


