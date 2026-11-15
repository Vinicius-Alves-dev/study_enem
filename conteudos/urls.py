from django.urls import path

from . import views

app_name = "conteudos"

urlpatterns = [
    path("", views.areas, name="areas"),
    # Esta rota precisa vir ANTES das de baixo, senão "aula/12/concluir/"
    # seria confundida com area/disciplina/assunto.
    path("aula/<int:aula_id>/concluir/", views.alternar_conclusao, name="concluir"),
    path("<slug:area_slug>/", views.area_detail, name="area"),
    path("<slug:area_slug>/<slug:disciplina_slug>/", views.disciplina_detail, name="disciplina"),
    path("<slug:area_slug>/<slug:disciplina_slug>/<slug:assunto_slug>/", views.assunto_detail, name="assunto"),
]