import requests

from pathlib import Path


def create_folder_safely(folder_name="library"):
    Path(f"./{folder_name}").mkdir(parents=True, exist_ok=True)
    return folder_name


def save_text(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(Path(f"./{filename}"), "w") as file:
        file.write(response.text)


def main():
    library_path = create_folder_safely()
    for id in range(1, 11):
        url = f"https://tululu.org/txt.php?id={id}"
        save_text(url, Path(f"{library_path}/id_{id}.txt"))


if __name__ == "__main__":
    main()
