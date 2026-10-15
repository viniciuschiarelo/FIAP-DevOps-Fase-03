# Flashcards – 02-terraform__06-terraform-provider-kubernets

## 1. Terraform no ecossistema Kubernetes _(Iniciante)_

**Pergunta:** Qual é a principal vantagem de gerenciar recursos do Kubernetes (como Namespaces e Deployments) via Terraform em vez de aplicar manifests YAML manualmente com `kubectl apply`?

<details>
<summary>Ver resposta</summary>

Traz o ciclo de vida do Kubernetes para a **Infraestrutura como Código (IaC)**.
- **Rastreabilidade** do estado (tfstate)
- **Versionamento** e **code review**
- Menos **drift** entre ambientes

</details>

## 2. Kubernetes Provider vs Kubectl Provider _(Intermediário)_

**Pergunta:** Qual é a principal diferença de funcionamento e caso de uso entre o Kubernetes Provider e o Kubectl Provider no Terraform?

<details>
<summary>Ver resposta</summary>

A diferença está no **formato**: HCL nativo vs YAML bruto.
- **Kubernetes Provider** → objetos traduzidos para HCL; ideal para padronizar de forma declarativa, sem YAML
- **Kubectl Provider** → aceita YAML bruto via `kubectl_manifest` (saídas de Helm, arquivos legados), simulando o `kubectl apply`

</details>

## 3. Limitações do Kubernetes Provider _(Intermediário)_

**Pergunta:** Por que o Kubernetes Provider oficial do Terraform pode não ser suficiente para cobrir todos os cenários dentro de um cluster Kubernetes?

<details>
<summary>Ver resposta</summary>

Porque **nem todo recurso da API** (principalmente **CRDs**) tem um bloco HCL equivalente no provider.
- Nesses casos, complementa-se com o **Kubectl Provider** (YAML direto) ou com **Helm**

</details>

## 4. Gerenciamento de Secrets no Terraform _(Intermediário)_

**Pergunta:** Por que definir valores em texto puro ou em base64 diretamente no recurso `kubernetes_secret` é má prática em produção, e qual a solução recomendada?

<details>
<summary>Ver resposta</summary>

Porque **base64 é codificação, não criptografia**.
- O segredo fica exposto no **Git** e no **tfstate**
- Solução: integrar o Terraform a um cofre externo (**HashiCorp Vault**, **AWS Secrets Manager**) para injeção segura e credenciais dinâmicas

</details>

## 5. HashiCorp Vault e Credenciais Dinâmicas _(Avançado)_

**Pergunta:** Como a integração do Vault Provider com o Terraform aprimora a postura de segurança (zero-trust) na gestão de segredos?

<details>
<summary>Ver resposta</summary>

O Terraform pede ao Vault **credenciais dinâmicas e temporárias** em tempo de execução.
- Nada fica gravado estaticamente no repositório
- Credenciais **efêmeras** expiram sozinhas
- Menor superfície de ataque em caso de vazamento

</details>

## 6. RBAC via Terraform (Role vs ClusterRole) _(Intermediário)_

**Pergunta:** Ao provisionar RBAC via Terraform, qual a diferença de escopo entre `kubernetes_role`/`kubernetes_role_binding` e `kubernetes_cluster_role`/`kubernetes_cluster_role_binding`?

<details>
<summary>Ver resposta</summary>

A diferença é o **escopo**: um namespace ou o cluster inteiro.
- **Role / RoleBinding** → permissões restritas a **um namespace**
- **ClusterRole / ClusterRoleBinding** → valem no **cluster todo** e em recursos sem namespace (ex.: nodes)

</details>

## 7. Princípio do Menor Privilégio em RBAC _(Intermediário)_

**Pergunta:** Como o princípio do menor privilégio (least privilege) deve ser aplicado ao criar regras de RBAC no Terraform?

<details>
<summary>Ver resposta</summary>

Concedendo **só os verbos e recursos estritamente necessários**.
- Ex.: `get` e `list` em vez de `*` ou `delete`
- Restringir a recursos e grupos/usuários específicos
- Evita exclusões acidentais e acessos indevidos em clusters multi-tenant

</details>

## 8. Papel do Helm Provider no Terraform _(Intermediário)_

**Pergunta:** Quando é preferível utilizar o Helm Provider do Terraform em vez de declarar recursos individuais com o Kubernetes Provider?

<details>
<summary>Ver resposta</summary>

Para implantar **stacks complexas prontas** (Prometheus, Grafana, Istio...).
- Um **Helm Chart** já empacota dezenas de manifests interdependentes (Deployments, CRDs, RBAC, ConfigMaps)
- Tudo vira **poucas linhas** de IaC

</details>

## 9. Abordagem Híbrida: Terraform vs Ferramentas de GitOps/Helm _(Avançado)_

**Pergunta:** Em arquiteturas corporativas de grande escala, qual é a divisão de responsabilidades recomendada entre Terraform, Helm e ferramentas GitOps (ArgoCD/FluxCD)?

<details>
<summary>Ver resposta</summary>

Cada ferramenta cuida de **uma camada**:
- **Terraform** → infraestrutura base (VPCs, clusters, namespaces, quotas, RBAC básico)
- **Helm** → empacota aplicações e componentes complexos
- **ArgoCD/FluxCD** → entrega contínua, sincronizando o cluster com o Git

</details>

## 10. GitOps com ArgoCD vs Push Model do Terraform _(Avançado)_

**Pergunta:** Qual a mudança conceitual fundamental entre o modelo tradicional de deploy via Terraform/CI e o modelo GitOps adotado pelo ArgoCD?

<details>
<summary>Ver resposta</summary>

A mudança é de **push** para **pull**.
- **Terraform/CI (push)** → a pipeline externa envia comandos ao cluster
- **GitOps (pull)** → um agente **dentro do cluster** observa o Git (fonte única da verdade), aplica as mudanças e **corrige drifts** sozinho

</details>

## 11. Pipeline DevOps Moderna (Terraform + GitHub Actions + ArgoCD) _(Avançado)_

**Pergunta:** Como se conectam Terraform, GitHub Actions e ArgoCD em um pipeline completo de entrega contínua para Kubernetes?

<details>
<summary>Ver resposta</summary>

Cada um cuida de uma etapa do fluxo:
- **Terraform** → provisiona a infraestrutura do cluster
- **GitHub Actions** → CI: testes, validações, build da imagem e atualização dos manifests
- **ArgoCD** → detecta a mudança nos manifests e sincroniza a aplicação no cluster

</details>

## 12. Dependência Implícita no Kubernetes Provider _(Intermediário)_

**Pergunta:** Como o Terraform garante a ordem correta de provisionamento entre recursos dependentes do Kubernetes, como um Namespace e um Deployment?

<details>
<summary>Ver resposta</summary>

Por **dependência implícita**: ao referenciar um atributo de outro recurso, o Terraform liga os dois no grafo.
- O Namespace é criado **antes** do Deployment automaticamente
```hcl
namespace = kubernetes_namespace.demo.metadata[0].name
```

</details>

## 13. Detecção de Drift em Recursos Kubernetes _(Intermediário)_

**Pergunta:** Como o Terraform lida com alterações manuais feitas via CLI (ex.: `kubectl scale`) em um Deployment gerenciado por código?

<details>
<summary>Ver resposta</summary>

Ele detecta o **drift** e propõe **voltar ao valor do código**.
- No `terraform plan`/`apply`, consulta a API do Kubernetes
- Compara o estado real com o `tfstate`
- O plano reverte as réplicas para o valor do bloco HCL

</details>

## 14. Gerenciamento de ConfigMaps via IaC _(Iniciante)_

**Pergunta:** Qual a vantagem técnica de provisionar objetos como `kubernetes_config_map` via Terraform em vez de manifests isolados?

<details>
<summary>Ver resposta</summary>

Permite **parametrizar a config com outputs de outros recursos** da infraestrutura.
- Ex.: endpoint do banco de dados, tópicos de mensageria
- Ganha rastreabilidade e controle de versão
- Aplicação consistente entre ambientes

</details>

## 15. Autenticação do Kubernetes Provider em CI/CD _(Avançado)_

**Pergunta:** Por que usar `config_path = "~/.kube/config"` no Kubernetes Provider deve ser evitado em pipelines de CI/CD, e como deve ser feita a conexão?

<details>
<summary>Ver resposta</summary>

Porque ambientes **efêmeros** de CI/CD **não têm** o arquivo `~/.kube/config`.
- Alimente o provider com **dados do próprio provisionamento** do cluster: `host`, `cluster_ca_certificate`
- Use **tokens temporários** da autenticação nativa da nuvem ou OIDC

</details>
