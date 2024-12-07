import sqlite3, uuid, sys

class QBlog:
    def __init__(self, dbFile="dbs/qBlog.db"):
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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS goods(
                id TEXT PRIMARY KEY,
                articleId TEXT NOT NULL,
                ip TEXT NOT NULL
            )
        """)
        self.conn.commit()
    def newArticle(self, title:str, subTitle:str, contnet:str, ip:str):
        articleId = str(uuid.uuid4())
        self.cursor.execute("INSERT INTO blogs (id, title, subTitle, content, ip) VALUES (?, ?, ?, ?, ?)",(articleId, title, subTitle, contnet, ip))
        self.conn.commit()
        return articleId
    
    def deleteArticleFromId(self, articleId:str):
        self.cursor.execute("DELETE FROM blogs WHERE id=?",(articleId,))
        self.conn.commit()
    def deleteArticleFromIp(self, authorIp:str):
        self.cursor.execute("DELETE FROM blogs WHERE ip=?",(authorIp,))
        self.conn.commit()
    def deleteArticleAll(self):
        self.cursor.execute("DELETE FROM blogs")
        self.conn.commit()
    
    def getArticleFromId(self, articleId:str):
        self.cursor.execute("SELECT * FROM blogs WHERE id=?",(articleId,))
        return self.cursor.fetchone()
    def getArticleFromIp(self, authorIp:str):
        self.cursor.execute("SELECT * FROM blogs WHERE ip=?",(authorIp,))
        return self.cursor.fetchall()
    def getArticleAll(self):
        self.cursor.execute("SELECT * FROM blogs")
        return self.cursor.fetchall()
    
    def newGood(self, articleId:str, ip:str):
        self.cursor.execute("INSERT INTO goods (id, articleId, ip) VALUES (?, ?, ?)",(str(uuid.uuid4()), articleId, ip))
        self.conn.commit()
    def getGoodAll(self):
        self.cursor.execute("SELECT * FROM goods")
        return self.cursor.fetchall()
    def getGoodArticleIdAndIp(self, articleId:str, ip:str):
        self.cursor.execute("SELECT * FROM goods WHERE articleId=? AND ip=?",(articleId, ip))
        return self.cursor.fetchone()

def control():
    qBlog = QBlog()
    while True:
        print("deleteFromIp:1, getAll:2, getFromIp:3, getFromId:4, deleteAll:5, deleteFromId:6, exit:7")
        mode = input("input mode:")
        if mode == "1":
            qBlog.deleteArticleFromIp(input("authorIp:"))
        elif mode == "2":
            print(qBlog.getArticleAll())
        elif mode == "3":
            print(qBlog.getArticleFromIp(input("authorIp:")))
        elif mode == "4":
            print(qBlog.getArticleFromId(input("articleId:")))
        elif mode == "5":
            qBLog.deleteArticleAll()
        elif mode == "6":
            qBlog.deleteArticleFromId(input("articleId:"))
        elif mode == "7":
            sys.exit()
        print("end")

if __name__ == "__main__":
    control()