import os
import requests
import argparse

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename


def create_parser(arg_1, arg_2):
    parser = argparse.ArgumentParser(description="Опциональные аргументы. По умолчанию 1 и 10 соответственно.")
    parser.add_argument("-s", arg_1, default=1, type=int)
    parser.add_argument("-e", arg_2, default=10, type=int)
    return parser


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_soup(url, book_id):
    url = f"{url}b{book_id}"
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def split_title_tag(soup):
    title_tag = soup.find("body").find("table", class_="tabs").find("h1")
    raw_title, raw_author = title_tag.text.split("::")
    title = raw_title.strip()
    author = raw_author.strip()
    return title, author


def get_genres(soup):
    genres = []
    genres_tag = soup.find_all("span", class_="d_book")
    for tag in genres_tag:
        genre = tag.find("a").text
        genres.append(genre)
    return "\n".join(genres)


def get_comments_texts(soup):
    texts = []
    comments = soup.find_all("div", class_="texts")
    for comment in comments:
        text = comment.find("span", class_="black").text
        texts.append(text)
    return "\n".join(texts)


def parse_book_page(soup):
    book_parsed = {}
    book_parsed["Заголовок"], book_parsed["Автор"] = split_title_tag(soup)
    print(book_parsed)
    book_parsed["Жанр"] = get_genres(soup)
    book_parsed["Отзывы"] = get_comments_texts(soup)
    book_parsed["Обложка"] = soup.find("body").find("div", class_="bookimage").find("img")["src"]
    return book_parsed


def compile_commets_guide(book_parsed):
    guide = []
    guide.append(book_parsed["Заголовок"])
    guide.append(book_parsed["Автор"])
    if book_parsed["Отзывы"]:
        guide.append(book_parsed["Отзывы"])
    guide.append("\n")
    return "\n".join(guide)


def download_txt(url, filename, folder="books/"):
    response = requests.get(url)
    response.raise_for_status()
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{filename}")
    with open(path, "w") as file:
        file.write(response.text)
    return path


def download_image(url, filename, folder="images/"):
    response = requests.get(url)
    response.raise_for_status()
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{filename}")
    with open(path, "wb") as file:
        file.write(response.content)
    return path


def save_comments(comments_guide, filename="Гид по отзывам.txt", folder="books/"):
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{filename}")
    with open(path, "w") as file:
        file.write("\n".join(comments_guide))


def main():
    url = "https://tululu.org/"
    arguments = create_parser("--start_id", "--end_id").parse_args()
    start_id = arguments.start_id
    end_id = arguments.end_id
    comments_guide = []
    for book_id in range(start_id, end_id + 1):
        txt_url = f"{url}txt.php"
        params = {
        "id": book_id
        }
        try:
            response = requests.get(url, params)
            response.raise_for_status()
            check_for_redirect(response)
            soup = get_soup(url, book_id)
            book_parsed = parse_book_page(soup)
            filename = sanitize_filename(f"{book_id}. {book_parsed['Заголовок']}.txt")
            download_txt(url, filename)
            pic_url = urljoin(url, book_parsed["Обложка"])
            pic_name = os.path.split(book_parsed["Обложка"])[-1]
            download_image(pic_url, pic_name)
            comments_guide.append(compile_commets_guide(book_parsed))
        except:
            continue
    save_comments(comments_guide)


if __name__ == "__main__":
    main()
