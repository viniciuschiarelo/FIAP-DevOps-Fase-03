# 1. Fundamentos e Arquitetura de Pipelines de CI/CD

## O que é CI/CD?

CI/CD é uma forma de automatizar o caminho entre desenvolver uma aplicação e entregar essa aplicação em produção.

A ideia principal é: quanto mais etapas repetitivas forem automatizadas, menor a chance de erro humano e mais rápido o time consegue entregar valor.

Em DevOps, isso não é só uma vantagem. É quase uma necessidade, porque sistemas modernos mudam o tempo todo e precisam ser entregues com segurança.

## CI - Continuous Integration

CI significa integração contínua.

É a parte do processo em que o código é construído e validado automaticamente.

Normalmente envolve:

- baixar o código do repositório;
- instalar dependências;
- fazer o build da aplicação;
- rodar testes;
- executar análise de qualidade;
- verificar se a aplicação continua funcionando depois da alteração.

Pensando de forma simples: CI é como uma conferência automática feita toda vez que alguém mexe no código.

Antes de aceitar a mudança como confiável, a pipeline pergunta:

- o projeto ainda compila?
- os testes continuam passando?
- a qualidade mínima foi mantida?
- essa alteração quebrou alguma coisa importante?

## CD - Continuous Delivery ou Continuous Deployment

CD é a etapa de entrega da aplicação.

Depois que a aplicação passa pela CI, ela pode ser preparada para ser publicada em algum ambiente, como homologação ou produção.

Essa etapa pode envolver:

- gerar uma release;
- criar ou publicar uma imagem de container;
- fazer deploy;
- monitorar a aplicação;
- operar a infraestrutura;
- exigir uma aprovação manual antes de publicar em produção.

Na prática, muitas empresas usam CD de forma semiautomatizada. A pipeline faz quase tudo, mas uma pessoa precisa aprovar o deploy final.

## Diferença entre CI e CD

CI responde à pergunta:

> O código está correto o suficiente para ser integrado?

CD responde à pergunta:

> Essa versão validada está pronta para ser entregue em algum ambiente?

## Ferramentas podem mudar, mas o fluxo é parecido

As ferramentas podem variar: GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Argo CD, Flux, AWS, Kubernetes e outras.

Mesmo assim, o raciocínio costuma ser o mesmo:

1. alguém altera o código;
2. a alteração entra no repositório;
3. uma pipeline é acionada;
4. a aplicação é construída;
5. testes e validações são executados;
6. um artefato é gerado;
7. esse artefato é entregue em algum ambiente.

## Estrutura básica de um workflow YAML

Em ferramentas como GitHub Actions, a pipeline costuma ser descrita em um arquivo YAML.

Esse arquivo define quando a pipeline executa e quais passos ela precisa seguir.

Uma estrutura comum possui:

1. metadados do workflow: nome e informações gerais;
2. triggers: quando a pipeline deve executar;
3. variáveis globais: valores reutilizados durante o workflow;
4. jobs: blocos principais de trabalho;
5. steps: ações executadas dentro de cada job.

## Triggers

Triggers são os gatilhos da pipeline.

Eles definem quando o workflow deve rodar.

Exemplos:

- quando alguém faz push;
- quando alguém abre um pull request;
- quando uma branch específica recebe alteração;
- quando arquivos específicos são modificados;
- manualmente, quando alguém clica para executar.

Depois que o YAML é criado e enviado para o GitHub, o GitHub Actions começa a executar o workflow sempre que os gatilhos configurados forem ativados.

## Variáveis e secrets

Variáveis servem para guardar valores reutilizáveis no workflow.

Exemplo:

- nome da aplicação;
- região da cloud;
- versão do runtime;
- caminho de algum arquivo.

Quando a informação é sensível, como senha, token ou chave de acesso, o ideal é usar `secrets`.

Secrets protegem informações que não devem aparecer diretamente no código.

## Jobs e steps

Um job representa um bloco de trabalho.

Um step representa uma etapa dentro desse bloco.

Exemplo mental:

- job: testar aplicação;
- steps: baixar código, instalar dependências, rodar testes.

## Jobs paralelos

Jobs paralelos são jobs que rodam ao mesmo tempo.

Isso ajuda a acelerar a pipeline, porque algumas tarefas não dependem uma da outra.

Exemplo:

- análise de código;
- testes unitários;
- verificação de segurança.

Se todas essas tarefas puderem rodar independentemente, elas podem ser executadas em paralelo. Se alguma falhar, a pipeline falha.

## Dependência entre jobs com needs

Nem tudo pode rodar em paralelo.

Algumas etapas precisam esperar outras terminarem.

No GitHub Actions, o `needs` serve para dizer que um job depende de outro.

Exemplo:

- primeiro roda a análise de código;
- depois rodam os testes;
- depois acontece o build;
- depois vem o deploy.

Se o build depende dos testes, ele só deve começar depois que os testes passarem.

## GitOps

GitOps é uma abordagem em que o Git guarda o estado desejado da aplicação ou da infraestrutura.

Em vez de alguém entrar manualmente no servidor para alterar algo, a mudança é feita no repositório.

Depois disso, uma ferramenta como Argo CD ou Flux observa o repositório e compara:

- o que está descrito no Git;
- o que está rodando no ambiente real.

Se existir diferença, a ferramenta reconcilia o ambiente para que ele fique igual ao que está no Git.

## Explicando GitOps de forma simples

Imagine que o Git é a lista oficial de como o ambiente deve estar.

Se o ambiente real estiver diferente da lista, o operador GitOps ajusta o ambiente até ele voltar ao estado esperado.

Isso traz mais controle, histórico e previsibilidade, porque toda mudança importante passa pelo repositório.

## Link da aula

- https://github.com/josenetoo/fiap-dclt-aula01


a