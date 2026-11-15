from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Area, Assunto, AulaConcluida, Disciplina, Videoaula


@login_required
def areas(request):
    """Nível 1: as 4 áreas do conhecimento."""
    areas = Area.objects.annotate(
        n_disc=Count("disciplinas", distinct=True),
        n_ass=Count("disciplinas__assuntos", distinct=True),
    )
    return render(request, "conteudos/areas.html", {"areas": areas})


@login_required
def area_detail(request, area_slug):
    """Nível 2: disciplinas de uma área."""
    area = get_object_or_404(Area, slug=area_slug)
    disciplinas = area.disciplinas.annotate(
        n_ass=Count("assuntos", distinct=True),
        n_aulas=Count("assuntos__videoaulas", distinct=True),
    )
    return render(request, "conteudos/area_detail.html", {"area": area, "disciplinas": disciplinas})


@login_required
def disciplina_detail(request, area_slug, disciplina_slug):
    """Nível 3: todos os assuntos de uma disciplina."""
    disciplina = get_object_or_404(Disciplina, slug=disciplina_slug, area__slug=area_slug)
    assuntos = disciplina.assuntos.annotate(n_aulas=Count("videoaulas"))
    return render(request, "conteudos/disciplina_detail.html", {
        "area": disciplina.area, "disciplina": disciplina, "assuntos": assuntos,
    })


@login_required
def assunto_detail(request, area_slug, disciplina_slug, assunto_slug):
    """Nível 4: a videoaula do assunto (+ lista de outras aulas)."""
    assunto = get_object_or_404(
        Assunto, slug=assunto_slug,
        disciplina__slug=disciplina_slug, disciplina__area__slug=area_slug,
    )
    aulas = list(assunto.videoaulas.all())

    aula_atual = aulas[0] if aulas else None
    escolhida = request.GET.get("aula", "")
    if escolhida.isdigit():
        aula_atual = next((a for a in aulas if a.id == int(escolhida)), aula_atual)

    # Progresso do aluno: ids das aulas deste assunto que ele já assistiu
    concluidas = set(
        AulaConcluida.objects.filter(usuario=request.user, videoaula__in=aulas)
        .values_list("videoaula_id", flat=True)
    )

    return render(request, "conteudos/assunto_detail.html", {
        "area": assunto.disciplina.area, "disciplina": assunto.disciplina,
        "assunto": assunto, "aulas": aulas, "aula_atual": aula_atual,
        "posicao": aulas.index(aula_atual) + 1 if aula_atual else None,
        "concluidas": concluidas,
        "aula_concluida": bool(aula_atual and aula_atual.id in concluidas),
    })


@login_required
@require_POST
def alternar_conclusao(request, aula_id):
    """Marca a aula como assistida; se já estava, desmarca."""
    aula = get_object_or_404(
        Videoaula.objects.select_related("assunto__disciplina__area"), pk=aula_id
    )
    _, criada = AulaConcluida.objects.get_or_create(usuario=request.user, videoaula=aula)
    if not criada:
        AulaConcluida.objects.filter(usuario=request.user, videoaula=aula).delete()

    a = aula.assunto
    url = reverse("conteudos:assunto", args=[a.disciplina.area.slug, a.disciplina.slug, a.slug])
    return redirect(f"{url}?aula={aula.id}")