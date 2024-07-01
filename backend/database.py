import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host, user, password, database) : 
        self.config = {
            'host': '127.0.0.1',
            'user': 'nlrunner',
            'password': 'nlrunner',
            'database': 'nlrunner_db'
        }
        self.conn = None
        self.cursor = None

    def connect(self) :
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("mysql 연결 성공")
        except Error as e :
            print(f"mysql 연결 오류 :  {e}")
            raise
    
    def close(self) :
        if self.conn:
            self.conn.close()
            print("데이터 베이스 연결 종료")
    
    def create_table(self) : 
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS test_table
                                  (id INT AUTO_INCREMENT PRIMARY KEY,
                                   url TEXT,
                                    title TEXT,
                                   content TEXT)''')
            self.conn.commit()
            print("테이블 생성 성공")
        except Error as e :
            print(f"테이블 생성 에러 발생 {e}")
            self.conn.rollback()
            raise
    
    def insert_video(self, url, content):
        try:
            self.cursor.execute("INSERT INTO test_table (url, content) VALUES (%s, %s)", (url, content))
            self.conn.commit()
            video_id = self.cursor.lastrowid
            return video_id
        except Error as e:
            print(f"유튜브 삽입 에러: {e}")
            self.conn.rollback()
            raise
    
    def insert_crawling(self, url, content, title) :
        try:
            self.cursor.execute("INSERT INTO test_table (url, title, content) VALUES (%s, %s, %s)",(url, title, content))
            self.conn.commit()
            crawling_id = self.cursor.lastrowid
            return crawling_id
        except Error as e:
            print(f"크롤링 텍스트 삽입 에러 : {e}")
            self.conn.rollback()
            raise

    def insert_pdf(self, pdf_url, content) :
        try:
            self.cursor.execute("INSERT INTO test_table (url, content) VALUES (%s, %s)",(pdf_url, content))
            self.conn.commit()
            pdf_id = self.cursor.lastrowid
            return pdf_id
        except Error as e :
            print(f"pdf 텍스트 삽입 에러: {e}")
            self.conn.rollback()
            raise

