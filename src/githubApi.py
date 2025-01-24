import requests

class GithubAPI():
    def __init__(self, user : str, repo : str):
        self.user = user
        self.repo = repo
    def getLatestRelease(self) -> dict:
        res = requests.get(f"https://api.github.com/repos/{self.user}/{self.repo}/releases")
        if str(res.status_code)[0] != "2":
            return {}
        resJ = res.json()
        return resJ[0]
    def getLatestReleaseAssetDownlodURLs(self) -> list[str]:
        urls = []
        latestRelease = self.getLatestRelease()
        if latestRelease == {}:
            return []
        latestReleaseID = latestRelease["id"]
        res = requests.get(latestRelease["assets_url"])
        if str(res.status_code)[0] != "2":
            return []
        for asset in res.json():
            urls.append(asset["browser_download_url"])
        return urls
