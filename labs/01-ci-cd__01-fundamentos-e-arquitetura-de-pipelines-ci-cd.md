#labs/01-ci-cd/01-fundamentos-e-arquitetura-de-pipelines-ci-cd

# 🛠️ Labs – Ci cd › Fundamentos e arquitetura de pipelines ci cd

> Gerado por `estude-fazendo.py` a partir de `01-ci-cd/01-fundamentos-e-arquitetura-de-pipelines-ci-cd`. Tente resolver sem abrir as dicas; abra uma de cada vez.

## Lab 1: Implementação e Troubleshooting de Pipelines CI/CD com GitHub Actions

_Gerado em 2026-10-17_

**🎯 Objetivo:** Capacitar o aluno a diagnosticar e corrigir falhas sintáticas e de dependência em pipelines declarativos, além de construir uma esteira automatizada completa de CI/CD com paralelismo, portões de qualidade (Shift-Left) e deploy condicional.

**🧰 Tecnologias:** `GitHub Actions`, `Docker`, `Git`, `act`, `YAML`

**🖥️ Ambiente:** Local com Docker e act CLI (ou repositório privado no GitHub / GitHub Codespaces)

**📋 Pré-requisitos:**

- [ ] Git instalado (versão 2.30+)
- [ ] Docker instalado e em execução (versão 20.10+)
- [ ] Ferramenta act instalada para execução local de workflows (ou acesso direto ao GitHub)

### Nível 4 (Break/Fix) – Diagnóstico de Dependências Inexistentes e Colisão de Chaves em Workflow

**Cenário:**

A equipe de engenharia tentou padronizar uma esteira de integração contínua (CI) em um repositório interno. No entanto, após o commit do arquivo `.github/workflows/ci.yml`, a pipeline sequer é aceita pelo motor de execução, acusando falhas estruturais de schema e dependências de jobs inválidas. Analise o arquivo quebrado, identifique as causas raízes e corrija o manifesto para que a pipeline execute com sucesso em paralelo e em sequência conforme o desenho pretendido.

**Código inicial:**

```
name: CI Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  code-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Run Linter
        run: echo "Linting code repository..."

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Run SAST Scanner
        run: echo "Analyzing code security (Shift Left)..."

  build-and-test:
    needs: [lint, security]
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Compile and Test Artifact
        run: echo "Compiling application and executing unit tests..."
        uses: actions/setup-node@v4
        with:
          node-version: 18
```

**Como executar:**

1. Crie uma pasta para o projeto e inicialize o git com `git init`.
2. Crie o diretório `.github/workflows/` e salve o código inicial em `.github/workflows/ci.yml`.
3. Execute a validação local com a ferramenta `act` rodando o comando `act --dryrun` ou `act -l`.
4. Observe os erros de schema e de referência acusados pelo interpretador do workflow.

**✅ Critério de sucesso:**

Ao executar `act -l`, todos os 3 jobs (`code-lint`, `security-scan` e `build-and-test`) devem ser listados sem erros de parser. Ao rodar `act -j build-and-test` (ou subir para o GitHub), os jobs anteriores devem executar em paralelo e o job final deve concluir com exit code 0.

<details>
<summary>💡 Dica 1</summary>

Dica 1 (Vaga): Verifique se os identificadores fornecidos na diretiva `needs` correspondem exatamente aos IDs dos jobs declarados no arquivo.

</details>

<details>
<summary>💡 Dica 2</summary>

Dica 2 (Direta): Na especificação do GitHub Actions, um mesmo item da lista `steps` não pode ter simultaneamente as instruções `run` e `uses`.

</details>

<details>
<summary>💡 Dica 3</summary>

Dica 3 (Quase a resposta): No job `build-and-test`, altere o `needs` para `[code-lint, security-scan]` e separe o step `Compile and Test Artifact` em dois steps individuais: um para `uses: actions/setup-node@v4` e outro subsequente para `run: echo ...`.

</details>

<details>
<summary>🔑 Gabarito comentado</summary>

```yaml
name: CI Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  code-lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Run Linter
        run: echo "Linting code repository..."

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Run SAST Scanner
        run: echo "Analyzing code security (Shift Left)..."

  build-and-test:
    needs: [code-lint, security-scan]
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Setup Node Runtime
        uses: actions/setup-node@v4
        with:
          node-version: 18
      - name: Compile and Test Artifact
        run: echo "Compiling application and executing unit tests..."
```
Causa raiz: No GitHub Actions, `needs` referencia o ID do job (a chave do dicionário no YAML) e não o rótulo descritivo. Além disso, cada step precisa ser exclusivo: ou invoca uma Action externa via `uses` ou roda comandos de terminal via `run`, nunca ambos no mesmo bloco.

</details>

- [ ] Concluído

### Nível 5 (Construa do Zero) – Construção de Esteira Completa de CI/CD com Gate de Segurança e Build Docker

**Cenário:**

Você deve projetar e implementar do zero uma esteira corporativa completa de CI/CD para uma aplicação web empacotada em container Docker, aplicando os conceitos de Pipeline as Code e DevSecOps apresentados na aula.
A esteira deve atender aos seguintes requisitos arquiteturais:
1. Gatilhos: Executar automaticamente em eventos de `push` e `pull_request` apontando para a branch `main`.
2. Estágio de Validação (CI / Shift-Left): Dois jobs executando em paralelo: `sast-sca-scan` (simulando análise estática de segurança e dependências) e `unit-tests` (simulando bateria de testes automatizados).
3. Estágio de Build (Empacotamento): Um job chamado `docker-build` que só inicia se os dois jobs do estágio de validação terminarem com sucesso (`needs`). Este job deve construir uma imagem Docker local usando a tag referenciando o hash curto do commit (`${{ github.sha }}`).
4. Estágio de Implantação (Continuous Delivery): Um job chamado `deploy-staging` que depende do sucesso de `docker-build`. Este job deve possuir uma guarda condicional (`if`) para que execute estritamente em eventos de `push` na branch `main` (não deve rodar em Pull Requests), simulando a publicação da imagem em staging.

**Como executar:**

1. Crie um arquivo `Dockerfile` simples na raiz contendo apenas:
`FROM alpine:3.19`
`CMD ["echo", "Container operacional"]`
2. Crie a estrutura de diretórios `.github/workflows/` e desenvolva o arquivo `.github/workflows/delivery-pipeline.yml`.
3. Configure todos os estágios, jobs, dependências com `needs`, checkout de código e condições de execução conforme os requisitos.
4. Valide a sintaxe e a ordem de execução localmente com o comando `act` ou via push em branch de teste no GitHub.

**✅ Critério de sucesso:**

Executar localmente `act pull_request` e verificar que os jobs `sast-sca-scan`, `unit-tests` e `docker-build` executam com sucesso, enquanto o job `deploy-staging` é ignorado/pulado. Ao executar `act push`, todos os 4 jobs devem executar com sucesso até a mensagem final de deploy com status exit 0.

<details>
<summary>💡 Dica 1</summary>

Dica 1: Para rodar jobs em paralelo, basta declará-los no mesmo nível dentro de `jobs:` sem a instrução `needs`. Para criar a dependência de bloqueio, use `needs: [job1, job2]`.

</details>

<details>
<summary>💡 Dica 2</summary>

Dica 2: Para o build da imagem Docker, você pode utilizar a action oficial `docker/build-push-action@v5` ou simplesmente executar um step com comando `docker build -t minha-app:${{ github.sha }} .`.

</details>

<details>
<summary>💡 Dica 3</summary>

Dica 3: Para a condição no job de deploy, use a cláusula `if: github.event_name == 'push' && github.ref == 'refs/heads/main'` logo abaixo da definição de `runs-on` ou `needs`.

</details>

<details>
<summary>🔑 Gabarito comentado</summary>

```yaml
name: Delivery Pipeline

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  sast-sca-scan:
    name: Security and Dependency Analysis
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: SAST Code Analysis
        run: echo "[INFO] Executing Static Application Security Testing... OK"
      - name: SCA Dependency Audit
        run: echo "[INFO] Checking dependencies for known CVEs... OK"

  unit-tests:
    name: Automated Unit Testing
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Run Test Suites
        run: echo "[INFO] Running unit tests and code coverage... 100% Passed"

  docker-build:
    name: Build Docker Container
    needs: [sast-sca-scan, unit-tests]
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Build Application Image
        run: |
          docker build -t my-app:${{ github.sha }} .
          docker images | grep my-app

  deploy-staging:
    name: Deliver to Staging Environment
    needs: [docker-build]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Continuous Delivery Trigger
        run: |
          echo "[DEPLOY] Deploying artifact tag my-app:${{ github.sha }} to staging cluster..."
          echo "[STATUS] Reconciled and active."
```
Decisões de Arquitetura: Os jobs de segurança e testes rodam em paralelo na fase de CI para garantir feedback rápido sem onerar o tempo total do runner (abordagem Shift Left). O estágio de build atua como um gate bloqueante através do `needs`, garantindo que artefatos só sejam gerados a partir de código aprovado. A condicional `if: github.event_name == 'push'` no estágio de CD impede que testes de pull requests gerem deploys indevidos, viabilizando Continuous Delivery seguro.

</details>

- [ ] Concluído
