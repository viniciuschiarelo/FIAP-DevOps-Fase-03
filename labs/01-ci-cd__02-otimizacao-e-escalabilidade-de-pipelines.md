#labs/01-ci-cd/02-otimizacao-e-escalabilidade-de-pipelines

# 🛠️ Labs – Ci cd › Otimizacao e escalabilidade de pipelines

> Gerado por `estude-fazendo.py` a partir de `01-ci-cd/02-otimizacao-e-escalabilidade-de-pipelines`. Tente resolver sem abrir as dicas; abra uma de cada vez.

## Lab 1: Otimização, Paralelismo e Governança de Pipelines CI/CD com GitHub Actions

_Gerado em 2026-10-17_

**🎯 Objetivo:** Capacitar o engenheiro a orquestrar fluxos multi-stage desacoplados, aplicar estratégias de matriz com paralelismo resiliente e estruturar workflows reutilizáveis para governança em escala corporativa.

**🧰 Tecnologias:** `GitHub Actions`, `CI/CD`, `actionlint`, `Docker`

**🖥️ Ambiente:** Local com Git e actionlint ou GitHub Codespaces

**📋 Pré-requisitos:**

- [ ] Git instalado
- [ ] Docker instalado (para simulação via act, se desejado) ou ferramenta actionlint instalada (`brew install actionlint` ou `go install github.com/rhysd/actionlint/cmd/actionlint@latest`)
- [ ] Conhecimento de sintaxe YAML e ciclo de vida de CI/CD

### Nível 4 (Break/Fix) – Diagnóstico de Pipeline Multi-Stage com Matriz Quebrada e Corrida de Dependências

**Cenário:**

A equipe de engenharia tentou refatorar uma pipeline monolítica para um modelo multi-stage otimizado com matrix strategy. No entanto, ao disparar a pipeline, o linter de CI rejeita o arquivo e, ao forçar a execução, os jobs quebram simultaneamente: o job de testes falha por não encontrar o pacote de compilação gerado pelo job anterior, a matriz falha na resolução de variáveis e o estágio de deploy falha ao referenciar uma dependência inexistente.

Sua missão é inspecionar o arquivo `.github/workflows/pipeline-broken.yml`, identificar os três erros estruturais e restabelecer o encadeamento correto com upload/download de artefato.

**Código inicial:**

```yaml
name: Enterprise Multi-Stage CI

on:
  push:
    branches: [ main ]

jobs:
  compile:
    name: Build Application
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create Build Directory
        run: |
          mkdir dist
          echo 'console.log("App Built")' > dist/bundle.js
      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: app-dist
          path: dist/

  test:
    name: Test on Matrix
    runs-on: ubuntu-latest
    strategy:
      matrix:
        target-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - name: Download Build Artifact
        uses: actions/download-artifact@v4
        with:
          name: app-dist
          path: dist/
      - name: Run Tests
        run: |
          echo "Testing with Node ${{ matrix.node_version }}"
          test -f dist/bundle.js

  deploy:
    name: Deploy Package
    runs-on: ubuntu-latest
    needs: [ "Test on Matrix" ]
    steps:
      - name: Deploy
        run: echo "Deploy executado com sucesso"
```

**Como executar:**

1. Crie o diretório do projeto e o subdiretório `.github/workflows/`.
2. Salve o código quebrado no arquivo `.github/workflows/ci.yml`.
3. Execute a validação estática de schema com o comando `actionlint .github/workflows/ci.yml` e analise os erros apontados no terminal.
4. Caso utilize o `act` com Docker, execute `act push` para verificar o erro em tempo de execução.

**✅ Critério de sucesso:**

Ao rodar `actionlint .github/workflows/ci.yml`, a saída não deve conter nenhum erro (código de saída `0`). Ao simular com `act -j deploy --dryrun` (ou `act push`), todos os jobs `compile`, `test (18)`, `test (20)`, `test (22)` e `deploy` devem ser planejados na ordem correta.

<details>
<summary>💡 Dica 1</summary>

Dica 1 (Vaga): Observe as dependências declaradas entre os jobs (`needs`) e os nomes utilizados para referenciá-los.

</details>

<details>
<summary>💡 Dica 2</summary>

Dica 2 (Direta): A propriedade `needs` deve referenciar o identificador único do job (`job_id`), não o campo visual `name`. Além disso, o job `test` tenta baixar um artefato criado por `compile`, mas não aguarda sua finalização.

</details>

<details>
<summary>💡 Dica 3</summary>

Dica 3 (Quase a resposta): Adicione `needs: [compile]` no job `test`; altere `needs: [ "Test on Matrix" ]` para `needs: [test]` no job `deploy`; e corrija a variável da matriz no step de teste de `${{ matrix.node_version }}` para `${{ matrix.target-version }}`.

</details>

<details>
<summary>🔑 Gabarito comentado</summary>

```yaml
name: Enterprise Multi-Stage CI

on:
  push:
    branches: [ main ]

jobs:
  compile:
    name: Build Application
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create Build Directory
        run: |
          mkdir dist
          echo 'console.log("App Built")' > dist/bundle.js
      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: app-dist
          path: dist/

  test:
    name: Test on Matrix
    needs: [compile]
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        target-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - name: Download Build Artifact
        uses: actions/download-artifact@v4
        with:
          name: app-dist
          path: dist/
      - name: Run Tests
        run: |
          echo "Testing with Node ${{ matrix.target-version }}"
          test -f dist/bundle.js

  deploy:
    name: Deploy Package
    runs-on: ubuntu-latest
    needs: [test]
    steps:
      - name: Deploy
        run: echo "Deploy executado com sucesso"
```
Causa-raiz técnica: 1) O job `test` rodava concorrentemente a `compile` por ausência de `needs: [compile]`, gerando uma race condition no download do artefato; 2) No job `deploy`, `needs` referenciou a string de `name` ("Test on Matrix") em vez do ID escalar `test`, o que viola o schema declarativo do GitHub Actions; 3) A interpolação `${{ matrix.node_version }}` divergia da chave declarada `target-version` dentro de `strategy.matrix`.

</details>

- [ ] Concluído

### Nível 5 (Construa do Zero) – Construção de Plataforma de CI com Reusable Workflow e Estratégia de Cache

**Cenário:**

Como Engenheiro de DevOps atuando na fundação de Engenharia de Plataformas (Platform Engineering) da empresa, você recebeu a incumbência de padronizar a validação de todos os microsserviços Node.js.

Você deve criar uma solução baseada em Workflows Reutilizáveis (`workflow_call`) que garanta segurança, reaproveitamento e eficiência de execução.

Requisitos técnicos:
1. Workflow Central/Reutilizável em `.github/workflows/reusable-node-check.yml`:
   - Disparado exclusivamente por `workflow_call`.
   - Deve receber via `inputs` o parâmetro `node_version` (tipo `string`, obrigatório) e `run_audit` (tipo `boolean`, padrão `false`, opcional).
   - Deve receber via `secrets` o segredo `DEPLOY_TOKEN` (opcional: `required: false`).
   - Deve implementar cache nativo de dependências (`actions/cache@v4` ou cache integrado do `actions/setup-node@v4`).
   - Deve conter steps para compilar e, condicionalmente se `run_audit` for true, rodar uma etapa de auditoria de segurança.
2. Workflow Chamador (Caller) em `.github/workflows/main-pipeline.yml`:
   - Disparado em `push` na branch `main`.
   - Um job de teste que utilize `strategy.matrix` para chamar o workflow reutilizável em duas versões de Node (`18` e `20`), com controle `fail-fast: false` e paralelismo máximo `max-parallel: 2`.
   - Um job final de release que só roda após todos os jobs da matriz do workflow reutilizável concluírem com sucesso.

**Como executar:**

1. Crie a pasta `.github/workflows/` no seu repositório local.
2. Crie e preencha `.github/workflows/reusable-node-check.yml` contendo a especificação do `workflow_call`.
3. Crie e preencha `.github/workflows/main-pipeline.yml` invocando o workflow reutilizável local com a sintaxe `./.github/workflows/reusable-node-check.yml` e a matriz de versões.
4. Valide a conformidade da sintaxe e dos tipos dos workflows usando `actionlint .github/workflows/*.yml`.

**✅ Critério de sucesso:**

A execução do comando `actionlint .github/workflows/*.yml` deve retornar zero erros e avisos de linting. O arquivo do workflow chamador deve passar parâmetros tipados e respeitar os contratos de interface do workflow reutilizável.

<details>
<summary>💡 Dica 1</summary>

Dica 1: No workflow reutilizável, declare os blocos `inputs` e `secrets` sob o gatilho `on.workflow_call`. No step condicional, utilize a expressão `if: ${{ inputs.run_audit }}`.

</details>

<details>
<summary>💡 Dica 2</summary>

Dica 2: Um job de workflow chamador que invoca outro workflow deve usar a palavra-chave `uses: ./.github/workflows/nome-do-arquivo.yml` no nível do job (e não dentro de `steps`). A passagem de valores ocorre sob `with:` e segredos sob `secrets:`.

</details>

<details>
<summary>💡 Dica 3</summary>

Dica 3: Ao usar matriz em um job que chama um workflow reutilizável, combine `strategy.matrix` com `with: node_version: ${{ matrix.node }}`. O job final de entrega deve declarar `needs: [call-reusable-check]`.

</details>

<details>
<summary>🔑 Gabarito comentado</summary>

Implementação do Workflow Reutilizável (`.github/workflows/reusable-node-check.yml`):
```yaml
name: Reusable Node.js Verification

on:
  workflow_call:
    inputs:
      node_version:
        required: true
        type: string
      run_audit:
        required: false
        type: boolean
        default: false
    secrets:
      DEPLOY_TOKEN:
        required: false

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js with Native Cache
        uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node_version }}
          cache: 'npm'
      - name: Install Dependencies
        run: echo "npm ci simulado com cache de dependencias ativo"
      - name: Run Build
        run: echo "Compilando para Node.js ${{ inputs.node_version }}"
      - name: Security Audit Step
        if: ${{ inputs.run_audit }}
        run: echo "Executando npm audit de segurança..."
```

Implementação do Workflow Chamador (`.github/workflows/main-pipeline.yml`):
```yaml
name: Main Service Pipeline

on:
  push:
    branches: [ main ]

jobs:
  call-reusable-check:
    strategy:
      fail-fast: false
      max-parallel: 2
      matrix:
        node: ["18", "20"]
    uses: ./.github/workflows/reusable-node-check.yml
    with:
      node_version: ${{ matrix.node }}
      run_audit: true
    secrets:
      DEPLOY_TOKEN: ${{ secrets.ORGANIZATION_DEPLOY_TOKEN }}

  release:
    name: Production Gate
    needs: [call-reusable-check]
    runs-on: ubuntu-latest
    steps:
      - name: Notification
        run: echo "Todos os estagios de verificacao matriciais foram concluidos."
```
Decisões arquiteturais: A separação em `workflow_call` modulariza a governança corporativa, permitindo que alterações de segurança (como o step de audit) sejam controladas centralmente pela equipe de plataforma. A combinação de `strategy.matrix` com `uses` no chamador otimiza o tempo de execução através de paralelismo balanceado com `max-parallel: 2`, enquanto `fail-fast: false` assegura visibilidade diagnóstica completa mesmo se uma versão específica falhar.

</details>

- [ ] Concluído
