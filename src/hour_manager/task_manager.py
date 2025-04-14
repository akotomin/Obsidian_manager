import os
import shutil
from src.md_file_parser import MarkdownWorker


class TaskManager:
    @staticmethod
    def task_mover(path, file_name):
        """
        Перемещает файл из переданной директории в директорию с выполненными задачами
        :param path: Путь, где лежит файл, кторый необходимо переместить
        :param file_name: название файла, который необходимо переместить
        """
        destination_folder = os.path.join(path, 'Выполнено')
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)  # Создаем папку, если её нет

        # Перемещаем файл
        shutil.move(os.path.join(path, file_name), os.path.join(destination_folder, file_name))
        print(f"Файл '{file_name}' перемещен в папку Выполнено")

    def content_worker(self, md_file, tasks_path, file, file_name):
        tags = md_file.yaml_header.get('tags', [])
        tasks_dict = dict()

        if 'выполнено' in tags:
            self.task_mover(tasks_path, file_name)
            return tasks_dict

        else:
            # Проверка задач
            all_tasks_done = md_file.unchecked_task_searcher()

            # Если все задачи выполнены, обновляем YAML-заголовок
            if all_tasks_done:
                # Функция обновления YAML заголовка
                new_content = md_file.overwrite_yaml_header()
                # Перезаписываем файл
                file.seek(0)  # Устанавливаем указатель в начало файла
                file.writelines(new_content)  # Записываем новый контент
                file.truncate()  # Убираем остатки старого содержимого, если новый контент короче

                # Перемещаем файл в папку Выполнено
                self.task_mover(tasks_path, file_name)

            # Если есть невыполненные задачи, добавляем содержание файла в словарь для описания в гугл задачу
            else:
                # В случае если задача не была перемещена в выполнено, добавляем ее в список задач
                tasks_dict[md_file.file_name] = [md_file.yaml_header, md_file.parse_task_content()]
                return tasks_dict
            return tasks_dict

    def task_manager(self, tasks_path):
        """
        Находит все задачи в переданной директории, обрабатывает их в зависимости от содержимого внутри задачи.
        1. Если у задачи есть тег #выполнено, то задача с помощью task_mover перемещается в директорию выполненых задач
        2. Если все подзадачи внутри фала выполнены, то задаче присваивается статус #выполнено, а затем она перемещается
        в директорию выполненых задач
        3. Если задача не выполнена, её содержимое разбирается и вместе с исходной задачей добавляется в словарь.
        После выполнения метода этот словарь возвращается.
        :param tasks_path: Директория, в которой необходимо искать файлы
        :return: Словарь вида `{task_name: {yaml_header, description}}` для невыполненных задач.
        :rtype: dict[str, dict[dict, ]]
        """

        for file_name in os.listdir(tasks_path):
            # Рассматриваем только markdown файлы
            if file_name.endswith('.md'):
                file_path = os.path.join(tasks_path, file_name)

                with open(file_path, 'r+', encoding="utf-8") as file:
                    content = file.readlines()

                    md_file = MarkdownWorker(content, file_name)
                    return self.content_worker(md_file, tasks_path, file, file_name)

        return {}


class TasksUnchecker:
    """
    Обновляет ежедневные задачи, если они были закрыты
    """
    @staticmethod
    def uncheck_tasks(path, date_format):
        # Хранение изменённых строк для отчёта
        replaced_lines = []
        date_was_updated = False

        # Открываем файл в режиме чтения и записи
        with open(path, 'r+', encoding="utf-8") as file:
            content = file.readlines()
            md_file = MarkdownWorker(content)
            # Получаем обновленное содержимое файла
            new_content = md_file.regular_file_changer()

            # Перемещаем указатель в начало файла и записываем новый контент
            file.seek(0)
            file.writelines(new_content)

            # Обрезаем файл до новой длины (на случай, если новый контент короче старого)
            file.truncate()
