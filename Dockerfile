# Usa imagem Python mais completa para evitar erros de build
FROM python:3.12-bullseye

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências do sistema (para compilar mysqlclient e afins)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Coleta arquivos estáticos (ignora erro se não estiver configurado ainda)
RUN python manage.py collectstatic --noinput || true

# Expõe a porta padrão do Gunicorn
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["gunicorn", "TrabalhoWeb.wsgi:application", "--bind", "0.0.0.0:8000"]

