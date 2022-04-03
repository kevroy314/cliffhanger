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
        session_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.db[session_name] = Session(session_name)
        return session_name

    def new_user(self, username, session_name):
        if username not in self.db[session_name].users:
            new_user = User(username)
            self.db[session_name].users[username] = new_user
            return True
        raise ValueError("Username taken in this session.")

    def update_user(self, username, session_name, **kwargs):
        self.db[session_name].users[username].update(**kwargs)

    def close(self):
        self.db.close()