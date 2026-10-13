## Aula 1
A ideia do AIOPs é termos um agente para conversar em linguagem natural relacionada ao cluster, por exemplo.

Em projetos grandes, rodar todos os testes a cada commit é muito lento, uma solução é usar a IA, ela analisa 
quais arquivos mudaram e sugere apenas os testes relacionados.

então temos um arquivo em python que verifica quais arquivos de teste foram modificados, após isso ele armazena
em um txt os arquivos alterados, e depois chama a IA, que faz o papel de um agente de pipeline e roda somente
os teste que tiveram seus arquivos alterados, assim encurtando o tempo de carga dos testes.


## Aula 2
Podemos usar a IA, para analisar logs automaticamente, detectando padroes de erro, que são muitas coisas para engenheiro
ler manualmente, essa solução é boa pois a IA identifica padrões de erro em segundos, alerta automatico, time
age antes do incidente escalar.

aplicação escrever os logs em um arquivo de log, temos uma automação que chama o gemini, para processar os padroes
dos logs, assim que o problema. por exemplo ela encontra 5 erros de db e após isso ela cria um alerta no github.