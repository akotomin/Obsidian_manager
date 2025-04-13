import yaml
from datetime import datetime


class MarkdownWorker:
    """
    Класс для работы с Markdown файлами.
    Позволяет разбивать на логические блоки информацию, находящуюся в файлах типа md и работать со структурой и текстом
    внутри файлов. На вход принимает прочитанный контент из файла и формирует блок YAML заголовка, а также основной
    контент файла, для дальнешего изменения
    """
    def __init__(self, content, file_name=None):
        self.file_name = file_name.strip(".md") if file_name is not None else file_name
        self.content = content
        self.content_start = 0
        self.yaml_header = self.__parse_yaml_header()
        self.content_lines = self.__get_content_lines()

    def __parse_yaml_header(self):
        """Парсит YAML заголовок из Markdown файла"""
        if not self.content or len(self.content) < 2 or self.content[0].strip() != "---":
            return None

        for i, line in enumerate(self.content[1:], start=1):
            if line.strip() == "---":
                self.content_start = i + 1
                try:
                    yaml_content = "\n".join(self.content[1:i])
                    return yaml.safe_load(yaml_content) or None
                except yaml.YAMLError as e:
                    print(f"Ошибка парсинга YAML: {e}")
                    return None
        return None

    def __get_content_lines(self) -> list[str]:
        """Возвращает список строк основного контента (после YAML-заголовка)"""
        if self.content_start >= len(self.content):
            return []

        content_lines = self.content[self.content_start:]
        return content_lines

    def unchecked_task_searcher(self):
        for line in self.content[self.content_start:]:
            line = line.strip()
            if line.startswith("- [ ]"):  # Найдена невыполненная задача
                return True
        return False

    def overwrite_yaml_header(self, change_content=False):
        if 'tags' not in self.yaml_header:
            self.yaml_header['tags'] = []
        self.yaml_header['tags'].append('выполнено')

        if change_content:
            self.yaml_header.get()

        # Формируем новый контент файла
        new_yaml_header = list()
        new_yaml_header.append("---\n")
        new_yaml_header.extend(yaml.dump(self.yaml_header, allow_unicode=True).splitlines(keepends=True))
        new_yaml_header.append("---\n")
        new_yaml_header.extend(lines[self.content_start:])

        return new_yaml_header

    def regular_file_changer(self, date_format):
        replaced_lines = []

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

    def parse_task_content(self):
        task_content = ""

        for line in self.content[self.content_start:]:
            # Если дошли до кнопки(button), значит задачи закончились
            if line.startswith('```button'):
                break
            # Пропускаем заголовок для подзадач
            elif line.startswith('###'):
                continue
            # Записываю в описание только невыполненные задачи
            elif line.startswith('- [ ]'):
                task_content += line[:5] + line[21:]

        return task_content



with open('Донорство.md', 'r', encoding="utf-8") as file:
    lines = file.readlines()

parser = MarkdownWorker(lines)
print("YAML заголовок:", parser.yaml_header)
# print("\nОсновной контент:")
# for line in parser.content_lines:
#     print(line, end='')

parser.yaml_header['start_date'] = datetime.now().strftime(date_format)
print()