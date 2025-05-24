import os
from dotenv import load_dotenv
from const import DATE_FORMAT
from config import REGULAR_PATH_FILE, TASKS_PATH, LAST_DATE
from datetime import datetime
from src.hour_manager.task_manager import TaskManager, TasksUnchecker
from src.hour_manager.calendar_client import GoogleCalendar

# Загружаем .env
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(dotenv_path)


if __name__ == "__main__":
    # Обновляем файл с датой выполнения
    def update_last_run_date():
        with open(dotenv_path, 'r+') as file:  # Открываем файл в режиме чтения и записи
            lines = file.readlines()  # Читаем все строки
            file.seek(0)  # Перемещаем указатель в начало файла
            file.truncate()  # Очищаем файл (чтобы перезаписать его)

            # Фильтруем строки и добавляем новую
            lines = [line for line in lines if not line.startswith("MY_DATE=")]
            lines.append(f"MY_DATE={datetime.now().strftime(DATE_FORMAT)}\n")

            file.writelines(lines)  # Записываем обновлённые строки


    if LAST_DATE is None:
        LAST_DATE = update_last_run_date()

    if LAST_DATE.split("T")[0] != datetime.now().strftime(DATE_FORMAT).split("T")[0]:
        # Обновляю ежедневные задачи
        uncheker = TasksUnchecker()
        uncheker.uncheck_tasks(REGULAR_PATH_FILE, DATE_FORMAT)
        # Актуализирую информацию по задачам и получаю список невыполненных задач
        manage_task = TaskManager()
        tasks_dict = manage_task.task_manager(TASKS_PATH, )
        # Добавляем задачи в гугл календарь
        calendar = GoogleCalendar()
        calendar.add_to_calendar(tasks_dict)

        update_last_run_date()
        print("Скрипты выполнены, дата обновлена")
    else:
        print("Скрипты уже выполнялись сегодня.")
