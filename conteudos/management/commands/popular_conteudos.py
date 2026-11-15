from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from conteudos.models import Area, Assunto, Disciplina

DADOS = [
    {
        "slug": "ciencias-da-natureza", "nome": "Ciências da Natureza e suas Tecnologias",
        "descricao": "Compreenda os fenômenos naturais, processos biológicos, transformações químicas e leis físicas aplicados ao cotidiano e às questões do ENEM.",
        "icone": "microscope", "cor": "green",
        "disciplinas": [
            {"slug": "biologia", "nome": "Biologia", "icone": "dna",
             "descricao": "Estudo dos seres vivos, ecossistemas, evolução, genética e fisiologia humana.",
             "assuntos": ["Citologia", "Bioquímica Celular", "Metabolismo Energético: Fotossíntese e Respiração", "Divisão Celular: Mitose e Meiose",
                          "Histologia", "Embriologia e Reprodução", "Fisiologia Humana", "Imunologia, Vacinas e Soros",
                          "Genética Clássica: Leis de Mendel", "Genética Molecular: DNA, RNA e Síntese de Proteínas", "Biotecnologia e Engenharia Genética",
                          "Evolução", "Taxonomia e Classificação dos Seres Vivos", "Vírus e Bactérias", "Protozoários, Fungos e Doenças Parasitárias",
                          "Botânica", "Zoologia", "Ecologia", "Ciclos Biogeoquímicos", "Impactos Ambientais e Sustentabilidade"]},
            {"slug": "fisica", "nome": "Física", "icone": "zap",
             "descricao": "Mecânica, termologia, óptica, ondulatória e eletrodinâmica em situações práticas.",
             "assuntos": ["Cinemática", "Dinâmica: Leis de Newton", "Trabalho, Energia e Potência", "Impulso e Quantidade de Movimento",
                          "Gravitação Universal", "Estática", "Hidrostática", "Termologia e Calorimetria", "Termodinâmica",
                          "Óptica Geométrica", "Ondulatória e Acústica", "Eletrostática", "Eletrodinâmica: Circuitos Elétricos",
                          "Eletromagnetismo", "Física Moderna", "Fontes de Energia"]},
            {"slug": "quimica", "nome": "Química", "icone": "flask-conical",
             "descricao": "Estrutura atômica, ligações químicas, estequiometria, físico-química e química orgânica.",
             "assuntos": ["Modelos Atômicos e Estrutura do Átomo", "Tabela Periódica e Propriedades", "Ligações Químicas", "Geometria e Polaridade das Moléculas",
                          "Funções Inorgânicas", "Reações Químicas", "Estequiometria", "Gases", "Soluções e Concentração",
                          "Propriedades Coligativas", "Termoquímica", "Cinética Química", "Equilíbrio Químico", "Eletroquímica: Pilhas e Eletrólise",
                          "Radioatividade", "Química Orgânica: Funções e Nomenclatura", "Isomeria", "Reações Orgânicas", "Polímeros", "Química Ambiental"]},
        ],
    },
    {
        "slug": "ciencias-humanas", "nome": "Ciências Humanas e suas Tecnologias",
        "descricao": "Analise processos históricos, transformações geográficas, geopolítica, pensamento filosófico e relações sociais.",
        "icone": "globe", "cor": "amber",
        "disciplinas": [
            {"slug": "historia", "nome": "História", "icone": "landmark",
             "descricao": "Do Brasil e do mundo: da Antiguidade aos dias atuais.",
             "assuntos": ["Povos Indígenas e Pré-história", "Antiguidade Clássica: Grécia e Roma", "Idade Média e Feudalismo", "Renascimento e Reformas",
                          "Absolutismo e Mercantilismo", "Brasil Colônia", "Escravidão e Cultura Africana no Brasil", "Revolução Industrial", "Iluminismo e Revolução Francesa",
                          "Independência das Américas", "Brasil Império", "Imperialismo e Neocolonialismo", "Primeira Guerra Mundial", "Brasil: República Velha",
                          "Entreguerras, Totalitarismos e Segunda Guerra", "Era Vargas", "Guerra Fria", "Ditadura Militar e Redemocratização", "Brasil Contemporâneo"]},
            {"slug": "geografia", "nome": "Geografia", "icone": "map",
             "descricao": "Espaço geográfico, meio ambiente, população, economia e geopolítica.",
             "assuntos": ["Cartografia e Orientação", "Geologia e Relevo", "Climatologia", "Hidrografia", "Biomas e Domínios Morfoclimáticos",
                          "Questões Ambientais", "Demografia e População", "Migrações", "Urbanização", "Agropecuária e Questão Agrária",
                          "Industrialização", "Globalização", "Geopolítica e Conflitos Atuais", "Matriz Energética", "Regionalização do Brasil"]},
            {"slug": "filosofia", "nome": "Filosofia", "icone": "brain",
             "descricao": "Das origens do pensamento grego às questões éticas e políticas contemporâneas.",
             "assuntos": ["Filosofia Antiga: Pré-socráticos, Sócrates, Platão e Aristóteles", "Filosofia Medieval", "Filosofia Moderna: Racionalismo e Empirismo",
                          "Filosofia Política e Contratualismo", "Ética e Moral", "Teoria do Conhecimento", "Filosofia Contemporânea"]},
            {"slug": "sociologia", "nome": "Sociologia", "icone": "users",
             "descricao": "Sociedade, cultura, trabalho, desigualdade e cidadania.",
             "assuntos": ["Clássicos: Durkheim, Weber e Marx", "Cultura e Identidade", "Desigualdade e Estratificação Social", "Trabalho e Sociedade",
                          "Movimentos Sociais", "Cidadania e Direitos Humanos", "Indústria Cultural e Cultura de Massa"]},
        ],
    },
    {
        "slug": "linguagens", "nome": "Linguagens, Códigos e suas Tecnologias",
        "descricao": "Domine interpretação de textos, gêneros textuais, variação linguística, literatura brasileira e estratégias de redação.",
        "icone": "languages", "cor": "red",
        "disciplinas": [
            {"slug": "lingua-portuguesa", "nome": "Língua Portuguesa", "icone": "book-text",
             "descricao": "Interpretação, gramática contextualizada, coesão e variação linguística.",
             "assuntos": ["Interpretação de Texto", "Gêneros Textuais", "Funções da Linguagem", "Variação Linguística", "Figuras de Linguagem",
                          "Coesão e Coerência", "Gramática Contextualizada", "Semântica e Intertextualidade"]},
            {"slug": "literatura", "nome": "Literatura", "icone": "scroll-text",
             "descricao": "Escolas literárias brasileiras e portuguesas e seus principais autores.",
             "assuntos": ["Trovadorismo, Humanismo e Classicismo", "Barroco", "Arcadismo", "Romantismo", "Realismo e Naturalismo",
                          "Parnasianismo e Simbolismo", "Pré-Modernismo", "Modernismo: Primeira Fase", "Modernismo: Segunda e Terceira Fases", "Literatura Contemporânea"]},
            {"slug": "lingua-estrangeira", "nome": "Língua Estrangeira", "icone": "languages",
             "descricao": "Leitura e interpretação em inglês e espanhol.",
             "assuntos": ["Interpretação de Textos em Inglês", "Vocabulário e Palavras Cognatas", "Interpretação de Textos em Espanhol", "Falsos Cognatos"]},
        ],
    },
    {
        "slug": "matematica", "nome": "Matemática e suas Tecnologias",
        "descricao": "Desenvolva raciocínio lógico e resolução de problemas envolvendo razão, proporção, funções, geometria e estatística.",
        "icone": "calculator", "cor": "blue",
        "disciplinas": [
            {"slug": "aritmetica", "nome": "Aritmética", "icone": "percent",
             "descricao": "Números, proporcionalidade, porcentagem e matemática financeira.",
             "assuntos": ["Conjuntos Numéricos e Operações", "MMC e MDC", "Razão e Proporção", "Regra de Três", "Porcentagem",
                          "Juros Simples e Compostos", "Escalas e Unidades de Medida", "Notação Científica"]},
            {"slug": "algebra-e-funcoes", "nome": "Álgebra e Funções", "icone": "sigma",
             "descricao": "Equações, funções, sequências, matrizes e trigonometria.",
             "assuntos": ["Equações e Inequações", "Função Afim", "Função Quadrática", "Função Exponencial", "Função Logarítmica",
                          "Progressão Aritmética", "Progressão Geométrica", "Sistemas Lineares", "Matrizes e Determinantes", "Trigonometria"]},
            {"slug": "geometria", "nome": "Geometria", "icone": "shapes",
             "descricao": "Figuras planas, sólidos geométricos e geometria analítica.",
             "assuntos": ["Geometria Plana: Áreas e Perímetros", "Semelhança e Teorema de Pitágoras", "Geometria Espacial: Volumes", "Geometria Analítica", "Trigonometria no Triângulo"]},
            {"slug": "estatistica-e-probabilidade", "nome": "Estatística e Probabilidade", "icone": "activity",
             "descricao": "Leitura de gráficos, medidas estatísticas, contagem e chances.",
             "assuntos": ["Leitura de Gráficos e Tabelas", "Média, Mediana e Moda", "Desvio Padrão e Variância", "Análise Combinatória", "Probabilidade"]},
        ],
    },
]


class Command(BaseCommand):
    help = "Cadastra áreas, disciplinas e assuntos do ENEM (pode rodar várias vezes sem duplicar)."

    @transaction.atomic
    def handle(self, *args, **options):
        n_ass = 0
        for i, a in enumerate(DADOS):
            area, _ = Area.objects.update_or_create(
                slug=a["slug"],
                defaults={"nome": a["nome"], "descricao": a["descricao"], "icone": a["icone"], "cor": a["cor"], "ordem": i},
            )
            for j, d in enumerate(a["disciplinas"]):
                disc, _ = Disciplina.objects.update_or_create(
                    area=area, slug=d["slug"],
                    defaults={"nome": d["nome"], "descricao": d["descricao"], "icone": d["icone"], "ordem": j},
                )
                for k, nome in enumerate(d["assuntos"]):
                    Assunto.objects.update_or_create(
                        disciplina=disc, slug=slugify(nome)[:180],
                        defaults={"nome": nome, "ordem": k},
                    )
                    n_ass += 1
        self.stdout.write(self.style.SUCCESS(f"Pronto! {len(DADOS)} áreas e {n_ass} assuntos cadastrados."))