# Use uma imagem oficial do Python como base
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo de dependências para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o diretório de trabalho
COPY src/ .

# Exponha a porta em que a aplicação Flask será executada
EXPOSE 8888

# Defina o comando para iniciar a aplicação quando o container for iniciado
CMD ["python", "backend.py"]
