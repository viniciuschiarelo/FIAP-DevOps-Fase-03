Por que podemos adotar o gitOps?

Segurança aprimorada
consistencia e reprodutibilidade
auditabilidade e rastreabilidade
experiencia do desenvolvedor

No modelo tradicional de CI/cd é necessario que a pipeline tenha credenciais de alto privilégio para executar o push
oque pode apresentar um risco de segurança caso a pipeline seja comprometida.

Já o modelo PULL do gitOps eliminia essa vulnerabilidade, nele a pipeline tem permissão apenas para fazer o push para o repositorio
git, o processo de implantação é orquestrado por um agente que reside dentro do ambiente de destino. Este agente 
monitora o repositorio git e ao detectar atualizações ele puxa a nova configuração e aplica.


## Aula 2
O argo é o meio campo entre o repositorio git e nosso kluster no kubernets


## Aula 3
O FluxCD tem o bootstrap que é a entrada dessa estrutura, após isso ele bate na API do Kubernets que possui varios controladores sendo um deles o source que olha para a fonte de origem, imagens, git e s3.
Já o Kustomize tem toda a parte de RBAC e polices, Alersts. O fluxCD é GITOPS puro, automação total e sem interface grafica

Quando devemos usar o FLuxCD ou o argo cd? 
Argo, para interface grafica, multi-cluster facil ou SSO/RBAC integrado
FLUX Cd para gitops 100% puro, image-automation, soluçção mais leve ou abordagem modular
