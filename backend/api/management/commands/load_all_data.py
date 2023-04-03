import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


def iter_csv(file_path: str):
    with open(file_path, 'r', encoding="utf8") as inp_f:
        reader = csv.reader(inp_f)
        for row in reader:
            yield row


class Command(BaseCommand):
    def handle(self, *args, **options):
        reader = iter_csv('data/ingredients.csv')
        for row in reader:
            ingredient = Ingredient(name=row[0], measurement_unit=row[1])
            ingredient.save()

        reader = iter_csv('data/tags.csv')
        for row in reader:
            tag = Tag(name=row[0], color=row[1], slug=row[2])
            tag.save()
