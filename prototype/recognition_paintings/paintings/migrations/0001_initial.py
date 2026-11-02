from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Artwork",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="Название")),
                ("artist", models.CharField(max_length=100, verbose_name="Художник")),
                ("year", models.IntegerField(blank=True, null=True, verbose_name="Год")),
                ("image", models.ImageField(blank=True, null=True, upload_to="artworks/", verbose_name="Изображение")),
                ("style_tag", models.CharField(choices=[("dali", "Дали"), ("magritte", "Магритт"), ("ernst", "Эрнст"), ("miro", "Миро")], max_length=20, verbose_name="Стиль")),
                ("description", models.TextField(blank=True)),
            ],
        ),
    ]
