import os
import shutil
import yaml
from datetime import datetime


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
                    lines = file.readlines()

                # Парсинг YAML-заголовка
                    yaml_header = {}
                    content_start = 0

                    if lines[0].strip() == "---":
                        for i, line in enumerate(lines[1:], start=1):
                            if line.strip() == "---":
                                content_start = i + 1
                                yaml_header = yaml.safe_load("".join(lines[1:i]))
                                break

                    if 'выполнено' in yaml_header.get('tags', []):
                        self.task_mover(tasks_path, file_name)

                    else:
                        # Проверка задач
                        all_tasks_done = True
                        for line in lines[content_start:]:
                            line = line.strip()
                            if line.startswith("- [ ]"):  # Найдена невыполненная задача
                                all_tasks_done = False
                                break

                        # Обновляем YAML-заголовок
                        if all_tasks_done:
                            if 'tags' not in yaml_header:
                                yaml_header['tags'] = []
                            yaml_header['tags'].append('выполнено')

                            # Формируем новый контент файла
                            new_content = list()
                            new_content.append("---\n")
                            new_content.extend(yaml.dump(yaml_header, allow_unicode=True).splitlines(keepends=True))
                            new_content.append("---\n")
                            new_content.extend(lines[content_start:])

                            # Перезаписываем файл
                            file.seek(0)  # Устанавливаем указатель в начало файла
                            file.writelines(new_content)  # Записываем новый контент
                            file.truncate()  # Убираем остатки старого содержимого, если новый контент короче

                            # Перемещаем файл в папку Выполнено
                            self.task_mover(tasks_path, file_name)

                        # Название файла без его свойства
                        name = file_name.strip(".md")

                        # Если есть невыполненные задачи, добавляем описание задачи
                        if not all_tasks_done:
                            description = ""

                            for line in lines[content_start:]:
                                # Убираем лишнее описание из задачи
                                if line.startswith('```button'):
                                    break
                                # Пропускаем заголовок для подзадач
                                elif line.startswith('###'):
                                    continue
                                # Записываю в описание только невыполненные задачи
                                elif line.startswith('- [ ]'):
                                    description += line[:5] + line[21:]

                            # В случае если задача не была перемещена в выполнено, добавляем ее в список задач
                            tasks_dict[name] = [yaml_header, description]

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
            lines = file.readlines()

            # Перемещаем указатель в начало файла
            file.seek(0)

            in_yaml = False

            for line in lines:
                if line.strip() == "---":  # Начало или конец YAML-заголовка
                    in_yaml = not in_yaml

                # Если внутри YAML-заголовка
                elif in_yaml and line.startswith("date:"):
                    # Перезаписываем дату
                    file.write(f"date: {datetime.now().strftime(date_format)}\n")
                    date_was_updated = True
                    continue

                # Заменяем символы в строках и записываем обратно
                if "- [x]" in line:
                    replaced_lines.append(
                        (
                            line.strip(),
                            line.replace("- [x]", "- [ ]").strip()
                        )
                    )

                file.write(line.replace("- [x]", "- [ ]"))

            # Удаляем остаток предыдущего содержимого файла
            file.truncate()

        # Вывод результатов
        if replaced_lines:
            print("Скрипт unchek_regular_task завершен успешно. Следующие строки были заменены:")
            for original, modified in replaced_lines:
                print(f"'{original}' -> '{modified}'")
        else:
            print("Скрипт unchek_regular_task завершен успешно. Замены не потребовались.")

        if date_was_updated:
            print("Дата в YAML-заголовке была обновлена.")
