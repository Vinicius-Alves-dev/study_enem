import re

from django.conf import settings
from django.db import models

# Aceita links do tipo youtube.com/watch?v=ID, youtu.be/ID, /embed/ID ou só o ID
_YT = re.compile(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})")


class Area(models.Model):
    """Nível 1: as 4 áreas do ENEM."""
    COR_CHOICES = [("green", "Verde"), ("amber", "Amarelo"), ("red", "Vermelho"), ("blue", "Azul")]

    nome = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=40, default="book-open", help_text="Nome de um ícone em lucide.dev")
    cor = models.CharField(max_length=10, choices=COR_CHOICES, default="blue")
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Área do conhecimento"
        verbose_name_plural = "Áreas do conhecimento"

    def __str__(self):
        return self.nome

    @property
    def nome_curto(self):
        return self.nome.replace(" e suas Tecnologias", "")


class Disciplina(models.Model):
    """Nível 2: Biologia, Física, Química..."""
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="disciplinas")
    nome = models.CharField(max_length=120)
    slug = models.SlugField()
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=40, default="book-open")
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        unique_together = [("area", "slug")]

    def __str__(self):
        return f"{self.nome} ({self.area.nome_curto})"


class Assunto(models.Model):
    """Nível 3: Citologia, Ecologia, Genética..."""
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name="assuntos")
    nome = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180)
    descricao = models.TextField(blank=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]
        unique_together = [("disciplina", "slug")]

    def __str__(self):
        return f"{self.nome} — {self.disciplina.nome}"


class Videoaula(models.Model):
    """Nível 4: as videoaulas de cada assunto."""
    assunto = models.ForeignKey(Assunto, on_delete=models.CASCADE, related_name="videoaulas")
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    canal = models.CharField("Canal (fonte)", max_length=120, blank=True,
                             help_text="Nome do canal do YouTube. Ex.: Biologia com Samuel Cunha")
    youtube_url = models.CharField("Link do YouTube", max_length=200,
                                   help_text="Cole o link do vídeo. Ex.: https://www.youtube.com/watch?v=XXXXXXXXXXX")
    duracao_min = models.PositiveSmallIntegerField("Duração (min)", null=True, blank=True)
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "id"]

    def __str__(self):
        return self.titulo

    @property
    def youtube_id(self):
        url = self.youtube_url.strip()
        m = _YT.search(url)
        if m:
            return m.group(1)
        return url if re.fullmatch(r"[A-Za-z0-9_-]{11}", url) else ""

    @property
    def youtube_watch_url(self):
        """Link oficial do vídeo no YouTube (abre em nova aba)."""
        vid = self.youtube_id
        return f"https://www.youtube.com/watch?v={vid}" if vid else self.youtube_url

    @property
    def thumbnail_url(self):
        """Imagem de capa original do vídeo (maior qualidade)."""
        return f"https://i.ytimg.com/vi/{self.youtube_id}/maxresdefault.jpg" if self.youtube_id else ""

    @property
    def thumbnail_fallback_url(self):
        """Capa alternativa, usada se o vídeo não tiver a versão maior."""
        return f"https://i.ytimg.com/vi/{self.youtube_id}/hqdefault.jpg" if self.youtube_id else ""


class AulaConcluida(models.Model):
    """Progresso do aluno: quais videoaulas ele já marcou como assistidas."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="aulas_concluidas")
    videoaula = models.ForeignKey(Videoaula, on_delete=models.CASCADE, related_name="conclusoes")
    concluida_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("usuario", "videoaula")]
        verbose_name = "Aula concluída"
        verbose_name_plural = "Aulas concluídas"

    def __str__(self):
        return f"{self.usuario} concluiu {self.videoaula}"