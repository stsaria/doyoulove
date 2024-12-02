import threading, ipaddress, requests, hashlib, random, time, os
from flask import Flask, render_template, request, redirect, url_for
from concurrent.futures import ThreadPoolExecutor

os.makedirs("dbs", exist_ok=True)

if not os.path.isfile("BANIPs"):
    open("BANIPs", mode="w", encoding="utf-8").close()

from qBlog import QBlog
qBlog = QBlog()

def getJpCidrs():
    cidrs = requests.get("http://ftp.apnic.net/stats/apnic/delegated-apnic-latest").text.splitlines()
    def isJpCidr(cidr:str):
        if cidr.startswith("#"):
            return None
        parts = cidr.split('|')
        if parts[0] == "JP" and (parts[3] == "ipv4" or parts[3] == "ipv6"):
            return parts[4]
        return None
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(isJpCidr, cidrs))
    return [cidr for cidr in results if cidr is not None]

jpCidrs = getJpCidrs()

def isJpIp(ip:str):
    ipO = ipaddress.ip_address(ip)
    if ipO.is_loopback:
        return True
    for jpCidr in jpCidrs:
        if ipO in ipaddress.ip_network(jpCidr):
            return True
    return False

class Web:
    app = Flask(import_name="NanceChat", template_folder="src/templates", static_folder="src/static")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    cursor = None
    def __init__(self, host="0.0.0.0", port=80):
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
        sortType = request.args.get("s", "0")
        blogs = {blog[0]:{"title":blog[1], "subTitle":blog[2], "ip":blog[4], "goods":0} for blog in qBlog.getArticleAll()}
        for good in qBlog.getGoodAll():
            if not good[1] in list(blogs.keys()):
                continue
            blogs[good[1]]["goods"] += 1
        if sortType == "0":
            blogs = dict(reversed(list(blogs.items())))
            blogs = dict(sorted(blogs.items(), key=lambda item: item[1]["goods"], reverse=True)) 
        elif sortType == "1":
            blogs = dict(reversed(list(blogs.items())))
        elif sortType == "3":
            blogs = dict(reversed(list(blogs.items())))
            blogs = dict(sorted(blogs.items(), key=lambda item: item[1]["goods"]))
        elif sortType == "4":
            blogs = dict(random.sample(list(blogs.items()), len(list(blogs.items()))))
        return render_template("qBlog/index.html", blogs=blogs)
    @app.route("/qBlog/blog")
    def qBlogViewer():
        articleId = request.args.get("id")
        if not articleId:
            return redirect(".")
        article = qBlog.getArticleFromId(articleId)
        if not article:
            return redirect(".")
        articleId, title, subTitle, content, authorIp = article
        return render_template("qBlog/blog.html", articleId=articleId, title=title, subTitle=subTitle, content=content, articleIp=hashlib.md5(authorIp.encode()).hexdigest()[:8])
    @app.route("/qBlog/new", methods=["GET", "POST"])
    def qBlogNew():
        title = ""
        subTitle = ""
        content = ""
        if request.method == "GET":
            return render_template("qBlog/new.html", title=title, subTitle=subTitle, content=content)
        elif request.method == "POST":
            if not isJpIp(request.remote_addr):
                return "sry jp only", 403
            title = request.form.get("title")
            subTitle = request.form.get("subTitle")
            content = request.form.get("content", "")
            banIpsF = open("BANIPs", encoding="utf-8")
            banIps = banIpsF.read().split("\n")
            banIpsF.close()
            if not (title and subTitle):
                return "fuck pram", 400
            elif not (5<=len(title)<=14 and 0<=len(subTitle)<=20 and 30<=len(content)<=5000):
                return render_template("qBlog/new.html", err=f"条件にクリアしていません<br>タイトル:{len(title)}文字<br>サブタイトル:{len(subTitle)}文字<br>内容:{len(content)}文字", title=title, subTitle=subTitle, content=content)
            elif request.remote_addr in banIps or request.remote_addr in banIps:
                return render_template("qBlog/new.html", err="あなたはBANされています。\nもし、間違えだと感じたら、Discordでお伝えください", title=title, subTitle=subTitle, content=content)
            articleId = qBlog.newArticle(title, subTitle, content, request.remote_addr)
            return redirect(url_for("qBlogViewer", _method="GET", id=articleId))
    @app.route("/qBlog/good")
    def qBlogGood():
        articleId = request.args.get("id")
        if not isJpIp(request.remote_addr):
            return "sry jp only", 403
        elif not articleId:
            return "fuck pram", 400
        elif not qBlog.getArticleFromId(articleId):
            return "Not found", 404
        elif qBlog.getGoodArticleIdAndIp(articleId, request.remote_addr):
            return "You have already registered good.", 403
        qBlog.newGood(articleId, request.remote_addr)
        return "", 200
    def runWeb(self):
        self.app.run(self.host, self.port)

if __name__ == "__main__":
    web = Web()
    web.runWeb()
