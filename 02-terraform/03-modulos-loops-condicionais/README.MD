### Aula 1
Aprendemos da maneira manual de criar infraestrutura, porem podemos utilizar agora, uma outra maneira que é buscar no terraform registry modulos prontos que são muito bem documentados. O OpenTofu também possui um repositório de modulos aberto para facilitarmos nossa vida. A ideia é aprendermos a criar nosso próprio modulo ou aprender a reutilizar modulos prontos.


### Aula 2
Modularizamos nossa infraestrutura, criando dentro da pasta raiz a pasta network, ela conterá todas as configurações dos arquivos da nossa VPC com suas subnets configuradas, apenas as configurações de network, é uma boa pratícas e no arquivo principal da nossa infraestrutura chamamso como dependencias usando module.network.vpc_id por exemplo, assim criamos a nossa referência, podendo chamar quantas vezes for necessário.

Os loops no terraform funciona utilizando o 'Count' e o 'For each', o count é usado para multiplos recursos que são identicos, ou seja usado para criar réplicas. já o for each, é usado para criar instancias de itens diferentes, lendo de uma lista por exemplo o tipo de instancia que ele vai querer.

Condicionais: A principal condicional que temos no terraform é o ternário, que é igual no JS por exemplo
const variavel = boolean ? 'true' : 'false'

### Aula 3
Documentação de condicionais do terraform: https://developer.hashicorp.com/terraform/language/expressions/conditionals
