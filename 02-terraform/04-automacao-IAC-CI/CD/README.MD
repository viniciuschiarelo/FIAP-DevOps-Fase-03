### Aula 01
Processo manual gera manutenção, inconsistencias, sem padrões. Automação transforma processos, garantindo entregas de valor para o usuário e segurança.

### Aula 02
Configurando GITHUB ACTIONS para TERRAFORM, na nossa pipeline temos as triggers de gatilho para identificar quando tivermos que subir o ambiente.

configuramos permissões de token para ele pedir um token novo de sessão e expirar ao final dela, garantindo maior segurança. Quando criamos dentro da pasta .github o diretório de workflows ele cria já automaticamente no nosso action o workflow. assim que ativarmos o gatilho da trigger ele roda o action. E no caso se por exemplo não especificarmos na trigger uma branch que tivermos e commitarmos ela não sera acionada.

### Aula 03 
Casos de usos avançados: https://github.com/kauaisg/infra-as-code-fiap - aula4-iac