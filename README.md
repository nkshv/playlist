Este é um projeto de aplicação web desenvolvido em Python com o framework Flask. Ele se conecta a um banco de dados MariaDB utilizando SQLAlchemy como ORM. A principal funcionalidade é interagir com a API do Spotify para criar novas playlists com base em recomendações de uma playlist existente. A aplicação é totalmente containerizada usando Docker e Docker Compose para facilitar a execução e o desenvolvimento.
# Como Executar

Siga os passos abaixo para configurar e rodar o ambiente de desenvolvimento localmente.
## 1. Clone o Repositório

Primeiro, clone este repositório para a sua máquina local:

```
git clone https://github.com/nkshv/playlist && cd playlist
```

## 2. Crie o Arquivo de Ambiente (.env)

Copie o conteúdo abaixo para o seu arquivo .env e preencha com suas credenciais:

**Credenciais da API do [Spotify](https://developer.spotify.com/dashboard)**
* CLIENT_ID=CLIENT_ID_SPOTIFY
* CLIENT_SECRET=CLIENT_SECRET_SPOTIFY
* REDIRECT_URI=http://localhost:8888/callback

**Credenciais do Banco de Dados**
* DB_USER=user
* DB_PASSWORD=senha
* DB_HOST=db
* DB_NAME=playlist_db

**Chave Secreta do Flask**
* FLASK_SECRET_KEY=chave_secreta

## 3. Construa e Inicie os Containers

Com o Docker em execução, use o Docker Compose para construir as imagens e iniciar os contêineres da aplicação e do banco de dados. Execute o seguinte comando no terminal:
```
docker-compose up --build
```

## 4. Acesse a Aplicação

Após a inicialização dos contêineres, a aplicação estará disponível no seu navegador.

Acesse: http://localhost:8888
