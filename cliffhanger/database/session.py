from cliffhanger.database.user import User

class Session():
    def __init__(self, session_id):
        self.session_id = session_id
        self.users = {}
        pass

    def new_user(self, username):
        if username not in self.users:
            new_user = User(username)
            self.users[username] = new_user
            return True
        raise ValueError("Username taken in this session.")
