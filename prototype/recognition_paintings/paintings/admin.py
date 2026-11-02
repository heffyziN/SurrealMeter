from django.contrib import admin
from .models import Artwork

@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "year", "style_tag")
    list_filter = ("style_tag", "artist", "year")
    search_fields = ("title", "artist", "description")
    ordering = ("artist", "year", "title")
