#!/usr/bin/env python3
"""
Gerador de flashcards para fixação de conteúdo (pós em DevOps).

Fluxo:
  1. Descobre quais READMEs (.md) foram alterados (via git).
  2. Para cada pasta alterada, lê o README + os PDFs de material de aula da pasta.
  3. Envia tudo para a API do Google Gemini pedindo flashcards em JSON.
  4. Salva o resultado em flashcards/<pasta>.json e flashcards/<pasta>.md.
     Se o JSON já existir, os cards novos são ACRESCENTADOS (e a IA recebe as
     perguntas antigas para não repetir).
  5. (Opcional) Exporta para o vault do Obsidian no formato do plugin
     Spaced Repetition. A nota é regenerada a partir do JSON, mas o histórico
     de revisão (<!--SR:...-->) que o plugin grava em cada card é mantido.

Uso local (mudanças ainda não commitadas):
    export GEMINI_API_KEY="sua-chave"
    python anotacoes.py --local   # exporta para ./vault se ele existir

Uso na pipeline (compara o commit atual com o anterior):
    python anotacoes.py --base HEAD~1
    # ou, em Pull Request:
    python anotacoes.py --base origin/main

Copiar os flashcards/*.json já gerados para o Obsidian (não usa a API):
    python anotacoes.py --sync-obsidian vault
    # roda sozinho após o git pull pelo hook .githooks/post-merge

Chave grátis: https://aistudio.google.com/apikey

ATENÇÃO: nunca coloque a chave no código ou em comentários.
Na pipeline, use GitHub Secrets (Settings > Secrets and variables > Actions).
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================
# "gemini-flash-latest" é um alias que sempre aponta para o Flash vigente.
# Se quiser fixar um modelo: export GEMINI_MODEL="nome-do-modelo"
# Para ver os nomes válidos para a sua chave: python anotacoes.py --list-models
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

# Limite de segurança para o envio inline (a API aceita ~20 MB por requisição)
MAX_INLINE_BYTES = 18 * 1024 * 1024

DEFAULT_MAX_CARDS = 15
NIVEIS_VALIDOS = {"Iniciante", "Intermediário", "Avançado"}

# Obsidian (plugin Spaced Repetition): pasta dentro do vault e tag raiz do deck
OBSIDIAN_SUBDIR = "Flashcards"
OBSIDIAN_TAG = "#flashcards"
# Vault padrão, relativo à raiz do repo (usado se existir e não houver --obsidian-dir)
OBSIDIAN_VAULT_PADRAO = "vault"


# ============================================================
# GIT: descobrir o que mudou
# ============================================================
def run_git(args: list[str], repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=repo,
        text=True,
    )


def listar_arquivos_alterados(repo: Path, base: str, local: bool) -> list[str]:
    """Retorna caminhos (relativos à raiz do repo) dos arquivos alterados."""
    if local:
        # Working tree: modificados, adicionados e não rastreados
        saida = run_git(["status", "--porcelain", "-uall"], repo)
        arquivos = []
        for linha in saida.splitlines():
            caminho = linha[3:]
            if " -> " in caminho:  # renomeado
                caminho = caminho.split(" -> ")[-1]
            arquivos.append(caminho.strip().strip('"'))
        return arquivos

    # Pipeline: diferença entre o commit base e o HEAD (ignora arquivos removidos)
    saida = run_git(["diff", "--name-only", "--diff-filter=ACMR", base, "HEAD"], repo)
    return [l.strip() for l in saida.splitlines() if l.strip()]


def obter_modulos_alterados(repo: Path, base: str, local: bool) -> list[dict]:
    """
    Para cada README alterado, devolve a pasta, o texto do README
    e os PDFs presentes na mesma pasta.
    """
    modulos = {}

    for arquivo in listar_arquivos_alterados(repo, base, local):
        p = Path(arquivo)
        eh_readme = p.name.lower().startswith("readme.") and p.suffix.lower() in {
            ".md",
            ".markdown",
        }
        if not eh_readme:
            continue

        pasta = (repo / p.parent).resolve()
        if pasta in modulos:
            continue

        caminho_readme = repo / p
        if not caminho_readme.is_file():
            continue

        modulos[pasta] = {
            "pasta": pasta,
            "nome": str(p.parent).replace("/", "__") if str(p.parent) != "." else "raiz",
            "readme_path": caminho_readme,
            "readme_texto": caminho_readme.read_text(encoding="utf-8", errors="replace"),
            "pdfs": sorted(f for f in pasta.glob("*.pdf") if f.is_file()),
        }

    return list(modulos.values())


# ============================================================
# GEMINI
# ============================================================
def montar_prompt(
    readme_texto: str, tem_pdf: bool, max_cards: int, perguntas_existentes: list[str]
) -> str:
    ja_existem = ""
    if perguntas_existentes:
        lista = "\n".join(f"- {p}" for p in perguntas_existentes)
        ja_existem = f"""
<perguntas_ja_existentes>
O aluno já estuda os flashcards abaixo. NÃO repita nem reformule essas perguntas.
Gere apenas cards para conceitos ainda não cobertos. Se não houver nada novo, retorne "flashcards": [].
{lista}
</perguntas_ja_existentes>
"""

    fonte_pdf = (
        "Você também recebeu o(s) PDF(s) com o material oficial da aula. "
        "Use-o como fonte principal de verdade e as anotações como indicação "
        "do que o aluno considerou importante."
        if tem_pdf
        else "Nenhum PDF foi enviado; baseie-se apenas nas anotações."
    )

    return f"""<contexto>
Você é um Engenheiro de DevOps sênior e especialista em retenção de conhecimento e aprendizagem acelerada (repetição espaçada e técnica de Feynman).
Seu objetivo é analisar anotações de estudo de uma pós-graduação em DevOps e o material da aula, extraindo os conceitos mais importantes e transformando-os em flashcards de alta qualidade para fixação.
{fonte_pdf}
</contexto>

<diretrizes>
1. Foco técnico: identifique termos-chave, ferramentas (Kubernetes, Terraform, Docker, CI/CD etc.), arquiteturas, métricas e práticas de DevOps.
2. Qualidade: as perguntas devem testar entendimento profundo (nada de sim/não ou decoreba rasa). Prefira "por que", "como", "quando usar", "qual a diferença entre". As respostas devem ser diretas, claras e explicativas.
3. Não invente conteúdo que não esteja no material. Se algo estiver incorreto nas anotações, corrija na resposta com base no PDF.
4. Gere no máximo {max_cards} flashcards, priorizando os conceitos mais importantes e evitando duplicatas.
5. Escreva em português do Brasil, mantendo termos técnicos em inglês quando forem o padrão da área.
6. Retorne ESTRITAMENTE JSON válido, sem texto fora do JSON.
</diretrizes>

<formatacao>
Os cards são lidos no Obsidian, então "pergunta" e "resposta" usam Markdown:
- Comandos, flags, funções, blocos, recursos, arquivos e valores SEMPRE entre crases (ex.: `terragrunt run-all apply`, `find_in_parent_folders()`, `remote_state`). Nunca use aspas simples para isso.
- "resposta": comece com UMA frase curta e direta que responde a pergunta, com o termo-chave em **negrito**. Depois, de 2 a 4 tópicos "- " com os detalhes (uma ideia por tópico, frases curtas).
- Em comparações, um tópico por lado: "- **A** → ...".
- Quando um exemplo ajudar, inclua um bloco de código curto (no máximo 6 linhas) com a linguagem indicada (```hcl, ```bash, ```yaml).
- Não use linhas em branco, títulos (#) nem tabelas. Use "\\n" para quebrar linhas.
</formatacao>

<formato_esperado>
{{
  "flashcards": [
    {{
      "conceito": "Nome do conceito ou ferramenta",
      "pergunta": "Pergunta clara e objetiva para testar o conhecimento",
      "resposta": "Explicação concisa e correta do conceito",
      "nivel": "Iniciante | Intermediário | Avançado"
    }}
  ]
}}
</formato_esperado>
{ja_existem}
<anotacoes_para_analise>
{readme_texto}
</anotacoes_para_analise>"""


def chamar_gemini(
    prompt: str,
    pdfs: list[Path],
    api_key: str,
    validar=None,
    max_tokens: int = 8192,
) -> dict:
    """Envia prompt + PDFs ao Gemini e devolve o JSON já validado.

    `validar` recebe o dict parseado e deve devolvê-lo (ou levantar ValueError
    para forçar nova tentativa). Padrão: validação de flashcards.
    """
    import requests  # só é necessário quando chama a API (o --sync-obsidian não usa)

    parts = [{"text": prompt}]

    total = 0
    for pdf in pdfs:
        dados = pdf.read_bytes()
        total += len(dados)
        if total > MAX_INLINE_BYTES:
            print(f"   ⚠️  Limite de tamanho atingido, ignorando: {pdf.name}")
            continue
        parts.append(
            {
                "inline_data": {
                    "mime_type": "application/pdf",
                    "data": base64.b64encode(dados).decode("ascii"),
                }
            }
        )
        print(f"   📎 PDF anexado: {pdf.name} ({len(dados) / 1024 / 1024:.1f} MB)")

    corpo = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json",
        },
    }
    # A chave vai no header (e não na URL) para não vazar em logs
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    ultimo_erro = None
    for tentativa in range(1, 4):
        try:
            resp = requests.post(GEMINI_URL, headers=headers, json=corpo, timeout=180)
            if resp.status_code in (429, 500, 503):
                # Erro temporário: cai no except e tenta de novo
                raise requests.exceptions.HTTPError(
                    f"{resp.status_code}: {resp.text[:200]}", response=resp
                )
            if resp.status_code >= 400:
                # Erro permanente (modelo inexistente, chave inválida...): não adianta repetir
                raise RuntimeError(
                    f"Erro {resp.status_code} da API (modelo: {GEMINI_MODEL}): {resp.text[:500]}"
                )

            texto = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return (validar or validar_flashcards)(parsear_json(texto))

        except (requests.exceptions.RequestException, KeyError, IndexError, ValueError) as e:
            ultimo_erro = e
            espera = 5 * tentativa
            print(f"   ⚠️  Tentativa {tentativa}/3 falhou: {e}. Aguardando {espera}s...")
            time.sleep(espera)

    raise RuntimeError(f"Falha ao chamar a API Gemini: {ultimo_erro}")


def parsear_json(texto: str) -> dict:
    texto = texto.strip()
    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.lower().startswith("json"):
            texto = texto[4:]
    return json.loads(texto.strip())


def validar_flashcards(dados: dict) -> dict:
    cards = dados.get("flashcards")
    if not isinstance(cards, list):
        raise ValueError("JSON sem a lista 'flashcards'")

    # Lista vazia é válida: a IA pode não ter encontrado nada novo
    validos = []
    for c in cards:
        if not all(k in c for k in ("conceito", "pergunta", "resposta")):
            continue
        if c.get("nivel") not in NIVEIS_VALIDOS:
            c["nivel"] = "Intermediário"
        validos.append(c)

    if cards and not validos:
        raise ValueError("Nenhum flashcard válido retornado")

    return {"flashcards": validos}


def listar_modelos(api_key: str) -> None:
    """Imprime os modelos que a sua chave pode usar com generateContent."""
    import requests

    resp = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
        headers={"x-goog-api-key": api_key},
        timeout=30,
    )
    resp.raise_for_status()
    for m in resp.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print(m["name"].removeprefix("models/"))


# ============================================================
# SAÍDA
# ============================================================
def normalizar(texto: str) -> str:
    return " ".join(texto.lower().split())


def carregar_flashcards(json_path: Path) -> list[dict]:
    if not json_path.is_file():
        return []
    try:
        return json.loads(json_path.read_text(encoding="utf-8")).get("flashcards", [])
    except (ValueError, AttributeError):
        print(f"   ⚠️  JSON inválido, ignorando: {json_path}")
        return []


def mesclar_flashcards(existentes: list[dict], novos: list[dict]) -> tuple[list[dict], int]:
    """Acrescenta os novos cards aos existentes, ignorando perguntas repetidas."""
    vistas = {normalizar(c["pergunta"]) for c in existentes}
    mesclados = list(existentes)
    for c in novos:
        chave = normalizar(c["pergunta"])
        if chave not in vistas:
            vistas.add(chave)
            mesclados.append(c)
    return mesclados, len(mesclados) - len(existentes)


def salvar_flashcards(modulo: dict, resultado: dict, saida_dir: Path) -> None:
    saida_dir.mkdir(parents=True, exist_ok=True)
    base = saida_dir / modulo["nome"]

    # JSON (para pipeline / importação em outras ferramentas)
    json_path = base.with_suffix(".json")
    json_path.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Markdown (para estudar direto no GitHub, resposta escondida em <details>)
    linhas = [f"# Flashcards – {modulo['nome']}", ""]
    for i, c in enumerate(resultado["flashcards"], 1):
        linhas += [
            f"## {i}. {c['conceito']} _({c['nivel']})_",
            "",
            f"**Pergunta:** {c['pergunta']}",
            "",
            "<details>",
            "<summary>Ver resposta</summary>",
            "",
            c["resposta"],
            "",
            "</details>",
            "",
        ]
    base.with_suffix(".md").write_text("\n".join(linhas), encoding="utf-8")

    print(f"   💾 Salvo: {json_path} e {base.with_suffix('.md')}")


# ============================================================
# OBSIDIAN (plugin Spaced Repetition)
# ============================================================
def texto_para_card(texto: str) -> str:
    """
    Adapta o texto à sintaxe do plugin:
      - linha em branco encerra o card, então são removidas;
      - "::" viraria um card de linha única, então é quebrado com um caractere invisível;
      - uma linha só com "?" ou "??" seria lida como separador.
    """
    linhas = []
    for linha in texto.replace("::", ":​:").splitlines():
        linha = linha.rstrip()
        if not linha.strip():
            continue
        if linha.strip() in {"?", "??"}:
            linha = "\\" + linha.strip()
        linhas.append(linha)
    return "\n".join(linhas)


def tag_do_modulo(nome: str) -> str:
    """'02-terraform__06-provider' -> '#flashcards/02-terraform/06-provider' (vira subdeck)."""
    partes = [re.sub(r"[^\w\-]", "-", p) for p in nome.split("__") if p]
    return "/".join([OBSIDIAN_TAG, *partes])


SR_COMENTARIO = re.compile(r"<!--SR:.*?-->")
ICONE_NIVEL = {"Iniciante": "🟢", "Intermediário": "🟡", "Avançado": "🔴"}


def chave_card(pergunta: str) -> str:
    """Identifica o card pela pergunta, ignorando formatação (crases, negrito, aspas...)."""
    return " ".join(re.sub(r"[\W_]+", " ", pergunta.lower()).split())


def ler_progresso(conteudo: str) -> dict[str, str]:
    """Mapeia pergunta -> comentário <!--SR:...--> que o plugin gravou na nota."""
    progresso = {}
    for bloco in re.split(r"^## ", conteudo, flags=re.M)[1:]:
        sr = SR_COMENTARIO.search(bloco)
        if not sr or "\n?\n" not in bloco:
            continue
        pergunta = bloco.split("\n?\n", 1)[0].split("\n", 1)[-1]
        progresso[chave_card(pergunta)] = sr.group(0)
    return progresso


def titulo_do_modulo(nome: str) -> str:
    """'02-terraform__05-gerenciando-ambientes' -> 'Terraform › Gerenciando ambientes'."""
    partes = [re.sub(r"^\d+[-_]", "", p).replace("-", " ").strip() for p in nome.split("__")]
    return " › ".join(p[:1].upper() + p[1:] for p in partes if p)


def exportar_obsidian(nome: str, cards: list[dict], vault: Path) -> None:
    """
    (Re)gera a nota do módulo a partir do JSON, preservando o agendamento de
    revisão (<!--SR:...-->) que o plugin grava em cada card.
    A nota é gerenciada pelo script: edições manuais nela são sobrescritas.
    """
    nota = vault / OBSIDIAN_SUBDIR / f"{nome}.md"
    nota.parent.mkdir(parents=True, exist_ok=True)
    antigo = nota.read_text(encoding="utf-8") if nota.is_file() else ""
    progresso = ler_progresso(antigo)

    contagem = {n: sum(c["nivel"] == n for c in cards) for n in ICONE_NIVEL}
    resumo = " · ".join(f"{ICONE_NIVEL[n]} {q} {n.lower()}" for n, q in contagem.items() if q)
    linhas = [
        tag_do_modulo(nome),
        "",
        f"# 🧠 {titulo_do_modulo(nome)}",
        "",
        f"> [!info] {len(cards)} cards · {resumo}",
        f"> Gerado por `anotacoes.py` a partir de `{nome.replace('__', '/')}`. "
        "Edições feitas aqui são sobrescritas; o progresso de revisão é mantido.",
        "",
    ]
    for c in cards:
        pergunta = texto_para_card(c["pergunta"])
        if not pergunta:
            continue
        linhas += [
            f"## {ICONE_NIVEL.get(c['nivel'], '🟡')} {c['conceito']}",
            "",
            pergunta,
            "?",
            texto_para_card(c["resposta"]),
        ]
        if sr := progresso.get(chave_card(pergunta)):
            linhas.append(sr)
        linhas.append("")

    novo = "\n".join(linhas)
    if novo == antigo:
        print(f"   📓 Obsidian: nada mudou em {nota.name}")
        return
    nota.write_text(novo, encoding="utf-8")
    print(f"   📓 Obsidian: {len(cards)} card(s) em {nota} ({len(progresso)} com progresso mantido)")


def sincronizar_obsidian(saida_dir: Path, vault: Path) -> int:
    """Exporta todos os flashcards/*.json para o vault (não chama a API)."""
    if not (vault / ".obsidian").is_dir():
        print(f"❌ {vault} não parece ser um vault do Obsidian (falta a pasta .obsidian).")
        return 1
    arquivos = sorted(saida_dir.glob("*.json"))
    if not arquivos:
        print(f"✅ Nenhum flashcard em {saida_dir}. Nada a sincronizar.")
        return 0
    for json_path in arquivos:
        exportar_obsidian(json_path.stem, carregar_flashcards(json_path), vault)
    return 0


# ============================================================
# MAIN
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(description="Gera flashcards dos READMEs alterados.")
    parser.add_argument("--repo", default=".", help="Raiz do repositório (padrão: .)")
    parser.add_argument("--base", default="HEAD~1", help="Commit base para o diff (padrão: HEAD~1)")
    parser.add_argument("--local", action="store_true", help="Usar git status (mudanças locais) em vez de diff")
    parser.add_argument("--output-dir", default="flashcards", help="Pasta de saída (padrão: flashcards)")
    parser.add_argument("--max-cards", type=int, default=DEFAULT_MAX_CARDS, help="Máx. de flashcards por pasta")
    parser.add_argument("--list-models", action="store_true", help="Lista os modelos disponíveis para a sua chave e sai")
    parser.add_argument(
        "--obsidian-dir",
        default=os.environ.get("OBSIDIAN_VAULT"),
        help=f"Vault do Obsidian para onde exportar os cards gerados (padrão: $OBSIDIAN_VAULT ou ./{OBSIDIAN_VAULT_PADRAO})",
    )
    parser.add_argument(
        "--sync-obsidian",
        metavar="VAULT",
        help="Só copia os flashcards/*.json existentes para o vault e sai (não usa a API)",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    saida_dir = repo / args.output_dir

    if args.sync_obsidian:
        return sincronizar_obsidian(saida_dir, Path(args.sync_obsidian).expanduser())

    vault = Path(args.obsidian_dir).expanduser() if args.obsidian_dir else None
    if vault is None and (repo / OBSIDIAN_VAULT_PADRAO / ".obsidian").is_dir():
        vault = repo / OBSIDIAN_VAULT_PADRAO
    if vault and not (vault / ".obsidian").is_dir():
        print(f"⚠️  {vault} não parece ser um vault do Obsidian; exportação desativada.")
        vault = None

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY não configurada (use GitHub Secrets na pipeline).")
        return 1

    if args.list_models:
        listar_modelos(api_key)
        return 0

    print("=" * 60)
    print(f"🧠 GERADOR DE FLASHCARDS (modelo: {GEMINI_MODEL})")
    print("=" * 60)

    try:
        modulos = obter_modulos_alterados(repo, args.base, args.local)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no git: {e}")
        print("   Dica: no GitHub Actions use actions/checkout com fetch-depth: 2 (ou 0).")
        return 1

    if not modulos:
        print("✅ Nenhum README alterado. Nada a fazer.")
        return 0

    falhas = 0
    for m in modulos:
        print(f"\n📂 Pasta: {m['nome']}")
        print(f"   📝 README: {m['readme_path'].name} | 📄 PDFs: {len(m['pdfs'])}")
        try:
            existentes = carregar_flashcards((saida_dir / m["nome"]).with_suffix(".json"))
            prompt = montar_prompt(
                m["readme_texto"],
                bool(m["pdfs"]),
                args.max_cards,
                [c["pergunta"] for c in existentes],
            )
            resultado = chamar_gemini(prompt, m["pdfs"], api_key)
            cards, qtd_novos = mesclar_flashcards(existentes, resultado["flashcards"])
            print(f"   ✓ {qtd_novos} flashcard(s) novo(s) ({len(cards)} no total)")
            salvar_flashcards(m, {"flashcards": cards}, saida_dir)
            if vault:
                exportar_obsidian(m["nome"], cards, vault)
        except Exception as e:  # noqa: BLE001
            falhas += 1
            print(f"   ❌ Falha em {m['nome']}: {e}")

    print("\n" + "=" * 60)
    print(f"Concluído: {len(modulos) - falhas}/{len(modulos)} pasta(s) com sucesso")
    print("=" * 60)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())