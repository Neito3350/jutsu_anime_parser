import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import makedirs
from os.path import isfile
from re import sub
from fake_useragent import UserAgent

ua = UserAgent()

HEADERS = {
    "User-Agent":ua.random,
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

OUT_DIR = "./downloaded_anime/"

class jutsuParser():
    def __init__(self):
        pass

    def get_all_episodes(self, anime_url:str, parse_black_buttons=True):
        """функция парсит все ссылки эпизоды аниме"""
        episodes = []

        r = requests.get(anime_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "lxml")

        # парсинг ссылок на эпизоды
        if parse_black_buttons:
            links = soup.find_all("a", class_={"short-btn green video the_hildi", "short-btn black video the_hildi"}, attrs="href")
        else:
            links = soup.find_all("a", class_={"short-btn green video the_hildi"}, attrs="href")

        # добавление полученных ссылок в список
        for link in links:
            episodes.append("https://jut.su{}".format(link["href"]))

        return episodes

    def get_and_download(self, link_from_episode:str, quality:str):
        """функция парсит название эпизода, название аниме и прямую ссылку на видео и возвращает результат в видео словаря"""

        r = requests.get(link_from_episode, headers=HEADERS)
        soup = BeautifulSoup(r.text, "lxml")

        # получение названия эпизода
        episodeNumber = soup.find("h1", class_="header_video allanimevideo the_hildi anime_padding_for_title_post").find("span").get_text().replace("Смотреть ", "")

        # получение прямой ссылки на видео с указанным качеством
        videoLink = soup.find("div", class_="videoContent").find("video").find("source", attrs={"res":str(quality)}).get("src")

        # получение название аниме
        animeName = sub(r'[^\w\s]+|[\d]+', r'',episodeNumber).strip().replace("серия", "").replace("сезон", "").strip()

        videoStream = requests.get(videoLink, headers=HEADERS, stream=True)

        # общий размер видео
        total = int(videoStream.headers.get('content-length', 0))

        # создание выходной папки
        try:
            makedirs("{}{}".format(OUT_DIR, animeName))
        except Exception:
            pass

        # запись в файл
        if not isfile("{}{}/{}.mp4".format(OUT_DIR, animeName, episodeNumber)):

            with open("{}{}/{}.mp4".format(OUT_DIR, animeName, episodeNumber), 'wb') as file, tqdm(desc=episodeNumber, total=total, unit='iB', unit_scale=True, unit_divisor=1024) as bar:
                for data in videoStream.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)

            print("Загрузка завершена!")
        else:
            print("Файл уже существует!")

    def cli(self):
        """функция реализует консольный интерфейс для скрипта"""

        episode_or_url = input("Выберите режим загрузки [1 - эпизод, 2 - аниме целиком]: ").lower().strip()
        
        match episode_or_url:
            case "1":
                forepisode_url = input("Ссылка на эпизод: ").strip()
                video_quality = input("Качество [360, 480, 720, 1080]: ").lower().strip()
                try:
                    print("Загрузка эпизода началась! [чтобы остановить загрузку нажмите Ctrl + C]")
                    self.get_and_download(forepisode_url, video_quality)
                except:
                    print("Неверно указана ссылка или качество, или аниме не доступно!")

            case "2":
                try:
                    forseason_url = input("Ссылка на аниме: ").strip()
                    video_quality = input("Качество [360, 480, 720, 1080]: ").lower().strip()
                except:
                    print("Неверно указана ссылка или качество!")
                
                all_season_or_inout_episode = input("Выберите режим загрузки [1 - все серии, 2 - интервалом]: ").lower().strip()
                
                match all_season_or_inout_episode:
                    case "1":
                        print("Загрузка аниме полностью.")

                        all_episodes = self.get_all_episodes(forseason_url)
                        print("Количество серий {}".format(len(all_episodes)))

                        print("Загрузка сезона началась! [чтобы остановить загрузку нажмите Ctrl + C]")

                        for episode in all_episodes:
                            self.get_and_download(episode, video_quality)

                        print("Загрузка сезона завершена!")
                    
                    case "2":
                        black_buttons_switch = input("Парсить серии помечанные серой кнопкой ? [1 - да; 0 - нет]: ")

                        if black_buttons_switch == "1":
                            all_episodes = self.get_all_episodes(forseason_url)
                        elif black_buttons_switch == "0":
                            all_episodes = self.get_all_episodes(forseason_url, parse_black_buttons=False)
                            print("Парсинг серий, помечанных серой кнопкой ОТКЛЮЧЕН!")
                        else:
                            print("Неверное значение флага! УСТАНОВЛЕНО ЗНАЧЕНИЕ ПО-УМОЛЧАНИЮ!")
                            all_episodes = self.get_all_episodes(forseason_url)

                        print("Загрузка интервалом.")

                        print("Количество серий {}".format(len(all_episodes)))

                        raw_interval = input("Введите с какой по какую серию загружать через запятую (например: 3,7): ").strip().split(",")
                        interval = [int(x) for x in raw_interval]

                        print("Интервал загрузки: с {} серии, по {} серию.".format(interval[0], interval[1]))

                        print("Загрузка интервала началась! [чтобы остановить загрузку нажмите Ctrl + C]")

                        for episode in all_episodes[int(interval[0])-1:int(interval[1])]:
                            self.get_and_download(episode, video_quality)

                        print("Загрузка интервала завершена!")
                    case _:
                        print("Неверный выбор!")
            case _:
                print("Неверный выбор!")


if __name__ == "__main__":
    jp = jutsuParser()
    jp.cli()