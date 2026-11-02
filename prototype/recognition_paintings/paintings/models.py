from django.db import models

class Artwork(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    artist = models.CharField(max_length=100, verbose_name="Художник")
    year = models.IntegerField(verbose_name="Год", null=True, blank=True)
    
    image = models.ImageField(upload_to='artworks/', null=True, blank=True, verbose_name="Изображение")
    
    STYLE_CHOICES = [
        ('dali', 'Дали'), ('magritte', 'Магритт'), 
        ('ernst', 'Эрнст'), ('miro', 'Миро'),
    ]
    style_tag = models.CharField(max_length=20, choices=STYLE_CHOICES, verbose_name="Стиль")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title