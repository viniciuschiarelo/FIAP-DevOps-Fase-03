### Aula 01
Variáveis de input => aquelas que passamos no .tfvars ou no variables.tf - normalmente são relacionadas a VPC,
id da imagem, tipo de instancia é tudo que precisamos informar para provisionar um recurso, se não informamos
o terraform não ira permitir nem seguir com o provisionamento

Variáveis de output => Ápos a execução, trazem infos importante sobre os recursos criados


Variáveis de locals => ajudam na organização. Criar filtros para trazer informações relevantes

o tfvars, é como se fosse o nosso arquivo env para o terraform, então na aula temos dois tfvars, um de dev (desenvolvimento) e outro de prod (Produção).

## Aula 02
Um cuidado que devemos tomar é que no terraform algumas coisas são sequenciais, então a ordem importa e devemos nos atentar a isso
Outputs => Até o momento que executamos nosso código do terraform ele permanece vazio até que executemos/aplicamos nossa infraestrutura a partir dai ele preenche nossas variaveis de output

terraform.tfstate é um arquivo muito importante para fazermos execuções, não podemos excluir ele, quando tiver alterações ele ou vai destruir a instancia ou modificala. Devemos tomar cuidado pois ao fazer alterações o tfstate pode excluir recursos que provisionamos, por exemplo na aula provisionamos recursos usando o tfvars de dev e depois aplicamos o de produção ele destroi os recursos de dev que anteriormente haviamos deixado disponível.

## Aula 03 
O ideal é termos um tfstate externo ao nosso projeto que armazene num bucket por exemplo para que não devamos ficar nos procupando com o tfstate, a versão dele e coisas assim, pois sempre teremos um backup. Quando não temos o tfstate, ele tenta buscar onde provisionamos, no caso da aula é na aws, como tanto o local quanto o atual está vazio ele vai querer recriar e mesmo que na AWS tenhamos algumas coisas, ele pode perder a refencia da ec2 por exemplo e queira recriar mesmo assim.

o tfstate é o coração do terraform, então no menor sinal de problema ele pode dar conflito, por exmplo caso exista um tfstate local e um remoto, o ideal é sempre usar o tfstate remoto.