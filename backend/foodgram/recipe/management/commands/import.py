from json import load

from django.core.management import BaseCommand
# Импорт моделей
from recipe.models import Ingredient


class Command(BaseCommand):
    help = "Команда для загрузки тестовых данных в БД из csv файлов"

    # Список переменных для импорта данных в модели
    models = (
        (
            (Ingredient, 'ingredients'),
        ),
    )

    def import_data(self):
        """ Метод импортирует ингредиенты в БД. """

        for data in self.models:
            for model, file in data:
                with open(f'../../data/{file}.json', encoding='utf-8') as f:
                    print(f'Начался импорт данных {file}')
                    for row in load(f):
                        if not model.objects.filter(**row).exists():
                            model.objects.create(**row)
                print(f'Импорт данных {file} завершен.')

    def handle(self, *args, **options):
        """ Агрегирующий метод, который вызывается с помощью команды import
        и добавляет тестовые данные в БД. """

        self.import_data()
