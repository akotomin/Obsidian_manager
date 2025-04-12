import os
import shutil
from ..md_file_parser import MarkdownWorker
from const import FOLDER_BY_TAG
from config import VAULT_PATH


def move_notes_by_tag(path, file_path, file_name, tags):
    """
    Перемещает задачи в общем хранилище obsidian и распределяет их по папкам в зависимости от тегов, записанных в файле
    :param path: Путь к хранилищу(obsidian vault)
    :param file_path: Путь к конкретному файлу
    :param file_name: Название файла md
    :param tags: Словарь с тегами внутри рассматриваемой заметки
    """
    for tag in tags:
        folder_name = FOLDER_BY_TAG.get(tag)
        if folder_name:
            destination_folder = os.path.join(path, folder_name)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)  # Создаем папку, если её нет

            # Перемещаем файл
            shutil.move(file_path, os.path.join(destination_folder, file_name))
            print(f"Перемещен файл '{file_name}' в папку '{folder_name}' по тегу '{tag}'")
            break  # Прекращаем поиск, если заметка уже перемещена

def file_enumeration(path):
    """
    Перебирает все файлы в папке, и применяет функцию move_notes_by_tag для перемещения файлов
    :param path: Путь к хранилищу(obsidian vault)
    """
    for file_name in os.listdir(path):
        if file_name.endswith(".md"):
            file_path = os.path.join(path, file_name)

            with open(file_path, 'r', encoding="utf-8") as file:
                content = file.readlines()

                md_file = MarkdownWorker(content)
                tags = md_file.yaml_header.get('tags', [])
                move_notes_by_tag(path, file_path, file_name, tags)

if __name__ == "__main__":
    file_enumeration(VAULT_PATH)
