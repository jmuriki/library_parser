import json

from pathlib import Path
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
	pages_folder = "pages"
	Path(f"./{pages_folder}").mkdir(parents=True, exist_ok=True)
	with open("books_descriptions.json", "r") as file:
		books_descriptions = json.load(file)
	for description in books_descriptions:
		description["book_path"] = description["book_path"].replace("\\", "/")
		description["img_src"] = description["img_src"].replace("\\", "/")
	paged_descriptions = [chunk for chunk in chunked(books_descriptions, 20)]
	packed_descriptions = [[chunk for chunk in chunked(page, 2)] for page in paged_descriptions]
	env = Environment(
	    loader=FileSystemLoader("."),
	    autoescape=select_autoescape(["html", "xml"])
	)
	template = env.get_template("template.html")
	for number, page in enumerate(packed_descriptions):
		rendered_page = template.render(
		    books_descriptions = page,
		)
		with open(f"./{pages_folder}/index{number + 1}.html", "w", encoding="utf8") as file:
		    file.write(rendered_page)


def main():
	on_reload()
	server = Server()
	server.watch("template.html", on_reload)
	server.serve(root=".")


if __name__ == "__main__":
    main()
 