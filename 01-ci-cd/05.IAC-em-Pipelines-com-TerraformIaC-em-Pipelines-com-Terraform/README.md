## Aula 01

Antes do terraform era adotada todo um planejamento antes de criar uma aplicação, oque acontecia, 
o time de aplicação fazia uma requisição de infraestrutura, o time de ti, aprovava ou rejeitavam e a partir dai
compravam os materiais para a infraestrutura para somente dps ligar a aplicação nela.
Depois do terraform isso ficou mais simples, pois conseguiamos criar toda a nossa infraestrutura configurada
através do terraform, via código.

Na aula vimos a configuração de uma pipeline, para subir ou atualizar nossa infraestrutura, que foi feita com
terraform, então toda vez que alteramos um arquivo dentro da pasta /terraform e subimos a alteração para o github
ele subira a infraestrutura na AWS automaticamente

## Aula 02 
Podemos usar a IAC para aplicar o conceito de multi-ambientes, como desenvolvimento, testes e produção, para isso
podemos trabalhar ou com diretórios separados, com workspaces, ou então variaveis de ambiente

## Aula 03
Podemos trabalhar com modulos também para o IAC, então disponibilizamos modulos com configurações especificas
como vpc, security-group e s3 a grande sacada e que referenciamos eles no nosso arquivo yml de modules, e a partir
do nosso ambiente puxamos essas informações dos modulos