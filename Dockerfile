# Escolhe imagem oficial do Python
FROM python:3.12-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências do sistema (incluindo para MySQL)
RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev libssl-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Coleta arquivos estáticos (caso necessário)
RUN python manage.py collectstatic --noinput || true

# Expõe a porta 8000
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["gunicorn", "ApoioSaude.wsgi:application", "--bind", "0.0.0.0:8000"]
