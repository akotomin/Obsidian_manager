import os
import shutil
from ..md_file_parser import MarkdownWorker


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

            # # Перемещаем указатель в начало файла
            # file.seek(0)
            #
            # in_yaml = False
            #
            # for line in lines:
            #     if line.strip() == "---":  # Начало или конец YAML-заголовка
            #         in_yaml = not in_yaml
            #
            #     # Если внутри YAML-заголовка
            #     elif in_yaml and line.startswith("date:"):
            #         # Перезаписываем дату
            #         file.write(f"date: {datetime.now().strftime(date_format)}\n")
            #         date_was_updated = True
            #         continue
            #
            #     # Заменяем символы в строках и записываем обратно
            #     if "- [x]" in line:
            #         replaced_lines.append(
            #             (
            #                 line.strip(),
            #                 line.replace("- [x]", "- [ ]").strip()
            #             )
            #         )
            #
            #     file.write(line.replace("- [x]", "- [ ]"))
            #
            # # Удаляем остаток предыдущего содержимого файла
            # file.truncate()

        # # Вывод результатов
        # if replaced_lines:
        #     print("Скрипт unchek_regular_task завершен успешно. Следующие строки были заменены:")
        #     for original, modified in replaced_lines:
        #         print(f"'{original}' -> '{modified}'")
        # else:
        #     print("Скрипт unchek_regular_task завершен успешно. Замены не потребовались.")
        #
        # if date_was_updated:
        #     print("Дата в YAML-заголовке была обновлена.")
