import yaml
from datetime import datetime
from const import DATE_FORMAT

class MarkdownWorker:
    """
    Класс для работы с Markdown файлами.
    Позволяет разбивать на логические блоки информацию, находящуюся в файлах типа md и работать со структурой и текстом
    внутри файлов.
    На вход принимает прочитанный контент из файла и формирует блок YAML заголовка, а также основной
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

    def __get_content_lines(self) -> list[str]:
        """Возвращает список строк основного контента (после YAML-заголовка)"""
        if self.content_start >= len(self.content):
            return []

        content_lines = self.content[self.content_start:]
        return content_lines

    def unchecked_task_searcher(self):
        all_task_done = []

        for line in self.content_lines:
            line = line.strip()
            if line.startswith("```button"):
                break
            elif line.startswith("### "):
                continue
            elif line.startswith("- [ ]"):  # Найдена невыполненная задача
                all_task_done.append(False)
            else:
                all_task_done.append(True)

        return all(all_task_done)

    def overwrite_yaml_header(self):
        """
        Перезаписывает YAML заголовок в файле, оставляя без изменений основной контент
        :return: new_content - новый контент файла с обновленным YAML заголовком.
        """
        if 'tags' not in self.yaml_header:
            self.yaml_header['tags'] = []
        self.yaml_header['tags'].append('выполнено')

        # Формируем новый контент файла
        new_content = list()
        new_content.append("---\n")
        new_content.extend(yaml.dump(self.yaml_header, allow_unicode=True).splitlines(keepends=True))
        new_content.append("---\n")
        new_content.extend(self.content[self.content_start:])

        return new_content

    def parse_task_content(self):
        task_content = ""

        for line in self.content_lines:
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

    def regular_file_changer(self):
        new_content = []
        self.yaml_header['date'] = datetime.now().strftime(DATE_FORMAT)

        # Добавляем обновленный YAML заголовок
        new_content.append("---\n")
        new_content.extend(yaml.dump(self.yaml_header, allow_unicode=True).splitlines(keepends=True))
        new_content.append("---\n")

        # Обрабатываем основной контент, заменяя выполненные задачи на невыполненные
        for line in self.content_lines:
            if "- [x]" in line:
                new_line = line.replace("- [x]", "- [ ]")
                new_content.append(new_line)
            else:
                new_content.append(line)

        return new_content
