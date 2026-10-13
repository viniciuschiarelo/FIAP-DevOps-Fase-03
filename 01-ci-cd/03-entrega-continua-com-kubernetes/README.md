# 3. Entrega Contínua com Kubernetes

## Link da aula

- https://github.com/josenetoo/fiap-dclt-aula03

## Ideia principal

Nesta aula, o foco foi automatizar a criação e publicação de uma imagem de container.

A pipeline observa alterações no projeto, cria uma nova imagem Docker e envia essa imagem para um registry.

No exemplo da aula, o registry usado foi o Amazon ECR.

## O que é ECR?

ECR significa Elastic Container Registry.

É o serviço da AWS usado para armazenar imagens de container.

Pensando de forma simples: o ECR é como um repositório para imagens Docker.

Assim como o GitHub guarda código, o ECR guarda imagens que podem ser usadas depois em ambientes como Kubernetes, ECS ou outros serviços de deploy.

## O que é uma imagem de container?

Uma imagem de container é um pacote com tudo que a aplicação precisa para rodar.

Ela pode conter:

- código da aplicação;
- dependências;
- runtime;
- configurações necessárias;
- instruções definidas no `Dockerfile`.

Depois que a imagem é criada, ela pode ser executada em diferentes ambientes de forma mais previsível.

## O papel do Dockerfile

O `Dockerfile` descreve como a imagem deve ser montada.

Ele funciona como uma receita.

Exemplo mental:

1. use uma imagem base;
2. copie os arquivos da aplicação;
3. instale dependências;
4. exponha a porta da aplicação;
5. defina o comando para iniciar o sistema.

Se o `Dockerfile` muda, a forma de construir a imagem também muda. Por isso, faz sentido acionar a pipeline quando ele é alterado.

## Quando a pipeline era acionada?

Na aula, a pipeline era acionada quando havia alterações em partes importantes do projeto, como:

- arquivos dentro de `src`;
- o arquivo `Dockerfile`.

Isso evita executar a pipeline sem necessidade.

Se uma mudança em documentação não afeta a imagem da aplicação, por exemplo, talvez não seja preciso criar uma nova imagem.

## Fluxo da pipeline

O fluxo geral da aula foi:

1. detectar alteração no código ou no `Dockerfile`;
2. iniciar a pipeline;
3. autenticar na AWS;
4. fazer login no ECR;
5. construir a imagem Docker;
6. marcar a imagem com uma tag;
7. enviar a imagem para o ECR.

## Por que autenticar na AWS?

O ECR é um serviço protegido.

Para enviar uma imagem para lá, a pipeline precisa provar que tem permissão.

Por isso, ela precisa configurar credenciais da AWS e fazer login no registry antes de publicar a imagem.

## Relação com entrega contínua

Publicar a imagem no ECR é uma etapa importante da entrega contínua.

Depois que a imagem está no registry, outro processo pode usá-la para atualizar um ambiente.

Esse próximo passo pode ser feito com:

- Kubernetes;
- Argo CD;
- Flux;
- Helm;
- manifests YAML;
- outro serviço de deploy.

## Explicando de forma simples

O fluxo é parecido com preparar uma entrega:

1. o código muda;
2. a pipeline monta um pacote novo da aplicação;
3. esse pacote vira uma imagem Docker;
4. a imagem é enviada para um local confiável;
5. o ambiente pode buscar essa imagem para rodar a nova versão.

## Resumo

A aula mostrou como automatizar a publicação de imagens de container no ECR.

Esse processo reduz trabalho manual e prepara a aplicação para ser implantada em ambientes modernos, especialmente ambientes baseados em containers e Kubernetes.
