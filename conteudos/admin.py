from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Area, Assunto, Disciplina, Videoaula


class DisciplinaInline(admin.TabularInline):
    model = Disciplina
    extra = 0
    prepopulated_fields = {"slug": ("nome",)}


class VideoaulaInline(admin.TabularInline):
    model = Videoaula
    extra = 1


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nome", "cor", "ordem")
    prepopulated_fields = {"slug": ("nome",)}
    inlines = [DisciplinaInline]


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("nome", "area", "ordem")
    list_filter = ("area",)
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Assunto)
class AssuntoAdmin(admin.ModelAdmin):
    list_display = ("nome", "disciplina", "ordem")
    list_filter = ("disciplina__area", "disciplina")
    search_fields = ("nome",)
    prepopulated_fields = {"slug": ("nome",)}
    inlines = [VideoaulaInline]