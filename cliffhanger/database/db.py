from sqlitedict import SqliteDict
from cliffhanger.database.session import Session
from cliffhanger.database.user import User
import random, string

class DB():
    def __init__(self, db_filename):
        self.db = SqliteDict(db_filename, autocommit=True)
        # self.db['some_key'] = any_picklable_object
        # print(self.db['some_key'])  # prints the new value
        # for key, value in self.db.iteritems():
        #     print(key, value)
        # print(len(self.db))

    def new_session(self):
        allowed_letters = string.ascii_lowercase.replace('i', '') \
                                                .replace('l', '') \
                                                .replace('o', '')
        allowed_digits = string.digits.replace("0", "") \
                                      .replace("1", "")
        session_id = ''.join(random.choices(allowed_letters + allowed_digits, k=8))
        self.db[session_id] = Session(session_id)
        return session_id

    def close(self):
        self.db.close()

data = DB("data/db.db")

def new_session():
    global data
    return data.new_session()

def get_session(session_id):
    global data
    return data.db[session_id]

def update_session_contents(session):
    data.db[session.session_id] = session