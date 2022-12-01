import json

from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
	env = Environment(
	    loader=FileSystemLoader('.'),
	    autoescape=select_autoescape(['html', 'xml'])
	)
	template = env.get_template('template.html')
	with open("books_descriptions.json", "r") as file:
		books_descriptions = json.load(file)
	for description in books_descriptions:
		description["book_path"] = description["book_path"].replace("\\", "/")
		description["img_src"] = description["img_src"].replace("\\", "/")
	rendered_page = template.render(
	    books_descriptions = books_descriptions,
	)
	with open('index.html', 'w', encoding="utf8") as file:
	    file.write(rendered_page)
	server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
	server.serve_forever()


if __name__ == "__main__":
    main()
