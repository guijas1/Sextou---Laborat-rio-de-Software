
# EventoFacil - Backend em Django

Este projeto é o backend do **EventoFacil**, uma plataforma para criar eventos, organizar categorias, permitir inscrições de usuários e registrar comentários.

O foco deste repositório é apenas o backend. Não há telas HTML nem frontend. A comunicação acontece por endpoints JSON, ou seja, o sistema recebe dados em JSON e responde em JSON.

## Como rodar o projeto

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Crie o banco de dados local:

```bash
python manage.py migrate
```

3. Rode os testes:

```bash
python manage.py test
```

4. Inicie o servidor:

```bash
python manage.py runserver
```

Depois disso, a API fica disponível em `http://127.0.0.1:8000/`.

## Estrutura do projeto

```text
config/          Configurações gerais do Django e rotas principais.
accounts/        Cadastro, login, logout e dados do usuário logado.
categories/      Categorias usadas para classificar eventos.
events/          Eventos, comentários, regras de criação e listagem.
registrations/   Inscrições e cancelamentos de inscrições.
```

## Visão abrangente: o que cada parte faz

Esta seção explica o projeto sem exigir conhecimento técnico profundo.

### `accounts`

Responsável pelas contas de usuário.

Ele permite criar uma conta, fazer login, fazer logout e consultar quem é o usuário atualmente autenticado.

### `categories`

Responsável por organizar eventos em grupos.

Exemplos de categorias: Workshop, Palestra, Show, Curso ou Tecnologia. Um evento sempre pertence a uma categoria.

### `events`

Responsável pelo cadastro e consulta de eventos.

Um evento possui título, descrição, data, local, capacidade máxima, categoria, organizador e status. Também é aqui que ficam os comentários dos usuários.

### `registrations`

Responsável pelas inscrições.

Ele controla quem se inscreveu em qual evento, impede inscrição duplicada e verifica se ainda existem vagas disponíveis.

### `services`

Os arquivos chamados `services.py` guardam as regras importantes do sistema.

Exemplo: a view recebe o pedido do usuário, mas quem decide se existe vaga ou se o organizador pode editar o evento é o service. Isso deixa o código mais fácil de testar e entender.

## Visão técnica: endpoints da API

### Saúde da aplicação

| Método | Endpoint | O que faz                                     |
| ------- | -------- | --------------------------------------------- |
| GET     | `/`    | Confirma que a aplicação está respondendo. |

### Contas

| Método | Endpoint                    | O que faz                             |
| ------- | --------------------------- | ------------------------------------- |
| POST    | `/api/accounts/register/` | Cria um usuário.                     |
| POST    | `/api/accounts/login/`    | Faz login e cria a sessão.           |
| POST    | `/api/accounts/logout/`   | Encerra a sessão do usuário logado. |
| GET     | `/api/accounts/me/`       | Retorna os dados do usuário logado.  |

Exemplo de cadastro:

```json
{
  "username": "maria",
  "email": "maria@example.com",
  "password": "pass12345"
}
```

### Como o login e o logout funcionam

Este projeto usa **sessão do Django**. Não existe token JWT.

1. O cliente envia usuário e senha para `POST /api/accounts/login/`.
2. Se os dados estiverem corretos, o Django devolve um cookie chamado `sessionid`.
3. O cliente precisa enviar esse mesmo cookie nas próximas requisições.
4. Para sair, o cliente envia `POST /api/accounts/logout/` com o cookie `sessionid`.
5. O Django apaga a sessão. Depois disso, endpoints protegidos voltam a responder com status `401`.

No Postman, os cookies normalmente são armazenados e enviados automaticamente. Faça o login e o logout usando exatamente o mesmo endereço, por exemplo `127.0.0.1`. Não alterne entre `127.0.0.1` e `localhost`, pois os cookies são associados ao endereço usado.

Requisição de logout:

```http
POST http://127.0.0.1:8000/api/accounts/logout/
```

O logout não precisa de corpo JSON. A resposta esperada é:

```json
{
  "message": "Logout realizado com sucesso.",
  "authenticated": false
}
```

Para confirmar, faça em seguida:

```http
GET http://127.0.0.1:8000/api/accounts/me/
```

A resposta esperada após o logout é status `401`:

```json
{
  "error": "Autenticacao obrigatoria."
}
```

Exemplo completo com `curl`, salvando e reutilizando o cookie:

```bash
curl -c cookies.txt -X POST http://127.0.0.1:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"maria\",\"password\":\"pass12345\"}"

curl -b cookies.txt -X POST http://127.0.0.1:8000/api/accounts/logout/
```

### Categorias

| Método | Endpoint                  | O que faz                                       |
| ------- | ------------------------- | ----------------------------------------------- |
| GET     | `/api/categories/`      | Lista categorias ativas.                        |
| POST    | `/api/categories/`      | Cria categoria. Apenas administradores.         |
| GET     | `/api/categories/<id>/` | Mostra uma categoria específica.               |
| PATCH   | `/api/categories/<id>/` | Edita uma categoria. Apenas administradores.    |
| DELETE  | `/api/categories/<id>/` | Desativa uma categoria. Apenas administradores. |

Exemplo de criação:

```json
{
  "name": "Workshop",
  "description": "Eventos práticos com participação dos alunos"
}
```

### Eventos

| Método | Endpoint                        | O que faz                                                              |
| ------- | ------------------------------- | ---------------------------------------------------------------------- |
| GET     | `/api/events/`                | Lista eventos publicados e futuros.                                    |
| POST    | `/api/events/`                | Cria um evento. Precisa estar logado.                                  |
| GET     | `/api/events/<id>/`           | Mostra detalhes de um evento publicado.                                |
| PATCH   | `/api/events/<id>/`           | Edita um evento. Apenas o organizador.                                 |
| DELETE  | `/api/events/<id>/`           | Exclui um evento. Apenas o organizador e sem inscrições confirmadas. |
| GET     | `/api/events/<id>/vacancies/` | Mostra quantas vagas ainda existem.                                    |
| GET     | `/api/events/<id>/comments/`  | Lista comentários do evento.                                          |
| POST    | `/api/events/<id>/comments/`  | Cria comentário. Precisa estar logado.                                |

Filtros disponíveis na listagem:

```text
/api/events/?category=1
/api/events/?search=python
```

Exemplo de criação de evento:

```json
{
  "category_id": 1,
  "title": "Python Day",
  "description": "Evento sobre Python e Django",
  "starts_at": "2026-07-20T19:00:00-03:00",
  "location": "Auditório principal",
  "max_capacity": 50,
  "status": "published"
}
```

### Inscrições

| Método | Endpoint                       | O que faz                                 |
| ------- | ------------------------------ | ----------------------------------------- |
| POST    | `/api/events/<id>/register/` | Inscreve o usuário logado no evento.     |
| POST    | `/api/events/<id>/cancel/`   | Cancela a inscrição do usuário logado. |

Regras importantes:

- O usuário precisa estar logado.
- O evento precisa estar publicado.
- O organizador não se inscreve no próprio evento.
- O mesmo usuário não pode ter duas inscrições confirmadas no mesmo evento.
- Se não houver vaga, a inscrição é recusada.

## Classes e funções principais

### `categories.models.Category`

Representa uma categoria de evento.

Campos principais:

- `name`: nome da categoria.
- `description`: explicação opcional.
- `is_active`: indica se a categoria aparece na API.
- `created_at`: data de criação.

### `events.models.Event`

Representa um evento criado por um organizador.

Campos principais:

- `organizer`: usuário que criou o evento.
- `category`: categoria do evento.
- `title`: título.
- `description`: descrição.
- `starts_at`: data e horário.
- `location`: local.
- `max_capacity`: quantidade máxima de pessoas.
- `cover_image`: URL opcional de imagem.
- `status`: `draft`, `published` ou `closed`.

Funções e propriedades:

- `clean()`: valida se a data é futura e se a capacidade é positiva.
- `confirmed_registrations_count`: conta inscrições confirmadas.
- `vacancies`: calcula vagas disponíveis.
- `has_vacancies`: informa se ainda há vaga.

### `events.models.Comment`

Representa um comentário feito em um evento.

Campos principais:

- `user`: autor do comentário.
- `event`: evento comentado.
- `content`: texto do comentário.
- `created_at`: data de criação.

### `registrations.models.Registration`

Representa a inscrição de um usuário em um evento.

Campos principais:

- `user`: usuário inscrito.
- `event`: evento escolhido.
- `status`: `confirmed` ou `canceled`.
- `registered_at`: data da inscrição.
- `updated_at`: última atualização.

Regra de banco:

- `unique_registration_per_user_event`: impede mais de um registro para o mesmo usuário no mesmo evento.

## Services

### `events.services.create_event()`

Cria um evento e executa as validações do model antes de salvar.

### `events.services.update_event()`

Atualiza um evento somente se o usuário for o organizador.

Também impede reduzir a capacidade para um número menor do que as inscrições confirmadas.

### `events.services.delete_event()`

Remove um evento somente se o usuário for o organizador.

Se já houver inscrição confirmada, o evento não é excluído.

### `events.services.published_events()`

Retorna apenas eventos publicados e com data futura.

### `events.services.get_published_event()`

Busca um evento publicado pelo `id`.

Se não encontrar, retorna erro 404.

### `events.services.create_comment()`

Cria comentário em um evento publicado.

### `events.services.close_past_events()`

Marca eventos antigos como encerrados.

Essa função pode ser usada futuramente em uma rotina automática.

### `registrations.services.register_user_for_event()`

Inscreve o usuário em um evento.

Ela verifica publicação, vagas, duplicidade e impede o organizador de se inscrever no próprio evento.

### `registrations.services.cancel_registration()`

Cancela uma inscrição confirmada.

## Views principais

### `accounts.views.RegisterView`

Recebe dados de cadastro e cria um usuário.

### `accounts.views.LoginView`

Recebe usuário e senha, autentica e cria uma sessão.

### `accounts.views.LogoutView`

Encerra a sessão atual.

### `accounts.views.MeView`

Mostra os dados básicos do usuário logado.

### `categories.views.CategoryListCreateView`

Lista categorias ativas e cria categorias quando o usuário é administrador.

### `categories.views.CategoryDetailView`

Mostra, altera ou desativa uma categoria específica.

### `events.views.EventListCreateView`

Lista eventos publicados e cria novos eventos.

### `events.views.EventDetailView`

Mostra detalhes, altera ou exclui um evento.

### `events.views.EventRegistrationView`

Chama o service que realiza inscrição no evento.

### `events.views.EventRegistrationCancelView`

Chama o service que cancela inscrição.

### `events.views.EventVacanciesView`

Retorna o número de vagas disponíveis.

### `events.views.EventCommentsView`

Lista e cria comentários.

## Funções auxiliares

### `config.api.json_body()`

Transforma o corpo JSON da requisição em um dicionário Python.

### `config.api.error_response()`

Transforma erros comuns em respostas JSON legíveis.

### `config.api.parse_required_datetime()`

Converte texto de data/hora para um objeto que o Django entende.

### `config.api.JsonLoginRequiredMixin`

Classe auxiliar para bloquear endpoints que exigem usuário logado.

## Testes

Os testes cobrem:

- criação de usuário;
- endpoint protegido por login;
- listagem de categorias;
- bloqueio de criação de categoria por usuário comum;
- criação de evento;
- recusa de evento com data passada;
- permissão de edição apenas para o organizador;
- listagem de eventos publicados;
- inscrição em evento;
- bloqueio de inscrição duplicada;
- bloqueio quando não há vagas;
- endpoint de inscrição exigindo login.

Comando:

```bash
python manage.py test
```

Resultado esperado:

```text
Ran 13 tests
OK
```
