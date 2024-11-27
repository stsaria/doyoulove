import threading, hashlib, os
from flask import Flask, render_template, request, redirect, url_for

os.makedirs("dbs", exist_ok=True)

from qBlog import QBlog
qBlog = QBlog()

class Web:
    app = Flask(import_name="NanceChat", template_folder="src/templates", static_folder="src/static")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    cursor = None
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
    @app.route("/")
    def index():
        return render_template("main/index.html")
    @app.route("/valorant")
    def varorant():
        return render_template("main/valorant.html")
    @app.route("/qBlog/")
    def qBlogIndex():
        blogs = [{"id":blog[0], "title":blog[1], "subTitle":blog[2], "ip":blog[4]} for blog in qBlog.getAll()]
        return render_template("qBlog/index.html", blogs=blogs)
    @app.route("/qBlog/blog")
    def qBlogViewer():
        articleId = request.args.get("id")
        if not articleId:
            return redirect("qBlog")
        articleId, title, subTitle, content, authorIp = qBlog.getFromId(articleId)
        if None in [articleId, title, subTitle, content, authorIp]:
            return redirect("qBlog")
        return render_template("qBlog/blog.html", title=title, subTitle=subTitle, content=content, articleId=hashlib.md5(authorIp.encode()).hexdigest()[:8])
    @app.route("/qBlog/new", methods=["GET", "POST"])
    def qBlogNew():
        title = ""
        subTitle = ""
        content = ""
        if request.method == "GET":
            return render_template("qBlog/new.html", title=title, subTitle=subTitle, content=content)
        elif request.method == "POST":
            title = request.form.get("title")
            subTitle = request.form.get("subTitle")
            content = request.form.get("content")
            if not (title and subTitle and content):
                return "fuck pram", 400
            elif not (5<=len(title)<=14 and 0<=len(subTitle)<=20 and 30<=len(content)<=5000):
                return render_template("qBlog/new.html", err=f"条件にクリアしていません<br>タイトル:{len(title)}文字<br>サブタイトル:{len(subTitle)}文字<br>内容:{len(content)}文字", title=title, subTitle=subTitle, content=content)
            elif not len(qBlog.getFromIp(request.remote_addr))<=10:
                return render_template("qBlog/new.html", err="投稿した記事の数が10個に達しました<br>次のリセットまで待ってください", title=title, subTitle=subTitle, content=content)
            articleId = qBlog.new(title, subTitle, content, request.remote_addr)
            return redirect(url_for("qBlogViewer", _method="GET", id=articleId))
    def runWeb(self):
        self.app.run(self.host, self.port)

def scheduleDeletionOneWeek():
    while True:
        time.sleep(60*60*24*7)
        qBlog.deleteAll()

if __name__ == "__main__":
    threading.Thread(target=scheduleDeletionOneWeek, daemon=True).start()
    web = Web()
    web.runWeb()
