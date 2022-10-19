import os
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename


def check_for_redirect(url):
    response = requests.get(url)
    response.raise_for_status()
    if response.history != []:
        raise HTTPError


def get_soup(url, id):
    url = f"{url}b{id}"
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_title(soup):
    title_tag = soup.find("body").find("table", class_="tabs").find("h1")
    return title_tag.text.split("::")[0].strip()


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{filename}")
    with open(path, "w") as file:
        file.write(response.text)
    return path


def download_image(url, filename, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{filename}")
    with open(path, "wb") as file:
        file.write(response.content)
    return path


def main():
    url = "https://tululu.org/"
    for id in range(1, 11):
        txt_url = f"{url}txt.php?id={id}"
        try:
            check_for_redirect(txt_url)
            soup = get_soup(url, id)
            title = get_title(soup)
            filename = sanitize_filename(f"{id}. {title}.txt")
            download_txt(url, filename)
            rel_link = soup.find("body").find("div", class_="bookimage").find("img")["src"]
            pic_url = urljoin(url, rel_link)            
            pic_name = os.path.split(rel_link)[-1]
            download_image(pic_url, pic_name)
        except:
            continue


if __name__ == "__main__":
    main()
