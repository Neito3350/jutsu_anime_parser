from fake_useragent import UserAgent

ua = UserAgent()

HEADERS = {
    "User-Agent":ua.random,
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

OUT_DIR = "./downloaded_anime/"