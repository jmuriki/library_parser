import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_soup(genre_page_url):
    response = requests.get(genre_page_url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def get_books_rel_paths(soup):
    tables = soup.find_all("table", class_="d_book")
    paths = [t.find("a")["href"] for t in tables]
    return paths


def main():
    url = "https://tululu.org/"
    genre = 55
    page = 1
    genre_page_url = f"{url}l{genre}/{page}/"
    soup = get_soup(genre_page_url)
    books_rel_paths = get_books_rel_paths(soup)
    books_urls = [urljoin(url, path) for path in books_rel_paths]
    print(books_urls)


if __name__ == "__main__":
    main()
