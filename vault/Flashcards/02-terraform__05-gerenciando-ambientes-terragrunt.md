#flashcards/02-terraform/05-gerenciando-ambientes-terragrunt

# 🧠 Terraform › Gerenciando ambientes terragrunt

> [!info] 20 cards · 🟢 4 iniciante · 🟡 10 intermediário · 🔴 6 avançado
> Gerado por `anotacoes.py` a partir de `02-terraform/05-gerenciando-ambientes-terragrunt`. Edições feitas aqui são sobrescritas; o progresso de revisão é mantido.

## 🟢 Papel do Terragrunt no Ecossistema IaC

Qual é a relação do Terragrunt com o Terraform/OpenTofu e qual problema estrutural ele resolve?
?
O Terragrunt é uma **camada fina (wrapper)** sobre o Terraform/OpenTofu — ele não os substitui.
- Resolve a **duplicação de código** entre ambientes (`dev`, `staging`, `prod`) → princípio **DRY**
- Permite **herança hierárquica** de configurações
- Centraliza o **backend** e orquestra a execução dos módulos

## 🟡 Separação de Módulos e Ambientes Vivos (live)

Por que a arquitetura recomendada para Terragrunt separa o repositório entre os diretórios `modules/` e `live/`?
?
Para separar **o que é a infraestrutura** (código reutilizável) de **onde ela é aplicada** (ambientes).
- **`modules/`** → código Terraform puro, genérico e reaproveitável
- **`live/`** → configuração real de cada ambiente (`dev`, `prod`...)
- Os ambientes só **instanciam e parametrizam** os módulos via `terragrunt.hcl`, sem copiar infraestrutura inteira

## 🟡 Herança com find_in_parent_folders()

Como o Terragrunt implementa o princípio DRY para evitar repetição de configurações comuns nos ambientes?
?
Com o bloco **`include`** usando a função **`find_in_parent_folders()`**.
- O `terragrunt.hcl` da pasta filha **herda** as definições dos níveis acima
- Configurações globais (backend, providers) ficam **uma única vez** no `terragrunt.hcl` raiz
```hcl
include "root" {
  path = find_in_parent_folders()
}
```

## 🟡 Centralização de Remote State

Como o bloco `remote_state` do Terragrunt melhora o gerenciamento de estado em comparação ao Terraform puro?
?
O `remote_state` é declarado **uma única vez** no arquivo raiz e vale para todos os módulos.
- **Terraform puro** → cada módulo tem um bloco `backend` hardcoded ou copiado
- **Terragrunt** → a `key` do state é gerada dinamicamente por módulo
- Todos compartilham o mesmo bucket e lock table, de forma padronizada
```hcl
key = "${path_relative_to_include()}/terraform.tfstate"
```

## 🔴 Geração Dinâmica de Código (generate)

Qual é a utilidade do bloco `generate` no Terragrunt e qual problema ele soluciona?
?
O `generate` **cria arquivos `.tf` automaticamente** (ex.: `provider.tf`) antes de rodar o Terraform.
- Evita declarar o mesmo bloco `provider` em todos os módulos filhos
- Mantém versões e regiões **centralizadas** em um só lugar

## 🔴 Gerenciamento de Dependências (dependency)

Como o bloco `dependency` permite encadear módulos mantendo estados separados?
?
O módulo aponta para outro via **`config_path`** e consome os **outputs** dele como inputs.
- Ex.: `dependency.vpc.outputs.vpc_id` usado pelo módulo EKS
- Cada módulo (VPC, EKS) mantém seu **state isolado**
- Resultado: menor **raio de impacto** (blast radius) nas alterações

## 🔴 Mocks em Dependências (mock_outputs)

Por que o uso de `mock_outputs` é relevante em blocos `dependency` durante comandos de validação ou planejamento?
?
Porque um módulo que **ainda não foi criado não tem outputs reais** no state.
- Cenário típico: o primeiro `plan` de uma stack inteira
- `mock_outputs` injeta **valores provisórios**
- Assim `plan` e `validate` do módulo consumidor passam sem erro de dependência ausente

## 🟡 Orquestração em Cascata (run-all)

Qual é a diferença funcional entre os comandos `terragrunt apply` e `terragrunt run-all apply`?
?
A diferença é o **escopo**: um módulo só ou a árvore inteira.
- **`terragrunt apply`** → só o módulo do diretório atual
- **`terragrunt run-all apply`** → descobre **recursivamente** todos os módulos abaixo, monta o **grafo de dependências** e aplica na ordem correta

## 🟢 Interoperabilidade Terraform e OpenTofu

Como o Terragrunt possibilita alternar entre o Terraform e o OpenTofu sem a necessidade de reescrever módulos?
?
Pela variável **`terraform_binary`**, definida de forma centralizada no arquivo raiz.
- O Terragrunt redireciona as chamadas de CLI para o binário escolhido
- O código HCL dos módulos **não muda**
```hcl
terraform_binary = "tofu" # ou "terraform"
```

## 🔴 Resiliência e Retentativas de CLI

Como o Terragrunt previne falhas intermitentes causadas por concorrência de state lock ou limites de taxa de API?
?
Com **retentativas automáticas** configuradas no bloco `terraform`.
- **`retryable_errors`** → regex dos erros a capturar (ex.: `Error acquiring the state lock`)
- **`retry_max_attempts`** → quantas vezes tentar de novo
- **`retry_sleep_interval_sec`** → espera entre as tentativas

## 🟡 Versionamento de Módulos em Repositórios

Por que é considerado uma boa prática referenciar módulos externos usando Git tags no `terraform.source`?
?
Para garantir **imutabilidade**: o ambiente sempre usa a mesma versão do módulo.
- Ex.: URL Git com `?ref=v1.2.3`
- Evita mudanças inesperadas vindas de commits na branch principal
- Permite **promover versões gradualmente** (testa `v1.3.0` em `dev` antes de `prod`)

## 🟢 Automação em CI/CD

Qual parâmetro é mandatório ao executar comandos `run-all` do Terragrunt em pipelines de CI/CD não-assistidos e por quê?
?
A flag **`--terragrunt-non-interactive`**.
- Suprime os prompts de confirmação no terminal
- Sem ela, a pipeline **congela** esperando uma resposta humana

## 🟡 Função path_relative_to_include()

Qual é a função do helper `path_relative_to_include()` na configuração do remote state e qual problema operacional ele resolve?
?
Calcula o **caminho relativo** entre o `terragrunt.hcl` do módulo filho e o arquivo pai incluído.
- Gera automaticamente uma **`key` única** no S3 para cada módulo, baseada na árvore de diretórios
- Evita que dois módulos **sobrescrevam o mesmo tfstate**
- Elimina paths hardcoded

## 🟡 Função find_in_parent_folders()

Como a função `find_in_parent_folders()` viabiliza a herança hierárquica dentro de blocos `include` no Terragrunt?
?
Ela **sobe pelos diretórios ancestrais** até achar o primeiro arquivo com o nome informado (padrão: `terragrunt.hcl`).
- Módulos filhos importam configs da raiz e de níveis intermediários
- Sem caminhos absolutos → estrutura **desacoplada**

## 🟡 Injeção de variáveis via bloco inputs

Como o bloco `inputs` do Terragrunt difere da passagem tradicional de variáveis por arquivos `.tfvars` no Terraform puro?
?
O `inputs` aceita **qualquer expressão HCL**, não só valores fixos.
- Pode usar `locals`, outputs de `dependency` e funções de herança
- **`.tfvars`** → valores estáticos
- Na execução, o Terragrunt injeta os valores no Terraform (variáveis de ambiente `TF_VAR_*`)

## 🔴 Bloco extra_arguments

Para que serve o bloco `extra_arguments` na configuração do Terragrunt e qual é um caso de uso prático em projetos corporativos?
?
Ele **anexa flags automaticamente** a comandos específicos do Terraform/OpenTofu (`plan`, `apply`, `destroy`...).
- Caso prático: padronizar `-parallelism=10` para limitar a concorrência na API do provedor em pipelines

## 🟡 Ordem de destruição com terragrunt run-all destroy

Como o `terragrunt run-all destroy` determina a ordem de destruição dos módulos em comparação ao `run-all apply`?
?
Ele **inverte o grafo de dependências** (DAG).
- **`apply`** → da base para o topo (VPC → EKS)
- **`destroy`** → dependentes primeiro (EKS → VPC)
- Evita erros por tentar remover recursos ainda em uso

## 🟡 Padronização de diretórios multi-ambiente

Qual é a justificativa técnica para estruturar projetos no padrão `infra/<env>/<region>/<stack>/<módulo>` com Terragrunt?
?
**Isolar o blast radius**: state e execução ficam particionados por ambiente e região.
- A árvore de pastas espelha a infraestrutura real
- Permite **herança em cascata** das configurações
- Permite rodar comandos em um nível específico da árvore

## 🟢 terragrunt hclfmt

Qual é a finalidade do comando `terragrunt hclfmt` e como ele se integra às práticas de CI/CD?
?
Ele **formata recursivamente** todos os `terragrunt.hcl` no padrão canônico do HCL.
- Usado em hooks de **pre-commit** e etapas de **lint** na pipeline
- Garante legibilidade e consistência entre times

## 🔴 Segurança e Assume Role dinâmico

Como o bloco `generate` do Terragrunt é utilizado para implementar a prática segura de Assume Role em arquiteturas AWS multi-conta?
?
O `generate` cria o `provider.tf` com um bloco **`assume_role`** apontando para a role da conta do ambiente alvo.
- A ARN muda por ambiente (`dev`, `staging`, `prod`) via `locals` ou secrets do CI/CD
- Aplica o **menor privilégio** sem replicar código manualmente
