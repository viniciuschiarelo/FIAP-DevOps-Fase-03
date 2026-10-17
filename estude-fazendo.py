#!/usr/bin/env python3
"""
Gerador de laboratórios práticos (Break/Fix + Construa do Zero).

Complementa o anotacoes.py: os flashcards fixam a teoria, os labs colocam a
mão na massa. Reaproveita a detecção de READMEs alterados e a chamada ao Gemini.

Fluxo:
  1. Descobre quais READMEs foram alterados (via git).
  2. Para cada pasta alterada, envia o README + PDFs da aula ao Gemini pedindo
     um laboratório em JSON.
  3. Salva em labs/<pasta>.json e labs/<pasta>.md. Se já existirem labs da
     pasta, o novo é ACRESCENTADO (e a IA recebe os títulos antigos para não repetir).
  4. (Opcional) Copia as notas para o vault do Obsidian (pasta Labs/).

Uso local (mudanças ainda não commitadas):
    export GEMINI_API_KEY="sua-chave"
    python estude-fazendo.py --local
    python estude-fazendo.py --local --tema "remote state com S3"

Uso na pipeline (compara o commit atual com o anterior):
    python estude-fazendo.py --base HEAD~1

Copiar os labs/*.md já gerados para o Obsidian (não usa a API):
    python estude-fazendo.py --sync-obsidian vault
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from anotacoes import (
    GEMINI_MODEL,
    OBSIDIAN_VAULT_PADRAO,
    chamar_gemini,
    obter_modulos_alterados,
    tag_do_modulo,
    titulo_do_modulo,
)

# Pasta dentro do vault e tag raiz no Obsidian
OBSIDIAN_SUBDIR = "Labs"
OBSIDIAN_TAG = "#labs"

# Um lab com gabarito completo é bem maior que um lote de flashcards
MAX_OUTPUT_TOKENS = 16384

CAMPOS_DESAFIO = (
    "nivel",
    "titulo_desafio",
    "cenario_e_enunciado",
    "instrucoes_de_execucao",
    "dicas",
    "criterio_de_sucesso",
    "gabarito_comentado",
)


# ============================================================
# PROMPT
# ============================================================
def montar_prompt_lab(
    readme_texto: str, tem_pdf: bool, titulos_existentes: list[str], tema_foco: str = ""
) -> str:
    """Monta o prompt para a IA gerar um Laboratório Prático (Hands-on Lab)

    focado em metodologias Break/Fix e Construção do Zero para Pós-Graduação em
    DevOps.
    """
    foco_adicional = ""
    if tema_foco:
        foco_adicional = f"""
<foco_especifico>
Dê prioridade absoluta para criar o laboratório sobre o seguinte tema/tecnologia: {tema_foco}.
</foco_especifico>
"""

    ja_existem = ""
    if titulos_existentes:
        lista = "\n".join(f"- {t}" for t in titulos_existentes)
        ja_existem = f"""
<labs_ja_existentes>
O aluno já fez os laboratórios abaixo sobre este material. Crie um lab com cenários e erros DIFERENTES,
explorando outros conceitos das anotações (ou combinando conceitos de um jeito novo).
{lista}
</labs_ja_existentes>
"""

    fonte_pdf = (
        "Você também recebeu o(s) PDF(s) com o material oficial da aula. "
        "Use-o como fonte principal de verdade para cenários, comandos corretos e boas práticas."
        if tem_pdf
        else "Nenhum PDF foi enviado; baseie-se estritamente nas anotações fornecidas."
    )

    return f"""<contexto>
Você é um Engenheiro de DevOps Principal e Especialista em Aprendizagem Prática Baseada em Problemas (Problem-Based Learning / Break-Fix Training).
Seu objetivo é analisar as anotações de estudo de um aluno de pós-graduação em DevOps e extrair um **Laboratório Prático (Hands-on Lab)** desafiador e realista.
O aluno entende a teoria, mas precisa sair da zona de "reconhecimento" e ir para a zona de "execução autônoma".
{fonte_pdf}
</contexto>
{foco_adicional}
<diretrizes>
1. FOCO EM EXECUÇÃO: O lab deve ter exatamente 2 desafios, um de cada nível:
   - **Nível 4 (Break/Fix - Conserte)**: Forneça um cenário com código/configuração quebrado de propósito (ex.: erro de sintaxe, permissão IAM, dependência cíclica, porta errada) e peça para o aluno diagnosticar e corrigir usando apenas as mensagens de erro.
   - **Nível 5 (Do Zero - Construa)**: Peça para o aluno implementar uma solução funcional a partir de um enunciado e requisitos técnicos claros.
2. AMBIENTE SEGURO: Dê preferência a soluções executáveis localmente (Docker, kind, minikube, LocalStack, Terraform CLI) ou em GitHub Codespaces, evitando custos em contas cloud reais a menos que estritamente necessário.
3. DICAS EM CAMADAS (Progressive Hints): As dicas devem ser liberadas gradualmente (Dica 1: Vaga/Direcionamento → Dica 2: Onde olhar → Dica 3: Quase o comando/solução).
4. CRITÉRIOS DE SUCESSO VERIFICÁVEIS: Diga exatamente qual comando rodar para validar que funcionou (ex.: `terraform plan` com 0 alterações, `curl -I localhost:8080` retornando 200 OK, `kubectl get pods` em status Running).
5. FIDELIDADE TÉCNICA: Utilize apenas comandos, arquivos e sintaxes atualizados das ferramentas citadas (Kubernetes, Terraform, Docker, CI/CD, AWS etc.).
6. Escreva em português do Brasil, mantendo termos técnicos em inglês quando forem o padrão da área.
7. Retorne ESTRITAMENTE JSON válido, sem texto explicativo fora da estrutura JSON.
</diretrizes>

<formatacao>
Todos os textos em Markdown dentro dos campos do JSON devem seguir estas regras:
- Nomes de arquivos, comandos, flags, recursos, variáveis e saídas de terminal SEMPRE entre crases (ex.: `terraform validate`, `deployment.yaml`, `PORT=8080`). Nunca use aspas simples para isso.
- Mantenha blocos de código/solução curtos e diretos com a linguagem especificada (```hcl, ```bash, ```yaml, ```json).
- Não use títulos Markdown (#) nem tabelas dentro dos campos string. Use "\\n" para quebras de linha no JSON.
</formatacao>

<formato_esperado>
{{
  "lab": {{
    "titulo": "Título curto e chamativo do laboratório prático",
    "tecnologias": ["Terraform", "Docker"],
    "objetivo": "Frase clara explicando o que o aluno será capaz de executar/solucionar no final",
    "pre_requisitos": [
      "Ferramenta X instalada (versão Y)",
      "Acesso ao Docker Local / LocalStack"
    ],
    "ambiente_recomendado": "Local com Docker | LocalStack | GitHub Codespaces | Minikube",
    "desafios": [
      {{
        "nivel": "Nível 4 (Break/Fix)",
        "titulo_desafio": "Nome do Desafio de Diagnóstico",
        "cenario_e_enunciado": "Explicação do problema real e o contexto do erro.",
        "codigo_inicial_ou_incompleto": "Bloco de código ou manifesto YAML/HCL que contém o erro para o aluno copiar e testar",
        "instrucoes_de_execucao": "Passo a passo inicial para simular a falha (ex: execute `docker-compose up` e veja o erro X)",
        "dicas": [
          "Dica 1 (Vaga): Verifique a seção de rede no arquivo de configuração.",
          "Dica 2 (Direta): O container A está tentando acessar o container B usando localhost em vez do nome do serviço.",
          "Dica 3 (Quase a resposta): Altere `localhost:5432` para `postgres:5432` na variável `DATABASE_URL`."
        ],
        "criterio_de_sucesso": "Comando exato e saída esperada para provar que a correção funcionou.",
        "gabarito_comentado": "Código corrigido completo acompanhado de uma explicação técnica curta sobre a causa raiz."
      }},
      {{
        "nivel": "Nível 5 (Construa do Zero)",
        "titulo_desafio": "Nome do Desafio de Construção",
        "cenario_e_enunciado": "Requisitos da arquitetura/automação que deve ser criada do zero sem colar código.",
        "codigo_inicial_ou_incompleto": "",
        "instrucoes_de_execucao": "O que deve ser criado e quais contratos de interface/portas/nomes devem ser respeitados.",
        "dicas": [
          "Dica 1: Lembre-se do bloco de variáveis...",
          "Dica 2: Utilize a função X do Terraform para...",
          "Dica 3: A estrutura do manifesto exige..."
        ],
        "criterio_de_sucesso": "Como validar localmente a solução criada.",
        "gabarito_comentado": "Código de referência ideal e explicação das decisões de arquitetura empregadas."
      }}
    ]
  }}
}}
</formato_esperado>
{ja_existem}
<anotacoes_para_analise>
{readme_texto}
</anotacoes_para_analise>"""


def validar_lab(dados: dict) -> dict:
    """Garante a estrutura mínima do lab (ValueError faz o chamar_gemini tentar de novo)."""
    lab = dados.get("lab") if isinstance(dados, dict) else None
    if not isinstance(lab, dict) or not lab.get("titulo"):
        raise ValueError("JSON sem o objeto 'lab' com 'titulo'")

    desafios = [
        d for d in lab.get("desafios") or []
        if isinstance(d, dict) and all(d.get(k) for k in CAMPOS_DESAFIO)
    ]
    if not desafios:
        raise ValueError("Lab sem nenhum desafio completo")

    for d in desafios:
        d.setdefault("codigo_inicial_ou_incompleto", "")
        if isinstance(d["dicas"], str):
            d["dicas"] = [d["dicas"]]
    for campo in ("tecnologias", "pre_requisitos"):
        if not isinstance(lab.get(campo), list):
            lab[campo] = [lab[campo]] if lab.get(campo) else []
    lab.setdefault("objetivo", "")
    lab.setdefault("ambiente_recomendado", "")
    lab["desafios"] = desafios
    return {"lab": lab}


# ============================================================
# SAÍDA
# ============================================================
def carregar_labs(json_path: Path) -> list[dict]:
    if not json_path.is_file():
        return []
    try:
        return json.loads(json_path.read_text(encoding="utf-8")).get("labs", [])
    except (ValueError, AttributeError):
        print(f"   ⚠️  JSON inválido, ignorando: {json_path}")
        return []


def bloco_codigo(texto: str) -> str:
    """Se a IA mandou código cru (sem ```), embrulha para não quebrar o Markdown."""
    texto = texto.strip()
    return texto if texto.startswith("```") else f"```\n{texto}\n```"


def recolhivel(resumo: str, conteudo: str) -> list[str]:
    """<details> funciona tanto no GitHub quanto no Obsidian."""
    return ["<details>", f"<summary>{resumo}</summary>", "", conteudo.strip(), "", "</details>", ""]


def renderizar_markdown(nome: str, labs: list[dict]) -> str:
    linhas = [
        tag_do_modulo(nome).replace("#flashcards", OBSIDIAN_TAG, 1),
        "",
        f"# 🛠️ Labs – {titulo_do_modulo(nome)}",
        "",
        f"> Gerado por `estude-fazendo.py` a partir de `{nome.replace('__', '/')}`. "
        "Tente resolver sem abrir as dicas; abra uma de cada vez.",
        "",
    ]
    # Mais recente primeiro: é o que você ainda não fez
    for i, lab in reversed(list(enumerate(labs, 1))):
        linhas += [f"## Lab {i}: {lab['titulo']}", ""]
        if lab.get("gerado_em"):
            linhas += [f"_Gerado em {lab['gerado_em']}_", ""]
        linhas += [f"**🎯 Objetivo:** {lab['objetivo']}", ""]
        if lab["tecnologias"]:
            linhas += ["**🧰 Tecnologias:** " + ", ".join(f"`{t}`" for t in lab["tecnologias"]), ""]
        if lab["ambiente_recomendado"]:
            linhas += [f"**🖥️ Ambiente:** {lab['ambiente_recomendado']}", ""]
        if lab["pre_requisitos"]:
            linhas += ["**📋 Pré-requisitos:**", ""]
            linhas += [f"- [ ] {p}" for p in lab["pre_requisitos"]]
            linhas.append("")

        for d in lab["desafios"]:
            linhas += [
                f"### {d['nivel']} – {d['titulo_desafio']}",
                "",
                "**Cenário:**",
                "",
                d["cenario_e_enunciado"].strip(),
                "",
            ]
            if d["codigo_inicial_ou_incompleto"].strip():
                linhas += ["**Código inicial:**", "", bloco_codigo(d["codigo_inicial_ou_incompleto"]), ""]
            linhas += [
                "**Como executar:**",
                "",
                d["instrucoes_de_execucao"].strip(),
                "",
                "**✅ Critério de sucesso:**",
                "",
                d["criterio_de_sucesso"].strip(),
                "",
            ]
            for n, dica in enumerate(d["dicas"], 1):
                linhas += recolhivel(f"💡 Dica {n}", dica)
            linhas += recolhivel("🔑 Gabarito comentado", d["gabarito_comentado"])
            linhas += ["- [ ] Concluído", ""]

    return "\n".join(linhas)


def salvar_labs(nome: str, labs: list[dict], saida_dir: Path) -> Path:
    saida_dir.mkdir(parents=True, exist_ok=True)
    base = saida_dir / nome
    base.with_suffix(".json").write_text(
        json.dumps({"labs": labs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    md_path = base.with_suffix(".md")
    md_path.write_text(renderizar_markdown(nome, labs), encoding="utf-8")
    print(f"   💾 Salvo: {base.with_suffix('.json')} e {md_path}")
    return md_path


def exportar_obsidian(md_path: Path, vault: Path) -> None:
    """
    Copia a nota para o vault. Só sobrescreve se o conteúdo mudou; os checkboxes
    marcados no Obsidian são mantidos enquanto a nota não for regenerada.
    """
    destino = vault / OBSIDIAN_SUBDIR / md_path.name
    destino.parent.mkdir(parents=True, exist_ok=True)
    novo = md_path.read_text(encoding="utf-8")
    if destino.is_file():
        antigo = destino.read_text(encoding="utf-8")
        # Ignora diferenças só de checkbox marcado: é progresso, não conteúdo novo
        if antigo.replace("- [x]", "- [ ]") == novo:
            return
    shutil.copyfile(md_path, destino)
    print(f"   📓 Obsidian: {destino}")


def sincronizar_obsidian(saida_dir: Path, vault: Path) -> int:
    if not (vault / ".obsidian").is_dir():
        print(f"❌ {vault} não parece ser um vault do Obsidian (falta a pasta .obsidian).")
        return 1
    for md_path in sorted(saida_dir.glob("*.md")):
        exportar_obsidian(md_path, vault)
    return 0


# ============================================================
# MAIN
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(description="Gera laboratórios práticos dos READMEs alterados.")
    parser.add_argument("--repo", default=".", help="Raiz do repositório (padrão: .)")
    parser.add_argument("--base", default="HEAD~1", help="Commit base para o diff (padrão: HEAD~1)")
    parser.add_argument("--local", action="store_true", help="Usar git status (mudanças locais) em vez de diff")
    parser.add_argument("--output-dir", default="labs", help="Pasta de saída (padrão: labs)")
    parser.add_argument("--tema", default="", help="Tema/tecnologia para priorizar no lab")
    parser.add_argument(
        "--obsidian-dir",
        default=os.environ.get("OBSIDIAN_VAULT"),
        help=f"Vault do Obsidian para onde exportar os labs (padrão: $OBSIDIAN_VAULT ou ./{OBSIDIAN_VAULT_PADRAO})",
    )
    parser.add_argument(
        "--sync-obsidian",
        metavar="VAULT",
        help="Só copia os labs/*.md existentes para o vault e sai (não usa a API)",
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

    print("=" * 60)
    print(f"🛠️  GERADOR DE LABS PRÁTICOS (modelo: {GEMINI_MODEL})")
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
            labs = carregar_labs((saida_dir / m["nome"]).with_suffix(".json"))
            prompt = montar_prompt_lab(
                m["readme_texto"],
                bool(m["pdfs"]),
                [lab["titulo"] for lab in labs],
                args.tema,
            )
            resultado = chamar_gemini(
                prompt, m["pdfs"], api_key, validar=validar_lab, max_tokens=MAX_OUTPUT_TOKENS
            )
            lab = resultado["lab"]
            lab["gerado_em"] = date.today().isoformat()
            labs.append(lab)
            print(f"   ✓ Lab novo: {lab['titulo']} ({len(lab['desafios'])} desafio(s), {len(labs)} no total)")
            md_path = salvar_labs(m["nome"], labs, saida_dir)
            if vault:
                exportar_obsidian(md_path, vault)
        except Exception as e:  # noqa: BLE001
            falhas += 1
            print(f"   ❌ Falha em {m['nome']}: {e}")

    print("\n" + "=" * 60)
    print(f"Concluído: {len(modulos) - falhas}/{len(modulos)} pasta(s) com sucesso")
    print("=" * 60)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
