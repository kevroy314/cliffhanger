from cliffhanger.database.user import User
from cliffhanger.utils.globals import data_location
from sqlitedict import SqliteDict
import string, random
import os

class Session():
    def __init__(self, session_id):
        self.session_id = session_id
        self.session_db = SqliteDict(os.path.join(data_location, session_id), autocommit=True)
        self.users = {}
        
        if 'users' not in self.session_db:
            self.session_db['users'] = {}
        else:
            for username in self.session_db['users']:
                self.users[username] = User(self.session_id, username)

    def new_user(self, username):
        if username not in self.users:
            new_user = User(self.session_id, username)
            self.users[username] = new_user
            self.session_db['users'] = list(self.users.keys()) #session database only stores keys
            return new_user
        raise ValueError("Username taken in this session.")

    @staticmethod
    def create_session():
        allowed_letters = string.ascii_lowercase.replace('i', '') \
                                                .replace('l', '') \
                                                .replace('o', '')
        allowed_digits = string.digits.replace("0", "") \
                                      .replace("1", "")
        session_id = ''.join(random.choices(allowed_letters + allowed_digits, k=8))
        return Session(session_id)

    @staticmethod
    def get_session(session_id):
        return Session(session_id)
    