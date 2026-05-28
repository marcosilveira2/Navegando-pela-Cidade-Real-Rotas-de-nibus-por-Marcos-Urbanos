# 🏛️ Boituva Landmarks
Navegando-pela-Cidade-Real-Rotas-de-Ônibus-por-Marcos-Urbanos

Este é um projeto desenvolvido em Django para mapear e gerenciar os Marcos Urbanos de Boituva. O projeto utiliza Docker para facilitar o ambiente de desenvolvimento entre a equipe.

## 🚀 Como Rodar o Projeto Localmente

Siga os passos abaixo para configurar e executar o projeto na sua máquina.

### 1. Pré-requisitos
Você precisará ter instalado em sua máquina:
* Git
* Docker e Docker Compose

### 2. Clonar o Repositório
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
```

### 3. Configurar as Variáveis de Ambiente

O projeto utiliza variáveis de ambiente para manter senhas seguras.

    Crie um arquivo chamado .env na raiz do projeto.

    Copie a estrutura abaixo e preencha com as suas senhas locais.

arquivo .env

SECRET_KEY=
MARIADB_ROOT_PASSWORD=
MARIADB_DATABASE=
MARIADB_USER=
MARIADB_PASSWORD=



### 4. Subir os Containers (Banco de Dados e Aplicação)

Com o Docker instalado, execute o comando abaixo para baixar as imagens e iniciar o MariaDB e o Django:
Bash
```bash
docker-compose up --build
```

### 5. Executar as Migrações do Banco

Em um novo terminal, execute as migrações para criar as tabelas no MariaDB:
Bash
```bash
docker-compose exec web python manage.py migrate
```
### 6. Criar Usuário Administrador (Opcional)

Para acessar o painel administrativo do Django (http://localhost:8000/admin), crie um superusuário:
Bash
```bash
docker-compose exec web python manage.py createsuperuser
```
O projeto estará disponível em: http://localhost:8000
