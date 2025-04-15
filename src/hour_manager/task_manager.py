import os
import shutil
from src.md_file_parser import MarkdownWorker


class TaskManager:
    @staticmethod
    def move_completed_tasks(path, file_name):
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

    def verify_all_tasks_done(self, md_file, tasks_path, file, file_name):
        tags = md_file.yaml_header.get('tags', [])

        if 'выполнено' in tags:
            self.move_completed_tasks(tasks_path, file_name)

        else:
            # Проверка задач
            all_tasks_done = md_file.unchecked_task_searcher()

            # Если все задачи выполнены, обновляем YAML-заголовок и файл
            if all_tasks_done:
                # Перезаписываем файл
                file.seek(0)  # Устанавливаем указатель в начало файла
                file.writelines(md_file.overwrite_yaml_header())  # Записываем новый контент
                file.truncate()  # Убираем остатки старого содержимого, если новый контент короче

                # Перемещаем файл в папку Выполнено
                self.move_completed_tasks(tasks_path, file_name)


            # Если есть невыполненные задачи, возвращаем саму задачу
            else:
                return md_file

        return None

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
        tasks_dict = dict()

        for file_name in os.listdir(tasks_path):
            # Рассматриваем только markdown файлы
            if file_name.endswith('.md'):
                file_path = os.path.join(tasks_path, file_name)

                with open(file_path, 'r+', encoding="utf-8") as file:
                    content = file.readlines()

                    md_file = MarkdownWorker(content, file_name)
                    checked_md_file = self.verify_all_tasks_done(md_file, tasks_path, file, file_name)
                    if checked_md_file is None:
                        continue
                    tasks_dict[md_file.file_name] = [md_file.yaml_header, md_file.parse_task_content()]

        return tasks_dict


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
