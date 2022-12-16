import json

from pathlib import Path
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_descs():
    with open("books_descriptions.json", "r") as file:
        descs = json.load(file)
    for desc in descs:
        desc["book_path"] = desc["book_path"].replace("\\", "/")
        desc["img_src"] = desc["img_src"].replace("\\", "/")
    return descs


def arrange_descs(descs):
    descs_per_line = 2
    lines_per_page = 10
    lined_descs = [chunk for chunk in chunked(descs, descs_per_line)]
    paged_descs = [chunk for chunk in chunked(lined_descs, lines_per_page)]
    return paged_descs


def on_reload():
    descs = get_descs()
    pages_folder_name = "pages"
    Path(f"./{pages_folder_name}").mkdir(parents=True, exist_ok=True)
    paged_descs = arrange_descs(descs)
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")
    pages_nums = [num for num, _ in enumerate(paged_descs, 1)]
    for number, page in enumerate(paged_descs, 1):
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
