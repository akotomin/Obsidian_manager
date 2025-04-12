import sys
import os

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import shutil
import yaml
from const import FOLDER_BY_TAG
from config import VAULT_PATH

def move_notes_by_tag(path, list_of_tags):
    """
    Перемещает задачи в общем хранилище obsidian и распределяет их по папкам в зависимости от тегов, записанных в файле
    :param path: Путь к хранилищу(obsidian vault)
    :param list_of_tags: Словарь с тегами для обработки файлов в хранилище
    """
    # Перебираем все файлы в хранилище
    for file_name in os.listdir(path):
        if file_name.endswith(".md"):
            file_path = os.path.join(path, file_name)

            with open(file_path, 'r', encoding="utf-8") as file:
                content = file.read()

                # Проверяем, есть ли заголовок YAML
                if content.startswith('---'):
                    # Найти конец заголовка YAML(поиск второго появления --- в файле, начиная с позиции 3)
                    end_of_yaml = content.find('---', 3)
                    if end_of_yaml != -1:
                        # Извлекаем содержимое заголовка
                        yaml_content = content[3:end_of_yaml].strip()
                        try:
                            # Парсим YAML
                            metadata = yaml.safe_load(yaml_content)
                            tags = metadata.get('tags', [])

                            # Перемещение файла в соответствующую папку по тегам
                            for tag in tags:
                                folder_name = list_of_tags.get(tag)
                                if folder_name:
                                    destination_folder = os.path.join(path, folder_name)
                                    if not os.path.exists(destination_folder):
                                        os.makedirs(destination_folder)  # Создаем папку, если её нет

                                    # Перемещаем файл
                                    shutil.move(file_path, os.path.join(destination_folder, file_name))
                                    print(f"Перемещен файл '{file_name}' в папку '{folder_name}' по тегу '{tag}'")
                                    break  # Прекращаем поиск, если заметка уже перемещена
                        except yaml.YAMLError as e:
                            print(f"Ошибка парсинга YAML в файле {file_name}: {e}")


if __name__ == "__main__":
    move_notes_by_tag(VAULT_PATH, FOLDER_BY_TAG)
