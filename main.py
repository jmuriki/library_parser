import requests

from pathlib import Path


def create_folder_safely(folder_name="library"):
    Path(f"./{folder_name}").mkdir(parents=True, exist_ok=True)
    return folder_name


def save_text(response, filename):
    with open(Path(f"./{filename}"), "w") as file:
        file.write(response.text)


def check_for_redirect(response):
    if response.history != []:
        raise HTTPError


def main():
    library_path = create_folder_safely()
    for id in range(1, 11):
        url = f"https://tululu.org/txt.php?id={id}"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            save_text(response, Path(f"{library_path}/id_{id}.txt"))
        except:
            continue


if __name__ == "__main__":
    main()
