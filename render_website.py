import json

from pathlib import Path
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_descriptions():
    with open("books_descriptions.json", "r") as file:
        descriptions = json.load(file)
    for description in descriptions:
        description["book_path"] = description["book_path"].replace("\\", "/")
        description["img_src"] = description["img_src"].replace("\\", "/")
    return descriptions


def arrange_descriptions(descriptions):
    descriptions_per_line = 2
    lines_per_page = 10
    lined_descriptions = [chunk for chunk in chunked(
            descriptions, descriptions_per_line
        )]
    paged_descriptions = [chunk for chunk in chunked(
            lined_descriptions, lines_per_page
        )]
    return paged_descriptions


def on_reload():
    descriptions = get_descriptions()
    pages_folder_name = "pages"
    Path(f"./{pages_folder_name}").mkdir(parents=True, exist_ok=True)
    paged_descriptions = arrange_descriptions(descriptions)
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")
    pages_nums = [num for num, _ in enumerate(paged_descriptions, 1)]
    for number, page in enumerate(paged_descriptions, 1):
        rendered_page = template.render(
            pages_nums=pages_nums,
            number=number,
            page=page,
        )
        if number == 1:
            with open("./index.html", "w", encoding="utf8") as file:
                file.write(rendered_page.replace("./", "/"))
        with open(
                f"./{pages_folder_name}/index{number}.html",
                "w",
                encoding="utf8",
        ) as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch("template.html", on_reload)
    server.serve(root=".")


if __name__ == "__main__":
    main()
