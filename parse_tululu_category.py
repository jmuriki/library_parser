import os
import json
import time
import requests
import argparse

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathvalidate import sanitize_filename

from library_parser import check_for_redirect
from library_parser import get_soup
from library_parser import split_title_tag
from library_parser import parse_book_page
from library_parser import download_txt
from library_parser import download_image
from library_parser import get_genres
from library_parser import get_comments_texts


def create_parser():
    parser = argparse.ArgumentParser(
        description="""Все представленные аргументы являются опциональными.
        По умолчанию будут скачаны все книги и картинки со всех доступных страниц
        в заранее определённые папки в корневом каталоге проекта."""
    )
    parser.add_argument(
        "-g",
        "--genre",
        default=55,
        type=int,
        help="""Введите номер жанра.
        По умолчанию будет указан номер 55, что соответствует жанру
        "Научная фантастика"."""
    )
    parser.add_argument(
        "-s",
        "--start_page",
        default=1,
        type=int,
        help="""Введите номер начальной страницы.
                Если не вводить номер конечной страницы,
                будут скачаны все доступные страницы
                с начальной включительно."""
    )
    parser.add_argument(
        "-e",
        "--end_page",
        default=1000000,
        type=int,
        help="""Введите номер конечной страницы.
                Если не вводить номер начальной страницы,
                будут скачаны все доступные страницы с первой по конечную
                (без включения конечной)."""
    )
    parser.add_argument(
        "-f",
        "--dest_folder",
        default=".",
        help="""Введите путь к каталогу с результатами парсинга:
                картинкам, книгам, JSON."""
    )
    parser.add_argument(
        "-i",
        "--skip_imgs",
        action="store_true",
        help="""По умолчанию картинки будут скачаны.
                Для отмены укажите при запуске аргумент без значения."""
    )
    parser.add_argument(
        "-t",
        "--skip_txt",
        action="store_true",
        help="""По умолчанию тексты книг будут скачаны.
                Для отмены укажите при запуске аргумент без значения."""
    )
    parser.add_argument(
        "-j",
        "--json_path",
        default=None,
        help="Введите путь к *.json файлу с результатами."
    )
    return parser


def get_books_rel_paths(url, genre, start_page, end_page):
    paths = []
    for page in range(start_page, end_page):
        genre_url = f"{url}l{genre}/{page}/"
        try:
            soup = get_soup(genre_url)
        except requests.exceptions.HTTPError:
            break
        tables = soup.select("table.d_book")
        paths.extend([table.select_one("a")["href"] for table in tables])
    return paths


def save_as_json(books_info, dest_folder, json_path, filename="books_info"):
    folder = json_path if json_path else dest_folder
    Path(folder).mkdir(parents=True, exist_ok=True)
    path = Path(f"{folder}/{filename}.json")
    with open(path, "w", encoding="utf8") as file:
        json.dump(books_info, file, ensure_ascii=False)


def main():
    arguments = create_parser().parse_args()
    genre = arguments.genre
    start_page = arguments.start_page
    end_page = arguments.end_page
    dest_folder = arguments.dest_folder
    skip_imgs = arguments.skip_imgs
    skip_txt = arguments.skip_txt
    json_path = arguments.json_path
    url = "https://tululu.org/"
    books_rel_paths = get_books_rel_paths(
        url,
        genre,
        start_page,
        end_page,
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
            if not skip_txt:
                txt_name = sanitize_filename(f"{parsed_page['title']}.txt")
                book_path = download_txt(txt_url, params, txt_name, dest_folder)
                parsed_page["book_path"] = book_path
            if not skip_imgs:
                pic_url = urljoin(book_url, parsed_page['pic_rel_path'])
                pic_name = parsed_page['pic_name']
                pic_path = download_image(pic_url, pic_name, dest_folder)
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
    save_as_json(books_info, dest_folder, json_path)


if __name__ == "__main__":
    main()
