import yaml


class MarkdownWorker:
    """
    Класс для работы с Markdown файлами.
    Позволяет разбивать на логические блоки информацию, находящуюся в файлах типа md и работать со структурой и текстом
    внутри файлов. На вход принимает прочитанный контент из файла и формирует блок YAML заголовка, а также основной
    контент файла, для дальнешего изменения
    """
    def __init__(self, content):
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

    def task_reader


with open('Донорство.md', 'r', encoding="utf-8") as file:
    lines = file.readlines()

parser = MarkdownParser(lines)
print("YAML заголовок:", parser.yaml_header)
print("\nОсновной контент:")
for line in parser.content_lines:
    print(line, end='')