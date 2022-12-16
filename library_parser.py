import os
import time
import requests
import argparse

from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename as sanitize_name


def create_parser():
    parser = argparse.ArgumentParser(
        description="""Опциональные аргументы.
        По умолчанию 1 и 10 соответственно."""
    )
    parser.add_argument("-s", "--start_id", default=1, type=int)
    parser.add_argument("-e", "--end_id", default=10, type=int)
    return parser


def check_for_redirect(response):
    response_history = response.history
    if response_history:
        raise requests.exceptions.HTTPError(response_history)


def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, "lxml")


def split_title_tag(soup):
    title_tag = soup.select_one("table.tabs h1")
    raw_title, raw_author = title_tag.text.split("::")
    title = raw_title.strip()
    author = raw_author.strip()
    return title, author


def get_genres(soup):
    genres_tags = soup.select("span.d_book a")
    genres = [tag.text for tag in genres_tags]
    return genres


def get_comments_texts(soup):
    comments = soup.select("div.texts span.black")
    texts = [comment.text for comment in comments]
    return texts


def parse_book_page(soup):
    parsed_page = {}
    parsed_page['title'], parsed_page['author'] = split_title_tag(soup)
    parsed_page['genres'] = get_genres(soup)
    parsed_page['comments'] = get_comments_texts(soup)
    parsed_page['pic_rel_path'] = soup.select_one(
        "body div.bookimage img")["src"]
    parsed_page['pic_name'] = os.path.split(parsed_page['pic_rel_path'])[-1]
    return parsed_page


def compile_comments_guide(parsed_page):
    guide = []
    guide.append(parsed_page['title'])
    guide.append(parsed_page['author'])
    if parsed_page['comments']:
        guide.append(parsed_page['comments'])
    guide.append("\n")
    return "\n".join(guide)


def download_txt(txt_url, params, txt_name, dest_folder=".", folder="books"):
    response = requests.get(txt_url, params)
    response.raise_for_status()
    check_for_redirect(response)
    Path(f"{dest_folder}/{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"{dest_folder}/{folder}/{txt_name}")
    with open(path, "w") as file:
        file.write(response.text)
    return str(path)


def download_image(pic_url, pic_name, dest_folder=".", folder="images"):
    response = requests.get(pic_url)
    response.raise_for_status()
    check_for_redirect(response)
    Path(f"{dest_folder}/{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"{dest_folder}/{folder}/{pic_name}")
    with open(path, "wb") as file:
        file.write(response.content)
    return str(path)


def save_comments(
            comments_guide,
            filename="Гид по отзывам.txt",
            folder="books/"
        ):
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{filename}")
    with open(path, "w") as file:
        file.write("\n".join(comments_guide))


def main():
    url = "https://tululu.org/"
    arguments = create_parser().parse_args()
    start_id = arguments.start_id
    end_id = arguments.end_id
    comments_guide = []
    for book_id in tqdm(range(start_id, end_id + 1)):
        txt_url = f"{url}txt.php"
        params = {
            "id": book_id
        }
        book_url = f"{url}b{book_id}/"
        try:
            soup = get_soup(book_url)
            parsed_page = parse_book_page(soup)
            txt_name = sanitize_name(f"{book_id}. {parsed_page['title']}.txt")
            download_txt(txt_url, params, txt_name)
            pic_url = urljoin(book_url, parsed_page['pic_rel_path'])
            pic_name = parsed_page['pic_name']
            download_image(pic_url, pic_name)
            comments_guide.append(compile_comments_guide(parsed_page))
        except requests.exceptions.HTTPError:
            print(requests.exceptions.HTTPError)
            continue
        except requests.exceptions.ConnectionError:
            print(requests.exceptions.ConnectionError)
            time.sleep(1)
            continue
    save_comments(comments_guide)


if __name__ == "__main__":
    main()
