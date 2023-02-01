import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import makedirs
from os.path import isfile
from re import sub

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

out_dir = "./out/"

def get_all_episodes(url:str):
    # получаю ссылки на все эпизоды в сезоне
    episodesUrls = []

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    episodes = soup.find_all("a", class_="short-btn green video the_hildi", attrs="href")

    for episode in episodes:
        episodesUrls.append("https://jut.su{}".format(episode["href"]))

    return episodesUrls

def download_episode(episodeUrl:str, quality:str):
    # получаю название эпизода и ссылку на него в нужном качестве, скачиваю

    r = requests.get(episodeUrl, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # получение названия эпизода и самого видео
    episodeName = soup.find("h1", class_="header_video allanimevideo the_hildi anime_padding_for_title_post").find("span").get_text().replace("Смотреть ", "")
    episodeVideo = soup.find("div", class_="videoContent").find("video").find("source", attrs={"res":str(quality)}).get("src")

    # получение названия аниме
    animeName = sub(r'[^\w\s]+|[\d]+', r'',episodeName).strip().replace("серия", "").replace("сезон", "").strip()

    # загрузка эпизода
    resp = requests.get(episodeVideo, headers=headers, stream=True)
    total = int(resp.headers.get('content-length', 0))

    try:
        makedirs("{}{}".format(out_dir, animeName))
    except Exception:
        pass
    
    if not isfile("{}{}/{}.mp4".format(out_dir, animeName, episodeName)):

        with open("{}{}/{}.mp4".format(out_dir, animeName, episodeName), 'wb') as file, tqdm(desc=episodeName, total=total, unit='iB', unit_scale=True, unit_divisor=1024) as bar:
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)

        print("Загрузка эпизода завершена!")
    else:
        print("Файл уже существует!")

def cli():
    episode_or_url = input("Скачать эпизод или сезон/аниме целиком ? [1 - эпизод, 2 - сезон/аниме целиком]: ").lower().strip()
    
    match episode_or_url:
        case "1":
            forepisode_url = input("Ссылка на эпизод: ").strip()
            try:
                video_quality = input("Качество [360, 480, 720, 1080]: ").lower().strip()
                print("Загрузка эпизода началась! [чтобы остановить загрузку нажмите Ctrl + C]")
                download_episode(forepisode_url, video_quality)
            except:
                print("Неверно указана ссылка или качество!")

        case "2":
            try:
                forseason_url = input("Ссылка на сезон/аниме целиком: ").strip()
                video_quality = input("Качество [360, 480, 720, 1080]: ").lower().strip()
            except:
                print("Неверно указана ссылка или качество!")
            
            all_season_or_inout_episode = input("Скачать весь сезон или интервалом? [1 - весь сезон, 2 - интервалом]: ").lower().strip()
            

            match all_season_or_inout_episode:
                case "1":
                    print("Загрузка сезона полностью.")

                    all_episodes = get_all_episodes(forseason_url)
                    print("Количество серий {}".format(len(all_episodes)))

                    print("Загрузка сезона началась! [чтобы остановить загрузку нажмите Ctrl + C]")

                    for episode in all_episodes[int(in_episode)-1:int(out_episode)]:
                        download_episode(episode, video_quality)

                    print("Загрузка сезона завершена!")
                
                case "2":
                    print("Загрузка интервалом.")

                    all_episodes = get_all_episodes(forseason_url)
                    print("Количество серий {}".format(len(all_episodes)))

                    in_episode = input("С какой серии начать загрузку: ").lower().strip()
                    out_episode = input("По какую серию загрузить: ").lower().strip() 

                    if in_episode.isdigit() and out_episode.isdigit():
                        print("Интервал загрузки: с {} серии, по {} серию.".format(in_episode, out_episode))

                        print("Загрузка интервала началась! [чтобы остановить загрузку нажмите Ctrl + C]")

                        for episode in all_episodes[int(in_episode)-1:int(out_episode)]:
                            download_episode(episode, video_quality)

                        print("Загрузка интервала завершена!")
                    else:
                        print("Нужно число, а не символ!")
                case _:
                    print("Неверный выбор!")
        case _:
            print("Неверный выбор!")

def main():
    cli()

if __name__ == "__main__":
    main()