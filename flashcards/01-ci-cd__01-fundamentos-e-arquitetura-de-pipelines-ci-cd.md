# Flashcards – 01-ci-cd__01-fundamentos-e-arquitetura-de-pipelines-ci-cd

## 1. Continuous Delivery vs. Continuous Deployment _(Iniciante)_

**Pergunta:** Qual é a diferença fundamental entre Continuous Delivery e Continuous Deployment na fase de CD?

<details>
<summary>Ver resposta</summary>

A distinção central reside no nível de automação e na presença de intervenção humana no **gatilho de liberação em produção**.
- **Continuous Delivery** → o artefato é testado e mantido sempre pronto para produção, mas o deploy final exige aprovação manual.
- **Continuous Deployment** → todas as alterações aprovadas na pipeline são implantadas automaticamente em produção sem intervenção humana.
- **Tomada de decisão** → Continuous Delivery é comum em setores regulamentados para compliance, enquanto Continuous Deployment maximiza agilidade.

</details>

## 2. Pipeline as Code (PaC) _(Iniciante)_

**Pergunta:** O que caracteriza a prática de Pipeline as Code (PaC) e quais benefícios ela traz para a equipe?

<details>
<summary>Ver resposta</summary>

Consiste em declarar e manter a lógica das pipelines de automação por meio de **arquivos de configuração versionados** no repositório.
- **Princípios de software** → permite versionamento, rastreabilidade, auditoria e revisão por pull requests dos fluxos de entrega.
- **Eliminação de silos** → substitui configurações manuais em interfaces gráficas por definições legíveis e padronizadas.
- **Exemplo** → workflows definidos em YAML em ferramentas como GitHub Actions sob a pasta `.github/workflows/`.

</details>

## 3. GitHub Actions: Jobs e Paralelismo _(Intermediário)_

**Pergunta:** Como o GitHub Actions organiza a execução de jobs concorrentes e dependências sequenciais?

<details>
<summary>Ver resposta</summary>

Por padrão, múltiplos jobs executam em **paralelo em runners isolados**, a menos que haja dependência explícita via `needs`.
- **Execução paralela** → jobs independentes rodam ao mesmo tempo para reduzir o tempo total da pipeline.
- **Execução sequencial** → o atributo `needs` define pré-requisitos lógicos para que um job aguarde a conclusão de outro.
- **Tratamento de erro** → se um job declarado em `needs` falhar, os jobs dependentes são ignorados por padrão.

</details>

## 4. GitHub Actions: Reusable Workflows vs Composite Actions _(Avançado)_

**Pergunta:** Qual a diferença entre Reusable Workflows e Composite Actions no GitHub Actions?

<details>
<summary>Ver resposta</summary>

Eles se diferenciam pelo escopo de execução e pela forma como lidam com **jobs, runners e segredos**.
- **Reusable Workflows** → reutilizam workflows completos com múltiplos jobs e runners próprios, além de consumirem `secrets` do repositório.
- **Composite Actions** → combinam múltiplos steps reutilizáveis dentro do contexto de um único job existente.
- **Acesso a credenciais** → Composite Actions não acessam segredos globais nativamente, exigindo passagem explícita por parâmetros de entrada.

</details>

## 5. DevSecOps: Shift-Left Security _(Intermediário)_

**Pergunta:** Como os mecanismos SAST, DAST e SCA implementam o conceito de Shift-Left em pipelines de CI/CD?

<details>
<summary>Ver resposta</summary>

Eles antecipam a detecção de riscos integrando verificações de segurança nas **etapas iniciais do ciclo de desenvolvimento**.
- **SAST** → análise de caixa branca que examina o código-fonte em busca de falhas antes mesmo da compilação.
- **SCA** → verificação automatizada que identifica vulnerabilidades e licenças irregulares em dependências externas de terceiros.
- **DAST** → análise de caixa preta executada em tempo de execução para simular ataques externos contra a aplicação ativa.

</details>

## 6. Jenkins: Arquitetura Master/Agent _(Intermediário)_

**Pergunta:** Como a arquitetura Master/Agent (Controller/Agent) do Jenkins viabiliza a distribuição e escala de pipelines?

<details>
<summary>Ver resposta</summary>

A arquitetura separa a inteligência de gerenciamento da **execução física das tarefas de build**.
- **Jenkins Master** → orquestrador central encarregado de agendar jobs, registrar logs e monitorar o status das execuções.
- **Jenkins Agent** → nós operacionais (VMs ou pods Kubernetes) que recebem e executam as instruções de trabalho do Master.
- **Escalabilidade horizontal** → permite distribuir cargas pesadas e provisionar nós sob demanda com diferentes ambientes operacionais.

</details>

## 7. Jenkins vs. GitHub Actions _(Intermediário)_

**Pergunta:** Quais critérios arquiteturais guiam a escolha estratégica entre Jenkins e GitHub Actions?

<details>
<summary>Ver resposta</summary>

A decisão é orientada pelo dilema técnico entre **controle granular da infraestrutura vs. conveniência e agilidade SaaS**.
- **Jenkins** → indicado para redes isoladas (air-gapped), infraestruturas legadas e demandas que exigem controle total de servidores e plugins.
- **GitHub Actions** → indicado para arquiteturas nativas da nuvem, configuração simplificada em YAML e redução de sobrecarga operacional.
- **Custo operacional** → o Jenkins elimina licença mas exige sustentação de hosts, enquanto o GitHub Actions adota cobrança sob demanda.

</details>

## 8. Estratégias de Deploy: Rolling Update vs Blue/Green vs Canary _(Intermediário)_

**Pergunta:** Qual a diferença de comportamento entre as estratégias de implantação Rolling Update, Blue/Green e Canary?

<details>
<summary>Ver resposta</summary>

Cada estratégia estabelece um equilíbrio diferente entre **custo de infraestrutura, risco de falha e tempo de reversão**.
- **Rolling Update** → substitui gradativamente as instâncias da versão antiga pela nova sem exigir infraestrutura extra duplicada.
- **Blue/Green** → mantém dois ambientes completos idênticos e chaveia o tráfego de uma só vez, viabilizando rollback instantâneo.
- **Canary** → expõe a nova versão a um percentual mínimo de usuários para monitorar métricas antes de propagar para 100% da base.

</details>

## 9. GitOps _(Avançado)_

**Pergunta:** Por que o GitOps é definido como um modelo declarativo de entrega contínua baseado em conciliação?

<details>
<summary>Ver resposta</summary>

Porque utiliza o repositório Git como a **única fonte da verdade** para determinar o estado desejado da aplicação.
- **Abordagem declarativa** → o estado pretendido da infraestrutura ou do Kubernetes é versionado em manifestos no Git.
- **Operador contínuo** → agentes no cluster comparam continuamente o estado atual em produção com o estado declarado no repositório.
- **Auto-reconciliação** → divergências causadas por alterações manuais não autorizadas são sobrescritas para refletir estritamente o Git.

</details>

## 10. GitOps: Argo CD vs Flux _(Avançado)_

**Pergunta:** Como Argo CD e Flux se comparam como soluções GitOps dentro do ecossistema CNCF?

<details>
<summary>Ver resposta</summary>

Ambos executam reconciliação declarativa, mas diferem no foco de **interface de operação e pegada arquitetural**.
- **Argo CD** → disponibiliza UI rica para visualização e gerenciamento simplificado de múltiplos clusters, ideal para grandes times.
- **Flux** → adota arquitetura modular minimalista com foco prioritário em CLI e APIs do Kubernetes, ideal para ambientes headless e air-gapped.
- **Avanços de deploy** → ambos suportam estratégias de entrega progressiva como Canary e Blue/Green em microsserviços.

</details>

## 11. Observabilidade em CI/CD _(Intermediário)_

**Pergunta:** Qual o valor da observabilidade em pipelines de CI/CD em relação ao monitoramento tradicional?

<details>
<summary>Ver resposta</summary>

A observabilidade busca esclarecer o **motivo de comportamentos e gargalos internos**, superando o simples alerta binário de falha.
- **Tríade de dados** → unifica logs, métricas de execução e traces distribuídos para auditar desde o commit até o deploy.
- **Flaky tests** → auxilia na identificação de testes instáveis que falham de maneira inconsistente sem causa funcional clara.
- **Decisão técnica** → utiliza dados históricos para redimensionar runners, mitigar gargalos de build e aprimorar fluxos de trabalho.

</details>

## 12. Platform Engineering _(Avançado)_

**Pergunta:** De que forma a Engenharia de Plataformas atua como a próxima evolução do DevOps para times de software?

<details>
<summary>Ver resposta</summary>

Construindo **portais internos de autoatendimento (Internal Developer Platforms - IDPs)** para abstrair a infraestrutura dos desenvolvedores.
- **Redução de carga cognitiva** → dispensa equipes de produto da manutenção complexa de toolchains de CI/CD e configurações cloud.
- **Golden Paths** → cria caminhos estruturados e pré-aprovados que aplicam governança, segurança e conformidade automaticamente.
- **Infraestrutura como produto** → transforma o DevOps de prática dispersa para um produto interno focado em experiência de desenvolvimento.

</details>
