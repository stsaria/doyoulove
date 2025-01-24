import threading, ipaddress, requests, hashlib, random, time, sys, re, os
from flask import Flask, render_template, request, redirect, url_for, abort
from concurrent.futures import ThreadPoolExecutor

os.makedirs("dbs", exist_ok=True)

if not os.path.isfile("BANIPs"):
    open("BANIPs", mode="w", encoding="utf-8").close()

from qBlog import QBlog
from chatButUnknow import ChatButUnknow
from githubApi import GithubAPI
chatButUnknow = ChatButUnknow()
qBlog = QBlog()

def getJpCidrs():
    jpCidrs = []
    cidrs = requests.get("http://ftp.apnic.net/stats/apnic/delegated-apnic-latest").text.splitlines()
    for cidr in cidrs:
        if cidr.startswith("#"):
            continue
        parts = cidr.split('|')
        if parts[1] == "JP" and parts[2] in ["ipv4", "ipv6"]:
            subnet = int()
            bitsNeeded = int(parts[4]).bit_length()
            prefixLen = 32 - bitsNeeded
            jpCidrs.append(f"{parts[3]}/{prefixLen}")
    return jpCidrs

if os.path.isfile("jpCidrs"):
    jpCidrsF = open("jpCidrs", encoding="utf-8")
    jpCidrs = jpCidrsF.read().split("\n")
    jpCidrsF.close()
else:
    jpCidrs = getJpCidrs()
    jpCidrsF = open("jpCidrs", mode="w", encoding="utf-8")
    jpCidrsF.write("\n".join(jpCidrs))
    jpCidrsF.close()

def isAllowIp(ip:str):
    ipO = ipaddress.ip_address(ip)
    if ipO.is_loopback:
        return True
    for jpCidr in jpCidrs:
        if ipO in ipaddress.ip_network(jpCidr, strict=False):
            return True
    return False

class Web:
    app = Flask(import_name="Do you love?", template_folder="src/templates", static_folder="src/static")
    if "debug" in sys.argv:
        app.config["TEMPLATES_AUTO_RELOAD"] = True
    cursor = None
    def __init__(self, host="0.0.0.0", port=80):
        self.host = host
        self.port = port
    # main
    @app.route("/")
    def index():
        return render_template("main/index.html")
    @app.route("/valorant")
    def varorant():
        return render_template("main/valorant.html")
    # qBlog
    @app.route("/qBlog/")
    def qBlogIndex():
        sortType = request.args.get("s", "0")
        blogs = {blog[0]:{"title":blog[1], "subTitle":blog[2], "ip":hashlib.md5(blog[4].encode()).hexdigest()[:8], "goods":0} for blog in qBlog.getArticleAll()}
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
        return render_template("qBlog/blog.html", articleId=articleId, title=title, subTitle=subTitle, content=content, authorIp=hashlib.md5(authorIp.encode()).hexdigest()[:8])
    @app.route("/qBlog/new", methods=["GET", "POST"])
    def qBlogNew():
        title = ""
        subTitle = ""
        content = ""
        if request.method == "GET":
            return render_template("qBlog/new.html", title=title, subTitle=subTitle, content=content)
        elif request.method == "POST":
            if not isAllowIp(request.remote_addr):
                return "sry jp only", 403
            title = request.form.get("title", "")
            subTitle = request.form.get("subTitle", "")
            content = request.form.get("content", "")
            banIpsF = open("BANIPs", encoding="utf-8")
            banIps = banIpsF.read().split("\n")
            banIpsF.close()
            if not (5<=len(title.strip())<=14 and 0<=len(subTitle.strip())<=20 and 30<=len(content.strip())<=5000):
                return render_template("qBlog/new.html", err=f"条件にクリアしていません<br>タイトル:{len(title)}文字<br>サブタイトル:{len(subTitle)}文字<br>内容:{len(content)}文字", title=title, subTitle=subTitle, content=content)
            elif request.remote_addr in banIps or request.remote_addr in banIps:
                return render_template("qBlog/new.html", err="あなたはBANされています。\nもし、間違えだと感じたら、Discordでお伝えください", title=title, subTitle=subTitle, content=content)
            articleId = qBlog.newArticle(title, subTitle, content, request.remote_addr)
            return redirect(url_for("qBlogViewer", _method="GET", id=articleId))
    @app.route("/qBlog/good")
    def qBlogGood():
        articleId = request.args.get("id")
        if not isAllowIp(request.remote_addr):
            return "sry jp only", 403
        elif not articleId:
            return "fuck pram", 400
        elif not qBlog.getArticleFromId(articleId):
            return "Not found", 404
        elif qBlog.getGoodArticleIdAndIp(articleId, request.remote_addr):
            return "You have already registered good.", 403
        qBlog.newGood(articleId, request.remote_addr)
        return "", 200
    # chatButUnknow
    @app.route("/chatButUnknow/", methods=["GET", "POST"])
    def chatButUnknowIndex():
        messages = {message[0]:{"content":message[1], "authorIp":hashlib.md5(message[3].encode()).hexdigest()[:8]} for message in reversed(chatButUnknow.getMessageAll())}
        return render_template("chatButUnknow/index.html", yourIp=hashlib.md5(request.remote_addr.encode()).hexdigest()[:8], messages=messages)
    @app.route("/chatButUnknow/new", methods=["POST"])
    def chatButUnknowNew():
        content = request.form.get("content", "")
        banIpsF = open("BANIPs", encoding="utf-8")
        banIps = banIpsF.read().split("\n")
        banIpsF.close()
        if not isAllowIp(request.remote_addr):
            return "sry jp only", 403
        elif not 1 <= len(content.strip()) <= 220:
            return "fuck pram", 400
        elif request.remote_addr in banIps or request.remote_addr in banIps:
            return "banned", 403
        chatButUnknow.newMessage(content, request.remote_addr)
        return redirect(url_for("chatButUnknowIndex", _method="GET"))
    # youCantStopSanpo
    @app.route("/youCantStopSanpo/")
    def youCantStopSanpo():
        return render_template("youCantStopSanpo/index.html")
    # minecraftRecommended
    @app.route("/minecraftRecommended/")
    def minecraftRecommended():
        return render_template("minecraftRecommended/index.html")
    @app.route("/minecraftRecommended/<string:page>")
    def minecraftRecommendedEtc(page:str):
        path = "minecraftRecommended/"
        page = page.replace(".", "")
        if page == "":
            path += "index.html"
        elif not re.match(r'^[a-zA-Z0-9_-]+$', page):
            abort(400)
        elif not os.path.exists(f"src/templates/{path}{page}.html"):
            abort(404)
        else:
            path += f"{page}.html"
        return render_template(path)
    # mySoftWares
    @app.route("/mySoftWares/getMineHuntPvPMainLatestAsset")
    def getMineHuntPvPMainLatestAsset():
        return redirect(GithubAPI("stsaria", "MineHuntPvPMain").getLatestReleaseAssetDownlodURLs()[0])
    def getMineHuntPvPLobbyerLatestAsset():
        return redirect(GithubAPI("stsaria", "MineHuntPvPLobbyer").getLatestReleaseAssetDownlodURLs()[0])
    def runWeb(self):
        self.app.run(self.host, self.port)

if __name__ == "__main__":
    threading.Thread(target=chatButUnknow.periodicDeletion, daemon=True)
    web = Web()
    web.runWeb()
