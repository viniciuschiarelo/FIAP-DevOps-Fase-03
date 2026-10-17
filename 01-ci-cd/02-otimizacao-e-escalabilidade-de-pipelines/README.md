# 2. Otimização e Escalabilidade de Pipelines

## Ideia principal

Depois que uma pipeline funciona, o próximo passo é melhorar sua eficiência.

O objetivo é fazer a pipeline entregar o mesmo resultado, mas em menos tempo, com mais organização e reaproveitando configurações quando possível.

## Multi-stage

Uma pipeline multi-stage é uma pipeline dividida em estágios.

Cada estágio representa uma fase do processo.

Exemplo:

1. validação;
2. testes;
3. build;
4. publicação;
5. deploy.

Essa divisão deixa o fluxo mais fácil de entender e controlar.

## Paralelização de processos

Paralelizar significa executar tarefas ao mesmo tempo.

Isso é útil quando uma etapa não depende diretamente da outra.

Exemplo:

- testes unitários;
- análise de qualidade;
- testes de segurança;
- testes de performance.

Essas etapas podem rodar em paralelo se uma não precisar esperar o resultado da outra.

O benefício é reduzir o tempo total da pipeline.

## O que não deve rodar em paralelo?

Algumas etapas precisam ser sequenciais.

Build e deploy são bons exemplos.

Normalmente, primeiro a aplicação precisa ser construída. Só depois faz sentido publicar ou fazer deploy.

Fluxo esperado:

1. validar código;
2. testar;
3. fazer build;
4. fazer deploy.

## Usando needs para controlar dependências

O `needs` define que um job precisa esperar outro job terminar.

Exemplo:

Se o build depende dos testes, o job de build deve ter `needs` apontando para os jobs de teste.

Assim, a pipeline evita fazer deploy de uma aplicação que ainda não foi validada.

## Matrix strategy

Matrix strategy é uma forma de executar o mesmo job em várias combinações de ambiente.

Na aula, a ideia foi testar a aplicação em diferentes versões do Node.js e em diferentes sistemas operacionais.

Exemplo:

- Node.js 18 no Ubuntu;
- Node.js 20 no Ubuntu;
- Node.js 22 no Ubuntu;
- Node.js 18 no Windows;
- Node.js 20 no macOS.

Isso aumenta a confiança na entrega, porque mostra se a aplicação funciona em diferentes cenários.

## Quando matrix strategy ajuda?

Ela ajuda quando o projeto precisa garantir compatibilidade com mais de uma versão ou ambiente.

Exemplos:

- biblioteca usada por vários projetos;
- aplicação que roda em ambientes diferentes;
- projeto que precisa suportar múltiplas versões de runtime;
- validação antes de atualizar a versão do Node.js.

## Cuidado com matrix strategy

Matrix strategy melhora a cobertura, mas pode aumentar o custo e o tempo da pipeline.

Se houver muitas combinações, a pipeline pode ficar pesada.

Por isso, o ideal é testar as combinações que realmente importam para o projeto.

## Reutilização de workflows

Reutilizar workflows é útil quando vários projetos seguem o mesmo padrão de pipeline.

Em vez de copiar e colar o mesmo YAML em todos os repositórios, é possível criar um workflow reutilizável.

Isso ajuda porque:

- reduz repetição;
- facilita manutenção;
- padroniza pipelines;
- evita inconsistência entre projetos.

## Exemplo simples

Se todos os projetos Node.js da empresa precisam instalar dependências, rodar testes e fazer build, esse fluxo pode virar um workflow reutilizável.

Quando for necessário alterar alguma coisa, a mudança é feita em um único lugar.

## Resumo

Otimizar pipelines não é só fazer tudo rodar mais rápido.

Também significa organizar melhor o fluxo, rodar em paralelo o que faz sentido, respeitar dependências e reaproveitar configurações comuns.

a