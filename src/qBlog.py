import sqlite3, uuid, sys

class QBlog:
    def __init__(self, dbFile="dbs/blogs.db"):
        self.conn = sqlite3.connect(dbFile, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS blogs(
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                subTitle TEXT NOT NULL,
                content TEXT NOT NULL,
                ip TEXT NOT NULL
            )
        """)
        self.conn.commit()
    def new(self, title:str, subTitle:str, contnet:str, ip:str):
        articleId = str(uuid.uuid4())
        self.cursor.execute("INSERT INTO blogs (id, title, subTitle, content, ip) VALUES (?, ?, ?, ?, ?)",(articleId, title, subTitle, contnet, ip))
        self.conn.commit()
        return articleId
    
    def getFromId(self, articleId:str):
        self.cursor.execute("DELETE FROM blogs WHERE id=?",(articleId,))
        self.conn.commit()
    def getFromIp(self, authorIp:str):
        self.cursor.execute("DELETE FROM blogs WHERE ip=?",(authorIp,))
        self.conn.commit()
    def deleteAll(self):
        self.cursor.execute("DELETE FROM blogs")
        self.conn.commit()
    
    def getFromId(self, articleId:str):
        self.cursor.execute("SELECT * FROM blogs WHERE id=?",(articleId,))
        return self.cursor.fetchone()
    def getFromIp(self, authorIp:str):
        self.cursor.execute("SELECT * FROM blogs WHERE ip=?",(authorIp,))
        return self.cursor.fetchall()
    def getAll(self):
        self.cursor.execute("SELECT * FROM blogs")
        return self.cursor.fetchall()

def control():
    qBLog = QBlog()
    while True:
        print("deleteFromIp:1, getAll:2, getFromIp:3, getFromId:4, deleteAll:5, deleteFromId:6, exit:7")
        mode = input("input mode:")
        if mode == "1":
            qBlog.deleteFromIp(input("authorIp:"))
        elif mode == "2":
            print(qBlog.getAll())
        elif mode == "3":
            print(qBlog.getFromIp(input("authorIp:")))
        elif mode == "4":
            print(qBlog.getFromId(input("authorId:")))
        elif mode == "5":
            qBLog.deleteAll()
        elif mode == "6":
            qBlog.deleteFromId(input("authorId:"))
        elif mode == "7":
            sys.exit()
        print("end")

if __name__ == "__main__":
    control()