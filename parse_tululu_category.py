import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_soup(genre_page_url):
    response = requests.get(genre_page_url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_book_rel_path(soup):
    table = soup.find("table", class_="d_book")
    path = table.find("a")["href"]
    return path


def main():
    url = "https://tululu.org/"
    genre = 55
    page = 1
    genre_page_url = f"{url}l{genre}/{page}/"
    soup = get_soup(genre_page_url)
    book_rel_path = get_book_rel_path(soup)
    book_url = urljoin(url, book_rel_path)
    print(book_url)


if __name__ == "__main__":
    main()
