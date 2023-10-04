import sqlite3

connect = sqlite3.connect('bd.db', check_same_thread=False)
cursor = connect.cursor()

def registr(tg_id):
    cursor.execute('''
            INSERT INTO "users" (tg_id) 
            VALUES (?, ?)''', (tg_id))
    connect.commit()

def check(tg_id):
    return cursor.execute('''
        SELECT tg_id 
        FROM "users" 
        WHERE tg_id = ?''', (tg_id,)).fetchone()


resull = cursor.execute('''
CREATE TABLE IF NOT EXISTS
"users"
("id" INTEGER NOT NULL,
"tg_id" INTEGER NOT NULL,
primary key("id" AUTOINCREMENT)
)''')

resull = cursor.execute('''
CREATE TABLE IF NOT EXISTS
"categories"
("id" INTEGER NOT NULL,
"name" TEXT NOT NULL,
"value" TEXT NOT NULL,
primary key("id" AUTOINCREMENT)
)''')

resull = cursor.execute('''
CREATE TABLE IF NOT EXISTS
"subscribes"
("id_user" INTEGER NOT NULL,
"id_category" INTEGER NOT NULL,
FOREIGN KEY (id_user) REFERENCES users(id) ON DELETE CASCADE,
FOREIGN KEY (id_category) REFERENCES categories(id) ON DELETE CASCADE
)''')
connect.commit()
# cursor.execute('''INSERT INTO categories (name,value) VALUES ("Бизнес","business")''')
# cursor.execute('''INSERT INTO categories (name,value) VALUES ("Развлечение", "entertainment")''')
# cursor.execute('''INSERT INTO categories (name,value) VALUES ("Общие","general")''')
# cursor.execute('''INSERT INTO categories (name,value) VALUES ("Здоровье","health")''')
# cursor.execute('''INSERT INTO categories (name,value) VALUES ("Наука","science")''')
# cursor.execute('''INSERT INTO categories (name,value) VALUES ("Спорт","sport")''')
# cursor.execute('''INSERT INTO categories (name,value) VALUES ("Технологии","techology")''')
# connect.commit()

#поиск категории у пользователя
def searchUserCategory(user_id):
    return cursor.execute('''SELECT categories.name
        FROM subscribes 
        INNER JOIN categories ON subscribes.id_category = categories.id
        WHERE subscribes.id_user = ?
        ''',(user_id,)).fetchall()

#Поиск категории в бд
def findCategory(name):
    return cursor.execute('''SELECT id
        FROM categories 
        WHERE name = ?
        ''',(name,)).fetchone()

def findCategoryName(id_category):
    return cursor.execute('''SELECT value
    FROM categories
    WHERE id = ?
    ''',(id_category,)).fetchone()

#отписаться от категории
def deleteSubscribes(tg_id,id_category):
    cursor.execute('''DELETE FROM subscribes 
        WHERE user_id = ?
        AND category_id = ?
        ''', (tg_id, id_category))
    connect.commit()
    return "Вы отписались"

def findUserSubscribes(id_user):
    return cursor.execute('''SELECT categories.name FROM subscribes
    INNER JOIN categories ON categories.id = subscribes.id_category
    WHERE subscribes.id_user = ?
    ''',(id_user,)).fetchall()

def findUserId(tg_id):
    return cursor.execute('''SELECT id
    FROM users
    WHERE tg_id = ?
    ''',(tg_id,)).fetchone()
