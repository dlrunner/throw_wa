from database.database import Database

class DatabaseConfig:
    def __init__(self):
        self.db_config = {
            'host': '127.0.0.1',
            'user': 'nlrunner',
            'password': 'nlrunner',
            'database': 'nlrunner_db'
        }
        self.db = None

    def connect(self):
        try:
            self.db = Database(**self.db_config)
            self.db.connect()
            self.db.create_table()
        except Exception as e:
            print(f"Database 연결 오류: {e}")
            raise

    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db
