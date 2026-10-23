import os
import random
import secrets
import sqlite3
import time
import uuid

from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for
)

app = Flask(__name__)

BASE = Path(__file__).resolve().parent
DATABASE = BASE / "devquiz.db"
KEY_FILE = BASE / ".devquiz-secret"

secret = os.environ.get("SECRET_KEY")

if not secret:
    if not KEY_FILE.exists():
        KEY_FILE.write_text(secrets.token_hex(32), encoding="utf-8")

    secret = KEY_FILE.read_text(encoding="utf-8").strip()

app.config.update(
    SECRET_KEY=secret,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=64 * 1024
)

CATEGORIAS = ["Python", "JavaScript", "SQL"]
NIVEIS = ["Fácil", "Médio", "Difícil"]

TEMPOS = {
    "Fácil": 45,
    "Médio": 60,
    "Difícil": 90
}

BANCO = []


def pergunta(categoria, nivel, titulo, codigo, opcoes, correta, explicacao):
    BANCO.append({
        "id": len(BANCO) + 1,
        "categoria": categoria,
        "nivel": nivel,
        "titulo": titulo,
        "codigo": codigo,
        "opcoes": opcoes,
        "correta": correta,
        "explicacao": explicacao
    })


pergunta(
    "Python", "Fácil",
    "Qual é o resultado desta expressão?",
    "print(3 ** 2)",
    ["6", "9", "8", "32"], 1,
    "** representa potenciação. Portanto, 3 ** 2 equivale a 3 × 3."
)

pergunta(
    "Python", "Fácil",
    "Qual elemento será exibido?",
    'nomes = ["Ana", "Bia", "Caio"]\nprint(nomes[1])',
    ["Ana", "Bia", "Caio", "Erro"], 1,
    "Listas usam índices iniciados em zero. O segundo elemento está no índice 1."
)

pergunta(
    "Python", "Médio",
    "Qual lista será produzida?",
    "numeros = [1, 2, 3, 4, 5]\nprint(numeros[1:4])",
    ["[1, 2, 3, 4]", "[2, 3, 4]", "[2, 3, 4, 5]", "[1, 4]"], 1,
    "O fatiamento inclui o índice inicial e exclui o final. São selecionados os índices 1, 2 e 3."
)

pergunta(
    "Python", "Médio",
    "O que será exibido?",
    'dados = {"nome": "Leticia"}\nprint(dados.get("idade", 0))',
    ["None", "Erro", "0", "idade"], 2,
    "get() retorna o valor padrão informado quando a chave não existe. Aqui, o padrão é 0."
)

pergunta(
    "Python", "Difícil",
    "Qual será o valor de a?",
    "a = [1, 2]\nb = a\nb.append(3)\nprint(a)",
    ["[1, 2]", "[1, 2, 3]", "[3]", "Erro"], 1,
    "a e b referenciam a mesma lista. Uma alteração feita por b também é observada por a."
)

pergunta(
    "Python", "Difícil",
    "O que será exibido?",
    "def adicionar(valor, lista=None):\n"
    "    if lista is None:\n"
    "        lista = []\n"
    "    lista.append(valor)\n"
    "    return lista\n\n"
    "adicionar(1)\n"
    "print(adicionar(2))",
    ["[1, 2]", "[2]", "[]", "None"], 1,
    "Quando lista é None, a função cria uma nova lista em cada chamada. A segunda chamada retorna somente [2]."
)

pergunta(
    "JavaScript", "Fácil",
    "Qual é o resultado da comparação?",
    'console.log(5 === "5");',
    ["true", "false", "undefined", "5"], 1,
    "=== compara sem converter automaticamente os tipos. Um número e uma string não são estritamente iguais."
)

pergunta(
    "JavaScript", "Fácil",
    "Qual método adiciona um elemento ao final de um array?",
    'const linguagens = ["Python"];',
    ["push()", "pop()", "shift()", "slice()"], 0,
    "push() adiciona elementos ao final. pop() remove o último e shift() remove o primeiro."
)

pergunta(
    "JavaScript", "Médio",
    "Qual array será exibido?",
    "const valores = [1, 2, 3];\n"
    "console.log(valores.map(numero => numero * 2));",
    ["[1, 2, 3]", "[2, 4, 6]", "[3, 6, 9]", "[2]"], 1,
    "map() cria um novo array com o resultado da função aplicada a cada elemento."
)

pergunta(
    "JavaScript", "Médio",
    "Qual valor será exibido?",
    "const valores = [2, 5, 8, 11];\n"
    "console.log(valores.filter(n => n > 5).length);",
    ["1", "2", "3", "4"], 1,
    "filter() mantém 8 e 11, pois são maiores que 5. O array resultante possui dois elementos."
)

pergunta(
    "JavaScript", "Difícil",
    "Em qual ordem os valores aparecem no console?",
    'console.log("A");\n'
    'setTimeout(() => console.log("B"), 0);\n'
    'console.log("C");',
    ["A, B, C", "B, A, C", "A, C, B", "C, B, A"], 2,
    "O callback de setTimeout não interrompe o código síncrono. A e C são exibidos antes de B."
)

pergunta(
    "JavaScript", "Difícil",
    "Qual valor será exibido?",
    "const a = { pontos: 10 };\n"
    "const b = { ...a };\n"
    "b.pontos = 20;\n"
    "console.log(a.pontos);",
    ["10", "20", "30", "undefined"], 0,
    "O spread cria uma cópia superficial do objeto. Como pontos é um número, alterar b.pontos não altera a.pontos."
)

pergunta(
    "SQL", "Fácil",
    "Qual comando consulta todas as colunas de uma tabela?",
    "",
    [
        "SELECT * FROM alunos;",
        "GET alunos;",
        "INSERT INTO alunos;",
        "OPEN alunos;"
    ], 0,
    "SELECT consulta dados. O asterisco seleciona todas as colunas da tabela indicada em FROM."
)

pergunta(
    "SQL", "Fácil",
    "Qual cláusula filtra linhas?",
    "SELECT * FROM produtos\n_____ preco > 100;",
    ["ORDER BY", "WHERE", "VALUES", "SET"], 1,
    "WHERE estabelece condições que as linhas devem atender para aparecer no resultado."
)

pergunta(
    "SQL", "Médio",
    "Como ordenar os preços do maior para o menor?",
    "",
    [
        "ORDER BY preco ASC",
        "GROUP BY preco",
        "ORDER BY preco DESC",
        "WHERE preco DESC"
    ], 2,
    "ORDER BY ordena resultados. DESC usa ordem decrescente; ASC usa ordem crescente."
)

pergunta(
    "SQL", "Médio",
    "Qual função conta todas as linhas de uma consulta?",
    "",
    ["SUM(*)", "COUNT(*)", "TOTAL_ROWS()", "MAX(*)"], 1,
    "COUNT(*) conta linhas, inclusive aquelas que possuem valores NULL em alguma coluna."
)

pergunta(
    "SQL", "Difícil",
    "Qual cláusula filtra grupos após uma agregação?",
    "SELECT categoria, COUNT(*)\n"
    "FROM produtos\n"
    "GROUP BY categoria\n"
    "_____ COUNT(*) > 3;",
    ["WHERE", "ORDER BY", "HAVING", "LIMIT"], 2,
    "HAVING filtra grupos produzidos por GROUP BY. WHERE filtra linhas antes do agrupamento."
)

pergunta(
    "SQL", "Difícil",
    "Qual JOIN mantém todos os alunos, mesmo aqueles sem matrícula?",
    "SELECT alunos.nome, matriculas.id\n"
    "FROM alunos\n"
    "_____ matriculas ON matriculas.aluno_id = alunos.id;",
    ["INNER JOIN", "LEFT JOIN", "CROSS JOIN", "JOIN"], 1,
    "LEFT JOIN mantém todas as linhas da tabela à esquerda. Sem correspondência, as colunas da tabela à direita ficam NULL."
)

QUESTOES = {item["id"]: item for item in BANCO}


def conectar():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def iniciar_banco():
    with conectar() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS partidas (
                id TEXT PRIMARY KEY,
                visitante TEXT NOT NULL,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                nivel TEXT NOT NULL,
                modo TEXT NOT NULL,
                total INTEGER NOT NULL,
                finalizada INTEGER NOT NULL DEFAULT 0,
                criada_em TEXT NOT NULL,
                finalizada_em TEXT
            );

            CREATE TABLE IF NOT EXISTS respostas (
                partida_id TEXT NOT NULL,
                ordem INTEGER NOT NULL,
                pergunta_id INTEGER NOT NULL,
                escolha INTEGER,
                respondida INTEGER NOT NULL DEFAULT 0,
                acertou INTEGER NOT NULL DEFAULT 0,
                iniciada_em REAL,
                segundos INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (partida_id, ordem),
                FOREIGN KEY (partida_id) REFERENCES partidas(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_visitante
            ON partidas(visitante);
        """)


@app.before_request
def preparar_sessao():
    if "visitante" not in session:
        session["visitante"] = uuid.uuid4().hex

    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(24)

    if request.method == "POST":
        recebido = request.form.get("csrf", "")

        if not secrets.compare_digest(recebido, session["csrf"]):
            abort(400, description="Sessão inválida. Recarregue a página.")


@app.context_processor
def contexto():
    return {
        "categorias": CATEGORIAS,
        "niveis": NIVEIS,
        "csrf": session.get("csrf", "")
    }


@app.template_filter("data_br")
def data_br(valor):
    if not valor:
        return ""
    return datetime.fromisoformat(valor).strftime("%d/%m/%Y às %H:%M")


def carregar_partida(db, partida_id):
    partida = db.execute("""
        SELECT * FROM partidas
        WHERE id = ? AND visitante = ?
    """, (partida_id, session["visitante"])).fetchone()

    if partida is None:
        abort(404)

    return partida


def finalizar(db, partida_id):
    db.execute("""
        UPDATE partidas
        SET finalizada = 1, finalizada_em = ?
        WHERE id = ? AND finalizada = 0
    """, (datetime.now().isoformat(timespec="seconds"), partida_id))


@app.route("/")
def inicio():
    with conectar() as db:
        historico = db.execute("""
            SELECT p.*,
                   SUM(r.acertou) AS acertos,
                   SUM(r.segundos) AS duracao
            FROM partidas p
            JOIN respostas r ON r.partida_id = p.id
            WHERE p.visitante = ? AND p.finalizada = 1
            GROUP BY p.id
            ORDER BY p.finalizada_em DESC
        """, (session["visitante"],)).fetchall()

        ativa = db.execute("""
            SELECT p.*,
                   SUM(r.respondida) AS respondidas
            FROM partidas p
            JOIN respostas r ON r.partida_id = p.id
            WHERE p.visitante = ? AND p.finalizada = 0
            GROUP BY p.id
            ORDER BY p.criada_em DESC
            LIMIT 1
        """, (session["visitante"],)).fetchone()

        ranking = db.execute("""
            SELECT p.nome,
                   p.finalizada_em,
                   SUM(r.acertou) AS acertos,
                   SUM(r.segundos) AS duracao
            FROM partidas p
            JOIN respostas r ON r.partida_id = p.id
            WHERE p.finalizada = 1
              AND p.categoria = 'Todas'
              AND p.nivel = 'Todos'
              AND p.modo = 'desafio'
              AND p.total = ?
            GROUP BY p.id
            ORDER BY acertos DESC, duracao ASC, p.finalizada_em ASC
            LIMIT 10
        """, (len(BANCO),)).fetchall()

    quantidade = len(historico)
    total_respondido = sum(item["total"] for item in historico)
    total_acertos = sum(item["acertos"] for item in historico)

    aproveitamento = (
        round(total_acertos / total_respondido * 100)
        if total_respondido else 0
    )

    melhor = max(
        (round(item["acertos"] / item["total"] * 100) for item in historico),
        default=0
    )

    return render_template(
        "index.html",
        tela="inicio",
        historico=historico,
        ativa=ativa,
        ranking=ranking,
        quantidade=quantidade,
        total_acertos=total_acertos,
        aproveitamento=aproveitamento,
        melhor=melhor,
        banco=BANCO
    )


@app.route("/iniciar", methods=["POST"])
def iniciar():
    nome = request.form.get("nome", "").strip()[:40] or "Estudante"
    categoria = request.form.get("categoria", "Todas")
    nivel = request.form.get("nivel", "Todos")
    modo = request.form.get("modo", "treino")

    if categoria not in CATEGORIAS + ["Todas"]:
        abort(400)

    if nivel not in NIVEIS + ["Todos"]:
        abort(400)

    if modo not in ["treino", "desafio"]:
        abort(400)

    selecionadas = [
        item for item in BANCO
        if (categoria == "Todas" or item["categoria"] == categoria)
        and (nivel == "Todos" or item["nivel"] == nivel)
    ]

    random.shuffle(selecionadas)
    partida_id = uuid.uuid4().hex

    with conectar() as db:
        db.execute("""
            INSERT INTO partidas (
                id, visitante, nome, categoria, nivel,
                modo, total, criada_em
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            partida_id,
            session["visitante"],
            nome,
            categoria,
            nivel,
            modo,
            len(selecionadas),
            datetime.now().isoformat(timespec="seconds")
        ))

        db.executemany("""
            INSERT INTO respostas (partida_id, ordem, pergunta_id)
            VALUES (?, ?, ?)
        """, [
            (partida_id, indice, item["id"])
            for indice, item in enumerate(selecionadas)
        ])

    session["nome"] = nome

    return redirect(url_for("quiz", partida_id=partida_id))


@app.route("/quiz/<partida_id>")
def quiz(partida_id):
    with conectar() as db:
        partida = carregar_partida(db, partida_id)

        if partida["finalizada"]:
            return redirect(url_for("resultado", partida_id=partida_id))

        atual = db.execute("""
            SELECT * FROM respostas
            WHERE partida_id = ? AND respondida = 0
            ORDER BY ordem
            LIMIT 1
        """, (partida_id,)).fetchone()

        if atual is None:
            finalizar(db, partida_id)
            return redirect(url_for("resultado", partida_id=partida_id))

        agora = time.time()

        db.execute("""
            UPDATE respostas
            SET iniciada_em = COALESCE(iniciada_em, ?)
            WHERE partida_id = ? AND ordem = ?
        """, (agora, partida_id, atual["ordem"]))

        atual = db.execute("""
            SELECT * FROM respostas
            WHERE partida_id = ? AND ordem = ?
        """, (partida_id, atual["ordem"])).fetchone()

    questao = QUESTOES[atual["pergunta_id"]]

    limite = TEMPOS[questao["nivel"]]
    restante = max(0, limite - (time.time() - atual["iniciada_em"]))

    return render_template(
        "index.html",
        tela="quiz",
        partida=partida,
        atual=atual,
        questao=questao,
        restante=restante,
        progresso=round(atual["ordem"] / partida["total"] * 100)
    )


@app.route("/responder/<partida_id>", methods=["POST"])
def responder(partida_id):
    try:
        ordem = int(request.form.get("ordem", ""))
        escolha = int(request.form.get("escolha", "-1"))
    except ValueError:
        abort(400)

    with conectar() as db:
        db.execute("BEGIN IMMEDIATE")
        partida = carregar_partida(db, partida_id)

        if partida["finalizada"]:
            return redirect(url_for("resultado", partida_id=partida_id))

        atual = db.execute("""
            SELECT * FROM respostas
            WHERE partida_id = ? AND respondida = 0
            ORDER BY ordem
            LIMIT 1
        """, (partida_id,)).fetchone()

        if atual is None:
            finalizar(db, partida_id)
            return redirect(url_for("resultado", partida_id=partida_id))

        if ordem != atual["ordem"] or atual["iniciada_em"] is None:
            return redirect(url_for("quiz", partida_id=partida_id))

        questao = QUESTOES[atual["pergunta_id"]]

        if escolha not in [-1, 0, 1, 2, 3]:
            abort(400)

        decorrido = max(0, time.time() - atual["iniciada_em"])
        limite = TEMPOS[questao["nivel"]]

        if partida["modo"] == "desafio" and decorrido >= limite:
            escolha = -1

        segundos = round(
            min(decorrido, limite)
            if partida["modo"] == "desafio"
            else decorrido
        )

        acertou = int(escolha == questao["correta"])

        db.execute("""
            UPDATE respostas
            SET escolha = ?, respondida = 1, acertou = ?, segundos = ?
            WHERE partida_id = ? AND ordem = ? AND respondida = 0
        """, (
            escolha, acertou, segundos, partida_id, ordem
        ))

        restantes = db.execute("""
            SELECT COUNT(*) FROM respostas
            WHERE partida_id = ? AND respondida = 0
        """, (partida_id,)).fetchone()[0]

        if restantes == 0:
            finalizar(db, partida_id)

    return redirect(url_for("quiz", partida_id=partida_id))


@app.route("/resultado/<partida_id>")
def resultado(partida_id):
    with conectar() as db:
        partida = carregar_partida(db, partida_id)

        if not partida["finalizada"]:
            return redirect(url_for("quiz", partida_id=partida_id))

        respostas = db.execute("""
            SELECT * FROM respostas
            WHERE partida_id = ?
            ORDER BY ordem
        """, (partida_id,)).fetchall()

    revisao = []
    desempenho = {}
    acertos = 0
    sequencia = 0
    melhor_sequencia = 0

    for resposta in respostas:
        questao = QUESTOES[resposta["pergunta_id"]]
        categoria = questao["categoria"]

        desempenho.setdefault(categoria, {"acertos": 0, "total": 0})
        desempenho[categoria]["total"] += 1

        if resposta["acertou"]:
            acertos += 1
            sequencia += 1
            desempenho[categoria]["acertos"] += 1
        else:
            sequencia = 0

        melhor_sequencia = max(melhor_sequencia, sequencia)

        revisao.append({
            "questao": questao,
            "resposta": resposta
        })

    percentual = round(acertos / partida["total"] * 100)
    duracao = sum(item["segundos"] for item in respostas)
    sem_resposta = sum(item["escolha"] == -1 for item in respostas)

    if percentual == 100:
        titulo = "Rodada perfeita!"
    elif percentual >= 70:
        titulo = "Você está avançando!"
    else:
        titulo = "Cada tentativa ensina."

    sugestoes = [
        categoria for categoria, dados in desempenho.items()
        if dados["acertos"] < dados["total"]
    ]

    return render_template(
        "index.html",
        tela="resultado",
        partida=partida,
        revisao=revisao,
        desempenho=desempenho,
        acertos=acertos,
        percentual=percentual,
        duracao=duracao,
        sem_resposta=sem_resposta,
        melhor_sequencia=melhor_sequencia,
        titulo=titulo,
        sugestoes=sugestoes
    )


iniciar_banco()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)