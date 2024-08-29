import csv
from pathlib import Path

from django.core.management import BaseCommand

from recipes.models import Ingredient

TABLES = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_file in TABLES.items():
            path_file = (
                f'{Path(__file__).resolve().parent.parent.parent.parent}/'
                f'data/{csv_file}'
            )
            with open(path_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                model_objects = []
                for row in reader:
                    model_objects.append(model(**row))
                model.objects.bulk_create(model_objects)
                self.stdout.write(self.style.SUCCESS(
                    f'Data imported from {csv_file} into {model.__name__}'
                ))

        self.stdout.write(self.style.SUCCESS(
            'All data has been imported successfully'
        ))
