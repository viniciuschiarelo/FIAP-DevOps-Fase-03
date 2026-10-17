# Flashcards – 01-ci-cd__02-otimizacao-e-escalabilidade-de-pipelines

## 1. Pipeline Multi-Stage _(Iniciante)_

**Pergunta:** Qual é o papel da instrução `needs` na estruturação de pipelines multi-stage no GitHub Actions?

<details>
<summary>Ver resposta</summary>

O campo `needs` estabelece uma **dependência sequencial explícita** entre jobs no fluxo de trabalho.
- Cria portões de validação que impedem a execução de etapas posteriores caso a fase anterior falhe.
- Permite que etapas independentes executem em paralelo por padrão até que um bloqueio seja declarado.
- Evita desperdício de recursos computacionais ao impedir builds e deploys de código quebrado.

</details>

## 2. Matrix Strategy _(Intermediário)_

**Pergunta:** Como a `matrix strategy` otimiza o tempo e o esforço de teste em pipelines de CI/CD?

<details>
<summary>Ver resposta</summary>

A estratégia gera **múltiplos jobs paralelos** a partir de uma única definição combinatória de variáveis.
- Elimina duplicações de código ao testar combinações de versões de runtimes e sistemas operacionais.
- Acelera o tempo de feedback executando as matrizes de teste simultaneamente.
- É declarada no bloco `strategy.matrix` informando listas para cada parâmetro desejado.

</details>

## 3. Matrix Strategy (fail-fast) _(Intermediário)_

**Pergunta:** Qual é o comportamento do parâmetro `fail-fast` na matrix strategy e quando desativá-lo?

<details>
<summary>Ver resposta</summary>

O parâmetro controla o **cancelamento automático** de todos os jobs irmãos da matriz caso um deles falhe.
- **Padrão (`fail-fast: true`)** → Cancela imediatamente os demais jobs em andamento para poupar recursos e custos.
- **Desativado (`fail-fast: false`)** → Garante que todas as variações executem até o fim independentemente de falhas individuais.
- Deve ser desativado quando é necessário obter a matriz de diagnóstico completa sobre quais ambientes quebraram.

</details>

## 4. Matrix Strategy (include e exclude) _(Intermediário)_

**Pergunta:** Como as diretivas `include` e `exclude` refinam o conjunto de execuções gerado pela matriz?

<details>
<summary>Ver resposta</summary>

Elas servem para **filtrar incompatibilidades ou injetar combinações** específicas no produto cartesiano da matriz.
- **`exclude`** → Remove combinações pontuais indesejadas ou incompatíveis da matriz original.
- **`include`** → Adiciona novas configurações customizadas ou variáveis adicionais a combinações existentes.

</details>

## 5. Matriz Dinâmica (fromJSON) _(Avançado)_

**Pergunta:** Em quais cenários e como a função `fromJSON()` viabiliza uma matriz dinâmica no GitHub Actions?

<details>
<summary>Ver resposta</summary>

A função `fromJSON()` viabiliza matrizes dinâmicas **convertendo strings JSON geradas em tempo de execução** em matrizes de jobs.
- Muito utilizada em monorepos para evitar a execução de testes em serviços que não sofreram alterações.
- Um job prévio analisa o diff do pull request e emite uma lista formatada em JSON como output.
- O job seguinte consome esse output dinamicamente via `matrix: ${{ fromJSON(needs.job_previo.outputs.matrix) }}`.

</details>

## 6. Workflows Reutilizáveis _(Intermediário)_

**Pergunta:** O que caracteriza um workflow reutilizável e qual gatilho viabiliza seu consumo por outros repositórios?

<details>
<summary>Ver resposta</summary>

Um workflow reutilizável atua como um **template centralizado de automação** ativado pelo gatilho `on: workflow_call`.
- Recebe entradas parametrizadas através da chave `inputs` e credenciais seguras via `secrets`.
- Permite que múltiplos repositórios (chamadores ou callers) consumam o mesmo padrão operacional.
- Centraliza correções e melhorias, aplicando-as automaticamente a todos os pipelines que o invocam.

</details>

## 7. Workflows Reutilizáveis vs Composite Actions _(Avançado)_

**Pergunta:** Qual a diferença de escopo, permissões e visibilidade entre Workflows Reutilizáveis e Composite Actions?

<details>
<summary>Ver resposta</summary>

A distinção baseia-se no **nível de abstração e capacidade de isolamento** dentro do ecossistema do GitHub Actions.
- **Workflows Reutilizáveis** → Reutilizam múltiplos jobs completos, suportam passagem nativa de secrets e exibem logs detalhados e independentes.
- **Composite Actions** → Reutilizam apenas steps dentro de um único job, não acessam secrets diretamente e agrupam todos os logs em uma única visualização.

</details>

## 8. Governança e Segurança em Workflows _(Avançado)_

**Pergunta:** Por que a boa prática de segurança recomenda fixar workflows reutilizáveis via commit SHA em vez de tags ou branches?

<details>
<summary>Ver resposta</summary>

A fixação por commit SHA assegura a **imutabilidade estrita do código executado**, blindando a cadeia de suprimentos.
- Tags e branches são ponteiros mutáveis que podem ser sobrescritos acidental ou maliciosamente.
- Garante conformidade ao impedir que alterações não auditadas entrem automaticamente na pipeline chamadora.
- Cumpre os requisitos de auditoria e estabilidade exigidos em ambientes regulados.

</details>

## 9. GitHub-hosted vs Self-hosted Runners _(Intermediário)_

**Pergunta:** Quais são as principais vantagens financeiras e de rede que justificam a adoção de self-hosted runners?

<details>
<summary>Ver resposta</summary>

Eles oferecem **isenção de minutos tarifados e integração com redes privadas**, compensando o esforço de gestão.
- **Custo** → Os minutos de execução em repositórios privados não são cobrados pelo GitHub.
- **Segurança e Rede** → Executam dentro de VPCs privadas, herdando papéis como IAM Roles sem expor credenciais de nuvem para a internet.
- **Controle** → Permitem uso de imagens hardened e hardware customizado conforme exigências da organização.

</details>

## 10. Segurança de Self-hosted Runners _(Intermediário)_

**Pergunta:** Por que o GitHub desencoraja categoricamente o uso de self-hosted runners em repositórios públicos?

<details>
<summary>Ver resposta</summary>

A prática expõe a infraestrutura corporativa ao **risco de execução arbitrária de código** vindo de pull requests externos.
- Qualquer usuário externo pode abrir um pull request contendo scripts maliciosos para rodar no servidor.
- Cria vetores diretos para invasão da rede privada, roubo de metadados de nuvem e movimentação lateral.
- Para projetos de código aberto, o padrão seguro obrigatório é a utilização de GitHub-hosted runners.

</details>

## 11. Actions Runner Controller (ARC) _(Avançado)_

**Pergunta:** Qual problema operacional o Actions Runner Controller (ARC) resolve no gerenciamento de runners?

<details>
<summary>Ver resposta</summary>

O ARC implementa o **escalonamento dinâmico de runners efêmeros** provisionados em clusters Kubernetes.
- Provisiona pods de runners sob demanda acompanhando a métrica da fila de jobs do GitHub.
- Destrói os runners automaticamente após a conclusão de cada job, garantindo um ambiente limpo e isolado.
- Elimina a sobrecarga de manutenção estática de máquinas virtuais dedicadas ociosas.

</details>

## 12. Cache vs Artifacts _(Intermediário)_

**Pergunta:** Qual a diferença fundamental entre o gerenciamento de artefatos (artifacts) e o cache de dependências em pipelines?

<details>
<summary>Ver resposta</summary>

A diferença reside na **finalidade e no ciclo de reaproveitamento** dos arquivos gerados.
- **Cache de dependências** → Armazena pacotes externos imutáveis (ex: `npm`, `pip`, `Maven`) para reutilização entre diferentes execuções da pipeline.
- **Artefatos (artifacts)** → Armazenam os binários finais gerados pelo build (ex: `.jar`, relatórios) para transferi-los entre jobs ou disponibilizá-los após o término.

</details>

## 13. Engenharia de Plataformas _(Avançado)_

**Pergunta:** Como os workflows reutilizáveis viabilizam a criação de uma Plataforma Interna de Desenvolvedores (IDP)?

<details>
<summary>Ver resposta</summary>

Eles transformam regras de automação em **produtos internos consumíveis em autoatendimento** pelos desenvolvedores.
- Padronizam etapas críticas de build, análise estática de código e deploy sem gerar sobrecarga cognitiva aos times de negócio.
- Permitem que o time central de plataforma atualize diretrizes de compliance sem exigir mudanças manuais nos repositórios clientes.
- Movem a equipe de DevOps de uma função de suporte reativo para uma postura de engenharia habilitadora.

</details>
