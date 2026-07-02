from django.db import migrations


DEFAULT_CATEGORIES = [
    ("Festa", "festa"),
    ("Show", "show"),
    ("Workshop", "workshop"),
    ("Esporte", "esporte"),
    ("Gastronomia", "gastronomia"),
    ("Tech & Talks", "tech"),
]


def seed_default_categories(apps, schema_editor):
    Category = apps.get_model("categories", "Category")

    for nome, slug in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(slug=slug, defaults={"nome": nome})


def unseed_default_categories(apps, schema_editor):
    Category = apps.get_model("categories", "Category")
    Category.objects.filter(slug__in=[slug for _, slug in DEFAULT_CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("categories", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, unseed_default_categories),
    ]
