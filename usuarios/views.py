from urllib import request

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Formulário personalizado para incluir o e-mail no cadastro
class CriarContaForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

def cadastro_view(request):
    if request.method == 'POST':
        form = CriarContaForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CriarContaForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@login_required
def dashboard_view(request):
    user = request.user
    nome = user.get_full_name() or user.username
    partes = nome.split()
    iniciais = (partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")).upper()

    context = {
        "iniciais": iniciais,
        "ano_foco": 2026,
        "ia_ativa": True,
        "total_redacoes": 0,
        "ultima_nota": None,
        "flashcards_hoje": 0,
        "duvidas_respondidas": 0,
        "redacoes_recentes": [],
        "areas": AREAS,
    }
    return render(request, 'usuarios/dashboard.html', context)

AREAS = [
    {"nome": "Linguagens, Códigos e suas Tecnologias",
     "descricao": "Língua Portuguesa, Literatura, Língua Estrangeira, Interpretação e Coesão Textual.",
     "icone": "languages", "cor": "red", "url": "#"},
    {"nome": "Ciências Humanas e suas Tecnologias",
     "descricao": "História do Brasil e Geral, Geografia, Filosofia e Sociologia.",
     "icone": "globe", "cor": "amber", "url": "#"},
    {"nome": "Ciências da Natureza e suas Tecnologias",
     "descricao": "Biologia (Ecologia, Genética, Citologia), Física e Química.",
     "icone": "microscope", "cor": "green", "url": "#"},
    {"nome": "Matemática e suas Tecnologias",
     "descricao": "Funções, Porcentagem, Geometria Plana e Espacial, Estatística e Probabilidade.",
     "icone": "calculator", "cor": "blue", "url": "#"},
]

