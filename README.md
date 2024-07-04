# Apoio Saúde

## Ideia do Projeto

O projeto "Apoio Saúde" tem como objetivo simplificar a vida de familiares e cuidadores ao oferecer uma solução organizada e acessível para o cuidado de pacientes. Através dessa aplicação, os usuários poderão gerenciar informações relacionadas ao cuidado de seus entes queridos de forma eficiente e intuitiva.

## Instalação

Para começar a trabalhar com o framework Django e iniciar o projeto "Apoio Saúde", siga os passos abaixo:

### Pré-requisitos

1. **Python**: Certifique-se de ter o Python instalado em seu sistema. Você pode baixá-lo e instalá-lo a partir do [site oficial do Python](https://www.python.org/downloads/).

2. **Git**: Se você ainda não tem o Git instalado, você pode baixá-lo e instalá-lo a partir do [site oficial do Git](https://git-scm.com/).

### Clonando o Repositório

Clone o repositório do projeto "Apoio Saúde":

```bash
git clone https://github.com/seu-usuario/apoio-saude.git
cd apoio-saude
```
### Inicialização do Ambiente Virtual (venv)

Crie um ambiente virtual para isolar as dependências do seu projeto. No terminal, navegue até o diretório do projeto e execute o seguinte comando:

```bash
python -m venv venv
```

## Ative o ambiente virtual:

No Windows:

```bash
.\venv\Scripts\activate
```

No macOS e Linux:

```bash
source venv/bin/activate
```

### Instalação das Dependências

Instale todas as dependências necessárias utilizando o pip:

```bash
pip install -r requirements.txt
```

## Configuração do Banco de Dados

Para configurar o banco de dados, siga os passos abaixo:

1. **Crie as Migrações**:

    ```bash
    python manage.py makemigrations
    ```

2. **Aplique as Migrações**:

    ```bash
    python manage.py migrate
    ```

3. **Criar um Superusuário**:

    ```bash
    python manage.py createsuperuser
    ```

    Siga as instruções para criar um superusuário com um nome de usuário, email e senha.


### Executando o Servidor de Desenvolvimento

Inicie o servidor de desenvolvimento:

```bash
python manage.py runserver
```

Isso iniciará o servidor de desenvolvimento do Django. Você poderá acessar seu projeto em http://localhost:8000/.
