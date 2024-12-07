import sqlite3, random, uuid, time, sys

class StringUnknower:
    def __init__(self):
        self.unknowsSettings = {
            "probabilities":{
                "abnormal":23,
                "allInAll":20,
            },
            "unknows":{
                "num":"n",
                "eng":"?!~+93j",
                "jpn":"ｲ縺繧繝縲■",
                "all":"╠ОэЧ▐В@^<>/"
            }
        }
    def isHit(self, persent:int):
        if 1 > persent > 100:
            raise ValueError(f"percentages are between 0 and 100(persent = {persent})")
        arr = ["a" if i < 100-persent else "b" for i in range(100)]
        return True if random.choice(arr) == "b" else False
    def unknower(self, s):
        unknowString = ""
        for c in s:
            uni = ord(c)
            if self.isHit(self.unknowsSettings["probabilities"]["abnormal"]):
                if self.isHit(self.unknowsSettings["probabilities"]["allInAll"]):
                    c = random.choice(self.unknowsSettings["unknows"]["all"])
                elif "a" <= c <= "z" or "A" <= c <= "Z":
                    c = random.choice(self.unknowsSettings["unknows"]["eng"])
                elif c.isdecimal():
                    c = random.choice(self.unknowsSettings["unknows"]["num"])
                elif 0x3040 <= uni <= 0x309F or 0x30A0 <= uni <= 0x30FF or 0x4E00 <= uni <= 0x9FFF:
                    c = random.choice(self.unknowsSettings["unknows"]["jpn"])
            unknowString += c
        return unknowString

class ChatButUnknow:
    def __init__(self, dbFile="dbs/chatButUnknow.db"):
        self.conn = sqlite3.connect(dbFile, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                sourceContent TEXT NOT NULL,
                ip TEXT NOT NULL
            )
        """)
    def newMessage(self, content:str, ip:str):
        stringUnknower = StringUnknower()
        self.cursor.execute("INSERT INTO messages (id, content, sourceContent, ip) VALUES (?, ?, ?, ?)",(str(uuid.uuid4()), stringUnknower.unknower(content), content, ip))
        self.conn.commit()
    def deleteMessageFromId(self, messageId:str):
        self.cursor.execute("DELETE FROM messages WHERE id=?",(messageId,))
        self.conn.commit()
    def deleteMessageFromIp(self, authorIp:str):
        self.cursor.execute("DELETE FROM messages WHERE ip=?",(authorIp,))
        self.conn.commit()
    def deleteMessageAll(self):
        self.cursor.execute("DELETE FROM messages")
        self.conn.commit()
    
    def getMessageFromIp(self, authorIp:str):
        self.cursor.execute("SELECT * FROM messages WHERE ip=?",(authorIp,))
        return self.cursor.fetchall()
    def getMessageAll(self):
        self.cursor.execute("SELECT * FROM messages")
        return self.cursor.fetchall()
    def periodicDeletion(self):
        while True:
            time.sleep(60*60*24*7)
            self.deleteMessageAll()

def control():
    qBlog = ChatButUnknow()
    while True:
        print("deleteFromIp:1, getAll:2, getFromIp:3, getFromId:4, deleteAll:5, deleteFromId:6, exit:7")
        mode = input("input mode:")
        if mode == "1":
            qBlog.deleteMessageFromIp(input("authorIp:"))
        elif mode == "2":
            print(qBlog.getMessageAll())
        elif mode == "3":
            print(qBlog.getMessageFromIp(input("authorIp:")))
        elif mode == "4":
            print(qBlog.getMessageFromId(input("messageId:")))
        elif mode == "5":
            qBLog.deleteAll()
        elif mode == "6":
            qBlog.deleteMessageFromId(input("messageId:"))
        elif mode == "7":
            sys.exit()
        print("end")

if __name__ == "__main__":
    control()