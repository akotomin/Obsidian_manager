from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from config import CREDENTIALS, GENERAL_CALENDAR_ID, PERSONAL_CALENDAR_ID
import pytz


class GoogleCalendar:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    CREDS = CREDENTIALS

    def __init__(self):
        creds = service_account.Credentials.from_service_account_info(
            self.CREDS, scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=creds)

    def get_calendar_list(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, calendar_id):
        calendar_list_entry = {
            'id': calendar_id
        }
        return self.service.calendarList().insert(
            body=calendar_list_entry).execute()

    def add_event(self, calendar_id, body):
        """
        Добавляет событие в календарь по переданному calendar_id
        :param calendar_id:
        :param body:
        :return:
        """
        return self.service.events().insert(
            calendarId=calendar_id,
            body=body).execute()

    def get_events_for_current_month(self, calendar_id):
        """
        Находит все события в календаре по переданному calendar_id
        :param calendar_id: календарь, в котором нужно найти все ивенты
        :return: словарь со всеми событиями в календаре за текущий месяц
        """
        # Получаем текущее время в часовом поясе Москвы
        now = datetime.now(pytz.timezone('Europe/Moscow'))

        # Начало текущего месяца (1-е число текущего месяца)
        first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Конец текущего месяца (последний день месяца в 23:59:59)
        # Для этого увеличим месяц на 1 и вычтем 1 день
        next_month = now.replace(day=28) + timedelta(days=4)  # Переход на следующий месяц
        last_day_of_month = (next_month.replace(day=1) - timedelta(days=1)).replace(hour=23, minute=59, second=59)

        # Переводим в формат ISO
        time_min = first_day_of_month.isoformat()
        time_max = last_day_of_month.isoformat()

        # Запрашиваем события в указанном диапазоне времени
        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,  # Получаем события, а не повторяющиеся шаблоны
            orderBy='startTime'  # Сортируем события по времени начала
        ).execute()

        # Преобразуем список событий в словарь, используя summary как ключ
        events_dict = {}
        for event in events.get('items', []):
            summary = event.get('summary')
            if summary:  # Проверяем, что summary существует
                events_dict[summary] = event

        return events_dict

    def delete_event(self, calendar_id, event_id):
        """
        Удаляет событие в выбранном календаре по переданному calendar_id
        :param calendar_id: Календарь, в котором требется удалить событие
        :param event_id: id события, которое требуется удалить
        """
        try:
            # Удаляем событие по ID
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
        except Exception as e:
            print(f"An error occurred: {e}")

    def add_to_calendar(self, tasks_dict):
        """
        Обрабатывает переданный словарь с задачами и обновляет их в календаре.

        В зависимости от состояния задачи выполняются следующие действия:
        - Если задача уже существует в календаре и её время изменилось, обновляет время.
        - Если задача отсутствует в календаре, добавляет её.

        Выводит в консоль сообщение о выполненном действии.

        :param tasks_dict: Словарь с задачами, содержащий информацию о времени и статусе.
        """
        # Формируем московское время
        local_tz = pytz.timezone("Europe/Moscow")

        for task_name, content in tasks_dict.items():
            # Формируем список параметров в зависимости от содержания файла
            params = {
                "description": content[1],
                "start_date": local_tz.localize(content[0].get("date")).isoformat()
                if "date" in content[0] else local_tz.localize(content[0].get("start_date")).isoformat(),
                "end_date": local_tz.localize(content[0].get("date")).isoformat()
                if "date" in content[0] else local_tz.localize(content[0].get("end_date")).isoformat(),
                "calendar_id": PERSONAL_CALENDAR_ID if "личная" in content[0].get('tags', []) else GENERAL_CALENDAR_ID
            }

            # (На случай, если я буду переносить дату задачи)
            # Если файл есть среди событий
            if task_name in self.get_events_for_current_month(params['calendar_id']).keys():
                event = self.get_events_for_current_month(params['calendar_id'])[task_name]
                event_date = event['start']['dateTime']
                if params['start_date'] == event_date:
                    print(f"Файл {task_name} уже записан в календарь")
                    continue

                # В случае если даты не равны, удаляем файл для отсутствия дублей
                else:
                    event_id = event['id']
                    self.delete_event(params['calendar_id'], event_id)

                    # Для пояснения в выводе:
                    event_name = event['summary']
                    event_date = event['start']['dateTime']
                    print(f"Событие {event_name} с датой {event_date} было успешно удалено.")

            event = {
                'summary': f'{task_name}',
                'description': f'{params["description"]}',
                'start': {
                    'dateTime': f'{params["start_date"]}',
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': f'{params["end_date"]}',
                    'timeZone': 'Europe/Moscow',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 60},
                    ]
                }
            }

            response = self.add_event(calendar_id=params['calendar_id'], body=event)
            print(f"Событие создано: {response.get('htmlLink')}")
