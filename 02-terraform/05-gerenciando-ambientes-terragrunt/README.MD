### Aula 01
Terragrunt é um projeto para orquestrarmos a utilização do terraform em multiplos times.

https://terragrunt.com/

O lado bom de usar o terragrunt é que conseguimos diminuir a duplicação de código separando nossa infraestrutura em pequenas pastas, por exemplo, um diretório de VPC somente com aquela configuração um de EKs com somente aquela configuração, e a grande maioria das alterações será feita em modulos, deixando algo mais simples de dar manutenção, o terraform é separado em blocos, ele é uma forma de deixar nosso ambiente mais produtivo


### Aula 02
Conseguimos referenciar no github ao invés de só localmente para conseguir pegar uma estrutura de modulos, por isso o ideal é deixarmos um arquivo de modulos em um repositório separado, pois assim conseguimos chamar eles de qualquer outro projeto

### Aula 03
