import os
import json
import time
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename


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
    parsed_page['pic_rel_path'] = soup.select_one("body div.bookimage img")["src"]
    parsed_page['pic_name'] = os.path.split(parsed_page['pic_rel_path'])[-1]
    return parsed_page


def get_books_rel_paths(url, genre, total_pages):
    paths = []
    for page in range(1, total_pages + 1):
        genre_url = f"{url}l{genre}/{page}/"
        soup = get_soup(genre_url)
        tables = soup.select("table.d_book")
        paths.extend([table.select_one("a")["href"] for table in tables])
    return paths


def download_txt(txt_url, params, txt_name, folder="books/"):
    response = requests.get(txt_url, params)
    response.raise_for_status()
    check_for_redirect(response)
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{txt_name}")
    with open(path, "w") as file:
        file.write(response.text)
    return str(path)


def download_image(pic_url, pic_name, folder="images/"):
    response = requests.get(pic_url)
    response.raise_for_status()
    check_for_redirect(response)
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{pic_name}")
    with open(path, "wb") as file:
        file.write(response.content)
    return str(path)


def save_as_json(books_info):
    with open(Path("./books_info.json"), "w", encoding="utf8") as file:
        json.dump(books_info, file, ensure_ascii=False)


def main():
    url = "https://tululu.org/"
    genre = 55
    total_pages = 4
    books_rel_paths = get_books_rel_paths(
        url,
        genre,
        total_pages,
    )
    books_info = []
    for path in books_rel_paths:
        book_url = urljoin(url, path)
        txt_url = f"{url}txt.php"
        book_id = path.strip("/b")
        params = {
        "id": book_id
        }
        try:
            soup = get_soup(book_url)
            parsed_page = parse_book_page(soup)
            txt_name = sanitize_filename(f"{parsed_page['title']}.txt")
            book_path = download_txt(txt_url, params, txt_name)
            pic_url = urljoin(book_url, parsed_page['pic_rel_path'])
            pic_name = parsed_page['pic_name']
            pic_path = download_image(pic_url, pic_name)
            parsed_page["book_path"] = book_path
            parsed_page["img_src"] = pic_path
            parsed_page.pop("pic_rel_path")
            parsed_page.pop("pic_name")
            books_info.append(parsed_page)
        except requests.exceptions.HTTPError as error:
            print(error)
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            continue
        except Exception as error:
            print(error)
            continue
    save_as_json(books_info)


if __name__ == "__main__":
    main()
