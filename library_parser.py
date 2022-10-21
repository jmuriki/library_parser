import os
import time
import requests
import argparse

from tqdm import tqdm
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


def get_soup(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return BeautifulSoup(response.text, "lxml")


def split_title_tag(soup):
    title_tag = soup.find("body").find("table", class_="tabs").find("h1")
    raw_title, raw_author = title_tag.text.split("::")
    title = raw_title.strip()
    author = raw_author.strip()
    return title, author


def get_genres(soup):
    genres_tags = soup.find_all("span", class_="d_book")
    genres = [t.find("a").text for t in genres_tags]
    return "\n".join(genres)


def get_comments_texts(soup):
    comments = soup.find_all("div", class_="texts")
    texts = [c.find("span", class_="black").text for c in comments]
    return "\n".join(texts)


def parse_book_page(soup):
    parsed_page = {}
    parsed_page['title'], parsed_page['author'] = split_title_tag(soup)
    parsed_page['genres'] = get_genres(soup)
    parsed_page['comments'] = get_comments_texts(soup)
    parsed_page['pic_rel_path'] = soup.find("body").find("div", class_="bookimage").find("img")["src"]
    parsed_page['pic_name'] = os.path.split(parsed_page['pic_rel_path'])[-1]
    return parsed_page


def compile_commets_guide(parsed_page):
    guide = []
    guide.append(parsed_page['title'])
    guide.append(parsed_page['author'])
    if parsed_page['comments']:
        guide.append(parsed_page['comments'])
    guide.append("\n")
    return "\n".join(guide)


def download_txt(url, params, filename, folder="books/"):
    response = requests.get(url, params)
    response.raise_for_status()
    check_for_redirect(response)
    Path(f"./{folder}").mkdir(parents=True, exist_ok=True)
    path = Path(f"./{folder}{filename}")
    with open(path, "w") as file:
        file.write(response.text)
    return path


def download_image(url, filename, folder="images/"):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
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
    for book_id in tqdm(range(start_id, end_id + 1)):
        txt_url = f"{url}txt.php"
        params = {
        "id": book_id
        }
        book_url = f"{url}b{book_id}/"
        try:
            soup = get_soup(book_url)
            parsed_page = parse_book_page(soup)
            filename = sanitize_filename(f"{book_id}. {parsed_page['title']}.txt")
            download_txt(txt_url, params, filename)
            pic_url = urljoin(book_url, parsed_page['pic_rel_path'])
            pic_name = parsed_page['pic_name']
            download_image(pic_url, pic_name)
            comments_guide.append(compile_commets_guide(parsed_page))
        except requests.exceptions.HTTPError as error:
            print(error)
            continue
        except requests.exceptions.ConnectionError as error:
            print(error)
            time.sleep(1)
            continue
        except Exception as error:
            print(error)
            continue
    save_comments(comments_guide)


if __name__ == "__main__":
    main()
