import requests

from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(url):
    response = requests.get(url)
    response.raise_for_status()
    if response.history != []:
        raise HTTPError


def get_title(id):
    url = f"https://tululu.org/b{id}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    title_tag = soup.find("body").find("table", class_="tabs").find("h1")
    title = title_tag.text.split("::")[0].strip()
    return title


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    with open(Path(f"./{folder}{filename}"), "w") as file:
        file.write(response.text)
    return path


def main():
    for id in range(1, 11):
        url = f"https://tululu.org/txt.php?id={id}"
        try:
            check_for_redirect(url)
            title = get_title(id)
            filename = sanitize_filename(f"{id}. {title}.txt")
            download_txt(url, filename)
        except:
            continue


if __name__ == "__main__":
    main()
