# E-commerce API

![Tests](https://github.com/gscavalcante02-png/ecommerce-api/actions/workflows/tests.yml/badge.svg)

API REST de e-commerce, só back-end, feita com FastAPI, SQLModel e PostgreSQL. Tem login com token, dois papéis de usuário (cliente e admin), catálogo de produtos com categorias (relação N:N) e pedidos com controle de estoque.

Foi construída como projeto de estudo, com foco em organização em camadas, testes e um ambiente que sobe com um comando só.

## Tecnologias

- Python 3.14, FastAPI, SQLModel, PostgreSQL
- Autenticação com JWT; senhas com hash (passlib + bcrypt)
- Testes com pytest (SQLite em memória)
- Docker e Docker Compose
- GitHub Actions: roda os testes e constrói a imagem Docker a cada push

## Como rodar

Precisa só do Docker instalado.

```
git clone https://github.com/gscavalcante02-png/ecommerce-api.git
cd ecommerce-api
copy .env.example .env
docker compose up --build
```

No Linux/macOS, use `cp` no lugar de `copy`.

Antes de usar de verdade, edite o `.env` e troque a `SECRET_KEY` e a senha do banco. Para gerar uma chave:

```
py -c "import secrets; print(secrets.token_hex(32))"
```

A API fica em http://localhost:8000 e a documentação interativa em http://localhost:8000/docs.

Para parar: `docker compose down` (os dados do banco ficam guardados). Para apagar também os dados: `docker compose down -v`.

## Variáveis de ambiente

| Variável                            | Para que serve                                    | Padrão                                   |
| ----------------------------------- | ------------------------------------------------- | ---------------------------------------- |
| `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Acesso ao PostgreSQL                              | `postgres` / `postgres` / `ecommerce_db` |
| `DB_HOST`, `DB_PORT`                | Endereço do banco (no Docker o Compose usa `db`)  | `localhost` / `5432`                     |
| `SECRET_KEY`                        | Chave que assina os tokens de login (obrigatória) | sem padrão                               |
| `ALGORITHM`                         | Algoritmo do JWT                                  | `HS256`                                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES`       | Validade do token                                 | `30`                                     |

## Rotas principais

| Área       | Rotas                                                                                                                      |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- |
| Auth       | `POST /auth/login`                                                                                                         |
| Usuários   | `POST /users/` (cadastro), `GET /users/me`. Admin: listar, buscar e atualizar usuários                                     |
| Categorias | `GET /categories/` (filtro por nome e paginação), `GET /categories/{id}`. Admin: criar                                     |
| Produtos   | `GET /products`, `GET /products/{id}`. Admin: criar, atualizar e remover                                                   |
| Pedidos    | `POST /orders/`, `GET /orders/` (só os do usuário), `GET /orders/{id}` (dono ou admin). Admin: `PATCH /orders/{id}/status` |

Regras importantes:

- O cadastro público sempre cria usuário comum; o papel nunca vem do cliente.
- Um pedido com quantidade maior que o estoque é recusado (`400`).
- Ninguém vê o pedido de outro usuário (`403`), exceto admin.

## Estrutura do projeto

```
core/          configurações e segurança (JWT, hash de senha)
database/      conexão com o banco e criação das tabelas
models/        tabelas (SQLModel)
schemas/       dados de entrada e saída da API (Pydantic)
crud/          acesso ao banco
routers/       rotas da API
tests/         testes de CRUD e de rotas
main.py        criação do app
```

## Testes

```
pip install -r requirements-dev.txt
python -m pytest
```

São 54 testes, cobrindo CRUD e rotas, incluindo permissões (usuário comum não cria produto e não vê pedido de outra pessoa). Eles usam SQLite em memória, então rodam rápido e sem precisar de um PostgreSQL.

## Decisões e dificuldades

- **Papel do usuário.** Em uma revisão de segurança, o schema de cadastro aceitava o campo `role`, o que permitiria alguém se cadastrar como admin. O cadastro agora usa um schema separado (`UserRegister`, sem `role`) e o servidor define o papel. Há um teste que garante isso.
- **Banco no Docker.** Dentro do Compose, a API encontra o banco pelo nome do serviço (`db`), e não por `localhost`. Como as tabelas são criadas ao iniciar, usei um healthcheck para a API só ligar depois que o PostgreSQL responde.
- **Dados fora do container.** O banco usa um volume, então apagar os containers não apaga os dados.
- **Dependências.** Fixei as versões que passaram nos testes e separei o que é só de desenvolvimento (`requirements-dev.txt`). A instalação foi validada num ambiente novo.
- **Imagem Docker.** O `Dockerfile` copia as dependências antes do código, para aproveitar o cache, e roda a API como usuário comum, sem root. O `.dockerignore` deixa o `.env` fora da imagem.
- **Testes.** Usam SQLite em memória, para rodar rápido e sem depender de um PostgreSQL no pipeline.

## Limitações e melhorias futuras

- Ainda não há script para criar o primeiro usuário admin.
- Cobrir com testes a atualização e a remoção de produtos.
- Usar migrações (Alembic) em vez de criar as tabelas ao iniciar.
- Trocar `datetime.utcnow` (obsoleto) e tornar o log de SQL (`echo`) configurável.
- Deploy público da API.
