# MovieMatch

MovieMatch é um projeto que comecei para praticar consumo de API e integração entre front-end e back-end.

A ideia é simples: o usuário escolhe algumas preferências, como gêneros, humor, nota mínima e período, e a aplicação tenta recomendar filmes que tenham mais relação com essas escolhas.

Para buscar os dados dos filmes, estou usando a API do TMDB

---

# Português

## Sobre o projeto

Esse projeto foi criado principalmente para estudo.

Meu objetivo era praticar como uma aplicação pode consumir dados de uma API externa, tratar essas informações e mostrar o resultado na tela.

Durante o desenvolvimento, fui adicionando algumas funcionalidades para deixar a recomendação um pouco mais personalizada.

O usuário pode informar algumas preferências e o sistema busca filmes compatíveis usando dados do TMDB.

Também é possível abrir os detalhes de um filme e ver informações como sinopse, nota, ano de lançamento e onde ele está disponível para assistir no Brasil.

---

## O que o projeto faz

Atualmente a aplicação permite:

* escolher um ou mais gêneros;
* informar o tipo de filme que a pessoa está procurando no momento;
* definir uma nota mínima;
* definir um período de lançamento;
* usar um filme como referência;
* definir uma duração máxima;
* escolher um idioma original;
* evitar alguns gêneros;
* escolher entre filmes mais conhecidos ou menos populares;
* calcular uma porcentagem de compatibilidade;
* mostrar o motivo da recomendação;
* mostrar pôster, nota, ano, gêneros e sinopse;
* consultar onde o filme pode ser assistido no Brasil.

---

## Como funciona

O front-end coleta as escolhas do usuário e envia essas informações para o back-end.

Um exemplo dos dados enviados é:

```json
{
  "genres": [
    "ficcao",
    "drama"
  ],
  "mood": "pensar",
  "rating": 7,
  "year_min": 2000,
  "runtime_max": 150,
  "language": "en",
  "popularity_mode": "balanced",
  "reference_movie": "Interestelar",
  "avoid_genres": [
    "terror"
  ]
}
```

O back-end recebe essas informações e consulta a API do TMDB.

Depois disso, ele aplica algumas regras para calcular uma compatibilidade entre os filmes encontrados e as preferências informadas pelo usuário.

Por exemplo:

```text
Arrival             91%
Ex Machina          87%
Predestination      83%
```

Esse cálculo ainda é uma lógica criada para estudo e pode ser melhorado no futuro.

---

## Compatibilidade

A porcentagem de compatibilidade leva em consideração alguns critérios, como:

* gêneros escolhidos;
* tipo de experiência desejada;
* nota do filme;
* popularidade;
* filme de referência;
* idioma;
* período de lançamento.

Quando o usuário abre os detalhes de um filme, também é possível ver uma explicação básica de como o score foi calculado.

---

## Combinação de gêneros

Se o usuário escolher mais de um gênero, o sistema tenta retornar filmes que tenham todos os gêneros selecionados.

Por exemplo:

```text
Ação + Romance
```

O filme precisa ter os dois gêneros.

Ele pode ter outros gêneros também, como:

```text
Ação
Romance
Comédia
```

---

## Tecnologias usadas

### Front-end

* HTML
* CSS
* JavaScript

### Back-end

* Python
* FastAPI
* Uvicorn
* HTTPX
* python-dotenv
* Pydantic

### API

* TMDB API

### Versionamento

* Git
* GitHub

---

## Estrutura do projeto

```text
movie-recommender/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
└── .gitignore
```

O arquivo `.env` não é enviado para o GitHub porque contém o token da API.

---

## Configuração

Para executar o projeto, é necessário ter uma conta no TMDB e gerar um API Read Access Token.

Depois disso, crie um arquivo chamado:

```text
backend/.env
```

Dentro dele:

```env
TMDB_TOKEN=SEU_TOKEN_DO_TMDB
```

Não publique esse token no GitHub.

---

## Como executar

### 1. Clonar o projeto

```bash
git clone https://github.com/MarcosPcost/movie-recommendations.git
```

Depois entre na pasta:

```bash
cd movie-recommendations
```

---

### 2. Entrar na pasta do back-end

```bash
cd backend
```

---

### 3. Criar um ambiente virtual

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

### 5. Criar o arquivo `.env`

```env
TMDB_TOKEN=SEU_TOKEN_DO_TMDB
```

---

### 6. Iniciar o back-end

```bash
uvicorn main:app --reload
```

O back-end ficará disponível em:

```text
http://127.0.0.1:8000
```

A documentação automática do FastAPI pode ser acessada em:

```text
http://127.0.0.1:8000/docs
```

---

### 7. Abrir o front-end

Abra:

```text
frontend/index.html
```

Também é possível usar uma extensão como Live Server no VS Code.

---

## Endpoints principais

Verificar se a API está funcionando:

```http
GET /
```

Gerar recomendações:

```http
POST /recommendations
```

Consultar onde assistir um filme no Brasil:

```http
GET /movies/{movie_id}/watch-providers
```

---

## Fluxo da aplicação

```text
Usuário
   ↓
Escolhe preferências
   ↓
JavaScript
   ↓
FastAPI
   ↓
TMDB API
   ↓
Filmes encontrados
   ↓
Cálculo de compatibilidade
   ↓
Resultados
   ↓
Front-end
```

---

## Segurança

O token da API fica armazenado somente no back-end.

Ele não fica diretamente no JavaScript do navegador.

Os principais arquivos ignorados pelo Git são:

```gitignore
.env
*.env
.venv/
__pycache__/
*.pyc
```

---

## O que eu pretendo melhorar

Como esse ainda é um projeto de estudo, existem várias coisas que quero testar no futuro, como:

* sistema de login;
* banco de dados;
* lista de filmes favoritos;
* filmes já assistidos;
* histórico de recomendações;
* sistema de gostei e não gostei;
* várias referências de filmes;
* preferências por atores e diretores;
* melhoria do algoritmo de compatibilidade;
* uso de machine learning;
* deploy do front-end e do back-end.

---

## O que aprendi com esse projeto

Com esse projeto consegui praticar principalmente:

* consumo de API;
* requisições HTTP;
* uso de JSON;
* integração entre JavaScript e Python;
* criação de API com FastAPI;
* uso de variáveis de ambiente;
* organização entre front-end e back-end;
* tratamento de dados;
* criação de filtros;
* lógica básica de recomendação;
* uso de Git e GitHub.

---

## Fonte dos dados

Os dados dos filmes são obtidos através da API do TMDB.

As informações de disponibilidade em plataformas de streaming são fornecidas pelo JustWatch através do TMDB.

Este projeto utiliza a API do TMDB, mas não possui relação oficial com o TMDB.

---

# English

## About the project

MovieMatch is a study project I created to practice API integration and basic full-stack development.

The main idea is to let the user choose some preferences and then recommend movies based on those choices.

The project uses the TMDB API to retrieve movie information.

The user can also open a movie and see details such as rating, release year, genres, overview and streaming availability in Brazil.

---

## Current features

The application currently allows the user to:

* select one or more genres;
* choose the type of movie experience they want;
* set a minimum rating;
* select a release period;
* use another movie as a reference;
* set a maximum runtime;
* choose an original language;
* exclude unwanted genres;
* choose between popular movies and less known movies;
* calculate a compatibility percentage;
* see why a movie was recommended;
* view poster, rating, year, genres and overview;
* check where the movie is available in Brazil.

---

## How it works

The front-end collects the user's preferences and sends them to the back-end.

Example:

```json
{
  "genres": [
    "ficcao",
    "drama"
  ],
  "mood": "pensar",
  "rating": 7,
  "year_min": 2000,
  "runtime_max": 150,
  "language": "en",
  "popularity_mode": "balanced",
  "reference_movie": "Interstellar",
  "avoid_genres": [
    "terror"
  ]
}
```

The back-end receives this information and requests movie data from TMDB.

It then applies some rules to calculate how well each movie matches the user's preferences.

Example:

```text
Arrival             91%
Ex Machina          87%
Predestination      83%
```

The recommendation logic was created mainly for learning purposes and can still be improved.

---

## Compatibility score

The compatibility score currently considers factors such as:

* selected genres;
* mood;
* movie rating;
* popularity;
* reference movie;
* original language;
* release period.

The movie details screen also shows a basic explanation of how the score was calculated.

---

## Genre matching

When the user selects multiple genres, the application tries to return movies that contain all selected genres.

For example:

```text
Action + Romance
```

The movie must contain both genres.

It can also contain additional genres, such as:

```text
Action
Romance
Comedy
```

---

## Technologies

### Front-end

* HTML
* CSS
* JavaScript

### Back-end

* Python
* FastAPI
* Uvicorn
* HTTPX
* python-dotenv
* Pydantic

### API

* TMDB API

### Version control

* Git
* GitHub

---

## Project structure

```text
movie-recommender/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
└── .gitignore
```

The `.env` file is not committed because it contains the API token.

---

## Setup

To run the project, you need a TMDB account and an API Read Access Token.

Create:

```text
backend/.env
```

Add:

```env
TMDB_TOKEN=YOUR_TMDB_TOKEN
```

Do not publish this token on GitHub.

---

## Running the project

### 1. Clone the repository

```bash
git clone https://github.com/MarcosPcost/movie-recommendations.git
```

Enter the project:

```bash
cd movie-recommendations
```

---

### 2. Open the back-end folder

```bash
cd backend
```

---

### 3. Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Create the `.env` file

```env
TMDB_TOKEN=YOUR_TMDB_TOKEN
```

---

### 6. Start the back-end

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

### 7. Open the front-end

Open:

```text
frontend/index.html
```

You can also use Live Server in VS Code.

---

## Main endpoints

Check if the API is running:

```http
GET /
```

Generate recommendations:

```http
POST /recommendations
```

Check Brazilian streaming availability:

```http
GET /movies/{movie_id}/watch-providers
```

---

## Application flow

```text
User
   ↓
Preferences
   ↓
JavaScript
   ↓
FastAPI
   ↓
TMDB API
   ↓
Movie data
   ↓
Compatibility calculation
   ↓
Recommendations
   ↓
Front-end
```

---

## Security

The TMDB token is stored only in the back-end.

It is not directly exposed in the browser JavaScript.

Files ignored by Git include:

```gitignore
.env
*.env
.venv/
__pycache__/
*.pyc
```

---

## Future improvements

This is still a learning project, so there are several things I would like to improve in the future:

* login system;
* database;
* favorites list;
* watched movies;
* recommendation history;
* like and dislike feedback;
* multiple reference movies;
* actor and director preferences;
* improved recommendation logic;
* machine learning;
* deployment.

---

## What I learned

This project helped me practice:

* consuming APIs;
* HTTP requests;
* JSON;
* JavaScript and Python integration;
* FastAPI;
* environment variables;
* front-end and back-end organization;
* data filtering;
* recommendation logic;
* Git and GitHub.

---

## Data source

Movie data is provided by the TMDB API.

Streaming availability data is provided by JustWatch through TMDB.

This project uses the TMDB API but is not officially associated with TMDB.
