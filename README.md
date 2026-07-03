# Sextou - Backend em Django

Backend da plataforma **Sextou**, para criação de eventos, organização por categorias, inscrição de usuários e comentários. É um projeto 100% API (JSON), sem telas HTML — o frontend (React/Vite) consome os endpoints separadamente.

> Este README foi atualizado a partir da leitura completa do código-fonte atual (`config`, `accounts`, `categories`, `events`, `registrations`). Ele substitui a versão anterior, que descrevia um fluxo de autenticação por sessão que não existe mais no código.

## Stack tecnológica

| Componente | Versão | Uso |
| --- | --- | --- |
| Python | 3.12 | linguagem |
| Django | 5.0.6 | framework web |
| djangorestframework | 3.15.1 | camada de API REST |
| djangorestframework-simplejwt | 5.5.1 | autenticação via JWT |
| django-cors-headers | 4.3.1 | liberação de CORS para o frontend |
| Pillow | 10.3.0 | suporte a upload de imagem (`ImageField`) |
| python-dotenv | 1.0.1 | carrega variáveis de `.env` automaticamente |
| SQLite | - | banco de dados local (`db.sqlite3`) |

## Estrutura do projeto

```text
config/          Settings, roteamento raiz e tratamento global de exceções da API.
accounts/        Cadastro de usuário, login/refresh JWT e dados do usuário logado.
categories/      Categorias usadas para classificar eventos (somente leitura via API).
events/          Eventos, comentários, vagas, inscrição/cancelamento (via ações do ViewSet).
registrations/   Listagem das inscrições do usuário logado.
```

Convenções internas:

- `views.py` — recebe a requisição HTTP, aplica permissões e chama serializer/service.
- `serializers.py` — validação e formatação de entrada/saída (equivalente a DTOs).
- `services.py` (em `events`) — regra de negócio isolada da view, para facilitar testes.
- `permissions.py` (em `events`) — regras de autorização por objeto.
- `migrations/` — evolução do schema do banco.

## Como rodar o projeto

1. Crie e ative um ambiente virtual (opcional, mas recomendado):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Copie o arquivo de variáveis de ambiente e ajuste os valores:

```bash
cp .env.example .env
```

```text
# .env
DJANGO_SECRET_KEY=
FRONTEND_URL=http://localhost:5173
```

`config/settings.py` carrega esse arquivo automaticamente via `python-dotenv` (`load_dotenv(BASE_DIR / ".env")`). Se `DJANGO_SECRET_KEY` ficar em branco, o projeto usa uma chave fixa de desenvolvimento definida no próprio `config/settings.py` — **não usar em produção**. Para gerar uma chave segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

`FRONTEND_URL` define qual origem é liberada no CORS (ver seção [Configurações relevantes](#configurações-relevantes-configsettingspy)); se não for definida, o padrão é `http://localhost:5173` (porta padrão do Vite).

4. Crie o banco de dados local e aplique as migrações (a migração de `categories` já popula categorias padrão: Festa, Show, Workshop, Esporte, Gastronomia, Tech & Talks):

```bash
python manage.py migrate
```

5. (Opcional) crie um superusuário para acessar o `/admin/`:

```bash
python manage.py createsuperuser
```

6. Inicie o servidor:

```bash
python manage.py runserver
```

A API fica disponível em `http://127.0.0.1:8000/`.

## Configurações relevantes (`config/settings.py`)

- `DEBUG = True` e `ALLOWED_HOSTS = ["*"]` — configuração de desenvolvimento, não deve ir para produção assim.
- `CORS_ALLOWED_ORIGINS = [FRONTEND_URL]` com `CORS_ALLOW_CREDENTIALS = True` — `FRONTEND_URL` vem da variável de ambiente (`.env`), com padrão `http://localhost:5173` (porta padrão do Vite) se não for definida. Para liberar outra origem (ex.: deploy do frontend), basta ajustar `FRONTEND_URL` no `.env` — hoje só é possível uma origem por vez, já que a lista sempre tem um único item.
- `TIME_ZONE = "America/Sao_Paulo"`, `USE_TZ = True` — datas são armazenadas em UTC e convertidas; ao enviar `data_hora`, inclua o offset (ex.: `-03:00`).
- `DEFAULT_PAGINATION_CLASS` = `PageNumberPagination` com `PAGE_SIZE = 10` — todas as views de listagem baseadas em `generics.ListAPIView`/`ModelViewSet.list` são paginadas (ver seção [Paginação](#paginação)).
- `LOGGING` configurado para exibir no console mensagens `DEBUG` de `rest_framework` e `rest_framework_simplejwt`, além de `INFO` do Django — útil para depurar problemas de autenticação.
- Uploads de imagem (`imagem_capa` de `Event`) vão para `media/capas/`, servidos via `MEDIA_URL = "media/"`.

## Autenticação

O projeto usa **JWT** via `djangorestframework-simplejwt`. Não existe mais autenticação por sessão/cookie nem endpoint de logout no backend — o token é stateless (não há `token_blacklist` instalado), então "logout" é responsabilidade do frontend (descartar o token salvo).

Fluxo:

1. `POST /accounts/register/` — cria o usuário.
2. `POST /accounts/login/` — autentica e devolve um par de tokens (`access` e `refresh`).
3. Nas próximas requisições autenticadas, envie o header:

   ```http
   Authorization: Bearer <access_token>
   ```

4. Quando o `access` expirar, use `POST /accounts/token/refresh/` enviando o `refresh` para obter um novo `access`.

O `access_token` e o `refresh_token` usam a duração padrão do SimpleJWT (não há bloco `SIMPLE_JWT` customizado em `settings.py`): access token válido por 5 minutos, refresh token por 1 dia, sem rotação automática.

### Endpoints de conta

| Método | Endpoint | Autenticação | O que faz |
| --- | --- | --- | --- |
| POST | `/accounts/register/` | pública | Cria um usuário. |
| POST | `/accounts/login/` | pública | Autentica e retorna `access`/`refresh`. |
| POST | `/accounts/token/refresh/` | pública | Troca um `refresh` válido por um novo `access`. |
| GET | `/accounts/me/` | obrigatória | Retorna dados do usuário logado. |

Exemplo de cadastro:

```json
POST /accounts/register/
{
  "username": "maria",
  "email": "maria@example.com",
  "password": "pass12345",
  "first_name": "Maria"
}
```

Resposta (`201`):

```json
{
  "id": 1,
  "username": "maria",
  "email": "maria@example.com",
  "first_name": "Maria",
  "nome": "Maria"
}
```

> Validação própria em `UserRegisterSerializer.validate_email`: recusa (`400`) se já existir um usuário com o mesmo e-mail **ou** o mesmo username.

Exemplo de login:

```json
POST /accounts/login/
{ "username": "maria", "password": "pass12345" }
```

Resposta (`200`):

```json
{
  "refresh": "eyJhbGciOi...",
  "access": "eyJhbGciOi..."
}
```

Exemplo de uso do token:

```bash
curl http://127.0.0.1:8000/accounts/me/ \
  -H "Authorization: Bearer eyJhbGciOi..."
```

## Endpoints da API

Todas as rotas abaixo (exceto `/accounts/...` e `/admin/`) ficam sob o prefixo `/api/`.

### Categorias

| Método | Endpoint | Autenticação | O que faz |
| --- | --- | --- | --- |
| GET | `/api/categories/` | pública | Lista todas as categorias (paginado). |

Não há endpoints de criação/edição/remoção de categoria pela API — isso só é feito pelo painel `/admin/`.

Formato de item:

```json
{ "id": 1, "nome": "Workshop", "slug": "workshop" }
```

### Eventos

Roteados via `DefaultRouter` (`events.urls`), registrados em `EventViewSet`.

| Método | Endpoint | Autenticação | O que faz |
| --- | --- | --- | --- |
| GET | `/api/events/` | pública | Lista **todos** os eventos (qualquer status), paginado. |
| POST | `/api/events/` | obrigatória | Cria um evento; o usuário logado vira o `organizador`. |
| GET | `/api/events/<id>/` | pública | Detalhe de um evento. |
| PUT/PATCH | `/api/events/<id>/` | apenas organizador | Edita o evento. |
| DELETE | `/api/events/<id>/` | apenas organizador | Exclui o evento. |
| GET | `/api/events/<id>/vacancies/` | pública | Retorna `vagas_disponiveis`. |
| POST | `/api/events/<id>/register/` | obrigatória | Inscreve o usuário logado no evento. |
| DELETE | `/api/events/<id>/cancel/` | obrigatória | Cancela a inscrição do usuário logado. |
| GET | `/api/events/<id>/comments/` | pública | Lista comentários do evento (não paginado). |
| POST | `/api/events/<id>/comments/` | obrigatória | Cria um comentário no evento. |

Permissões: `IsAuthenticatedOrReadOnly` + `IsOrganizerOrReadOnly` — leitura (`GET`) é sempre pública; qualquer escrita exige login, e editar/excluir exige ser o organizador do evento (verificado objeto a objeto).

Exemplo de criação de evento:

```json
POST /api/events/
Authorization: Bearer <access>
{
  "titulo": "Python Day",
  "descricao": "Evento sobre Python e Django",
  "data_hora": "2026-07-20T19:00:00-03:00",
  "local": "Auditório principal",
  "capacidade_maxima": 50,
  "categoria": "tech",
  "status": "publicado"
}
```

`categoria` é referenciada pelo **slug** (não pelo id). `status` aceita `rascunho`, `publicado` ou `encerrado` (padrão: `publicado`).

Para enviar `imagem_capa`, use `multipart/form-data` em vez de JSON.

Resposta (exemplo simplificado):

```json
{
  "id": 10,
  "titulo": "Python Day",
  "descricao": "Evento sobre Python e Django",
  "data_hora": "2026-07-20T19:00:00-03:00",
  "local": "Auditório principal",
  "capacidade_maxima": 50,
  "imagem_capa": null,
  "status": "publicado",
  "criado_em": "2026-07-03T13:00:00-03:00",
  "organizador": "maria",
  "categoria": "tech",
  "inscritos": 0,
  "ja_inscrito": false,
  "comentarios": []
}
```

Filtros: **não há** filtro por categoria ou busca por texto implementado atualmente na listagem de eventos (`/api/events/`) — a listagem retorna todos os eventos, de qualquer status e data, apenas paginados.

### Inscrições (ações do evento)

| Ação | Endpoint | Regras aplicadas (`events/services.py`) |
| --- | --- | --- |
| Inscrever-se | `POST /api/events/<id>/register/` | Se já existir inscrição `confirmada` → erro `inscricao_duplicada`. Se não houver vaga (`vagas_disponiveis <= 0`) → erro `evento_lotado`. Se existir inscrição `cancelada` anterior, ela é reaproveitada e marcada como `confirmada`. Caso contrário, cria uma nova inscrição. |
| Cancelar inscrição | `DELETE /api/events/<id>/cancel/` | Precisa existir inscrição `confirmada` para esse usuário/evento; caso contrário, erro `inscricao_nao_encontrada`. Ao cancelar, o status vira `cancelada` (o registro não é apagado). |

> Atenção: atualmente **não há** verificação impedindo o organizador de se inscrever no próprio evento, nem validação de evento "publicado" antes de inscrever — qualquer usuário autenticado pode se inscrever em qualquer evento, de qualquer status, desde que haja vaga.

### Minhas inscrições

| Método | Endpoint | Autenticação | O que faz |
| --- | --- | --- | --- |
| GET | `/api/registrations/me/` | obrigatória | Lista as inscrições do usuário logado (com o evento completo aninhado), paginado. |

Formato de item:

```json
{
  "id": 3,
  "evento": { "...": "objeto completo do evento, igual ao de /api/events/<id>/" },
  "status": "confirmada",
  "data_inscricao": "2026-07-03T13:05:00-03:00"
}
```

### Comentários

| Método | Endpoint | Autenticação | O que faz |
| --- | --- | --- | --- |
| GET | `/api/events/<id>/comments/` | pública | Lista comentários do evento, do mais antigo para o mais novo. |
| POST | `/api/events/<id>/comments/` | obrigatória | Cria comentário (`texto` obrigatório e não vazio). |

Exemplo:

```json
POST /api/events/10/comments/
Authorization: Bearer <access>
{ "texto": "Muito bom esse evento!" }
```

Resposta (`201`):

```json
{ "id": 5, "autor": "maria", "texto": "Muito bom esse evento!", "data": "2026-07-03T13:10:00-03:00" }
```

Se `texto` vier vazio ou só com espaços, o backend responde `400` com `{"detail": "O comentario nao pode estar vazio."}`.

## Modelos de dados

### `categories.Category`

| Campo | Tipo | Observações |
| --- | --- | --- |
| `nome` | `CharField(60)` | único. |
| `slug` | `SlugField(60)` | único; usado como identificador em `Event.categoria`. |

### `events.Event`

| Campo | Tipo | Observações |
| --- | --- | --- |
| `titulo` | `CharField(140)` | |
| `descricao` | `TextField` | |
| `data_hora` | `DateTimeField` | sem validação de data futura no código atual. |
| `local` | `CharField(200)` | |
| `capacidade_maxima` | `PositiveIntegerField` | sem validação explícita de mínimo além do tipo do campo. |
| `imagem_capa` | `ImageField` (opcional) | salva em `media/capas/`. |
| `status` | `CharField` | `rascunho`, `publicado` (padrão) ou `encerrado` — o valor não altera o comportamento de nenhum endpoint hoje (é apenas informativo). |
| `criado_em` | `DateTimeField` | preenchido automaticamente. |
| `organizador` | FK para `User` | `on_delete=CASCADE`. |
| `categoria` | FK para `Category` | `on_delete=PROTECT` (não é possível apagar uma categoria com eventos vinculados). |

Propriedades calculadas: `inscritos` (contagem de inscrições `confirmada`) e `vagas_disponiveis` (`capacidade_maxima - inscritos`, nunca negativo).

### `events.Comment`

| Campo | Tipo | Observações |
| --- | --- | --- |
| `evento` | FK para `Event` | `on_delete=CASCADE`, `related_name="comentarios"`. |
| `autor` | FK para `User` | `on_delete=CASCADE`. |
| `texto` | `TextField` | validado no service (`criar_comentario`) contra texto vazio. |
| `data` | `DateTimeField` | preenchido automaticamente. |

### `registrations.Registration`

| Campo | Tipo | Observações |
| --- | --- | --- |
| `usuario` | FK para `User` | `on_delete=CASCADE`. |
| `evento` | FK para `Event` | `on_delete=CASCADE`. |
| `status` | `CharField` | `confirmada` (padrão) ou `cancelada`. |
| `data_inscricao` | `DateTimeField` | preenchido automaticamente. |

Restrição de banco: `unique_together = ("usuario", "evento")` — só pode existir **um** registro por par usuário/evento (cancelamentos reutilizam a mesma linha em vez de criar uma nova).

## Regras de negócio (`events/services.py`)

| Função | Responsabilidade |
| --- | --- |
| `inscrever_usuario(evento, usuario)` | Cria/reativa a inscrição do usuário no evento, validando duplicidade e vagas. Executa em transação (`@transaction.atomic`). |
| `cancelar_inscricao(evento, usuario)` | Marca a inscrição confirmada como `cancelada`. Falha se não houver inscrição confirmada. |
| `listar_comentarios(evento)` | Retorna os comentários do evento (com `select_related("autor")`). |
| `criar_comentario(evento, autor, texto)` | Valida texto não vazio e cria o comentário. |

## Tratamento de erros

### Erros de autenticação (401) — normalizados globalmente

`config/exceptions.py` define `api_exception_handler`, configurado em `REST_FRAMEWORK.EXCEPTION_HANDLER`. Ele intercepta **qualquer** resposta `401` (token ausente, inválido ou expirado) e a reescreve em um formato único:

```json
{
  "detail": "Sua sessao expirou ou o token de acesso e invalido. Faca login novamente.",
  "code": "token_not_valid",
  "action": "login_required"
}
```

- `code` vem do erro original do SimpleJWT quando disponível (`token_not_valid`, etc.); se não houver código explícito (ex.: nenhum header `Authorization` enviado), cai no valor padrão `"authentication_failed"`.
- `action: "login_required"` é um sinal para o frontend redirecionar para a tela de login.

Esse tratamento **só se aplica a respostas 401**. Outros status (400, 403, 404) mantêm o formato padrão do Django REST Framework.

### Erros de negócio (400) — exceções customizadas

Definidas em `events/services.py`, todas como subclasses de `APIException` com `status_code = 400`:

| Exceção | `default_detail` | Quando ocorre |
| --- | --- | --- |
| `CapacidadeError` | "Evento lotado." | Tentativa de inscrição sem vagas disponíveis. |
| `InscricaoDuplicadaError` | "Voce ja esta inscrito." | Tentativa de inscrição já confirmada anteriormente. |
| `InscricaoNaoEncontradaError` | "Voce nao possui inscricao neste evento." | Tentativa de cancelar sem inscrição confirmada. |
| `ComentarioVazioError` | "O comentario nao pode estar vazio." | Comentário enviado sem texto (ou só espaços). |

Essas exceções resultam em respostas no formato padrão do DRF, por exemplo:

```json
{ "detail": "Voce ja esta inscrito." }
```

### Erros de validação de payload (400) — criação/edição de evento

`EventViewSet.create` e `EventViewSet.update` não deixam o DRF gerar a resposta padrão de validação; eles capturam `serializer.errors` manualmente, logam um `logger.warning` e retornam:

```json
{
  "detail": "Nao foi possivel criar o evento.",
  "errors": {
    "categoria": ["Object with slug=inexistente does not exist."]
  }
}
```

(o mesmo formato vale para update, trocando a mensagem para "Nao foi possivel atualizar o evento.")

### Outros erros padrão do DRF (não customizados)

- **403** ao tentar editar/excluir evento de outro organizador — mensagem padrão do DRF de permissão negada.
- **404** ao acessar `/api/events/<id>/...` com id inexistente — mensagem padrão `{"detail": "Not found."}`.
- **400** de `django.core.exceptions.ObjectDoesNotExist` no relacionamento `categoria` (slug inexistente) durante criação/edição — capturado como erro de validação do serializer (ver acima).

## Paginação

`DEFAULT_PAGINATION_CLASS = PageNumberPagination`, `PAGE_SIZE = 10`. Afeta:

- `GET /api/events/` (listagem do `EventViewSet`)
- `GET /api/categories/`
- `GET /api/registrations/me/`

Formato de resposta paginada:

```json
{
  "count": 23,
  "next": "http://127.0.0.1:8000/api/events/?page=2",
  "previous": null,
  "results": [ "..." ]
}
```

`GET /api/events/<id>/comments/` **não** é paginado (é uma `@action` que devolve a lista completa).

## CORS

Somente `http://localhost:5173` (padrão do Vite) está liberado em `CORS_ALLOWED_ORIGINS`, com `CORS_ALLOW_CREDENTIALS = True`. Para rodar o frontend em outra porta/host, adicione a origem em `config/settings.py`.

## Painel administrativo

`/admin/` expõe `Category`, `Event`, `Comment` e `Registration` (registrados via `admin.site.register` simples, sem customização de `ModelAdmin`). É o único lugar para criar/editar/remover categorias hoje, já que a API só oferece leitura.

## Testes

O projeto **não possui testes automatizados no momento** — não há nenhum arquivo `tests.py` em nenhum app. Antes de alterações relevantes, recomenda-se testar manualmente os fluxos (registro, login, criação de evento, inscrição, cancelamento, comentário) via `curl`/Postman/Insomnia.

## Pontos de atenção conhecidos

Levantados durante a leitura do código atual, úteis para próximos ajustes:

- `data_hora` de um evento não é validada contra o passado — é possível criar eventos com data já vencida.
- `capacidade_maxima` não tem validação de negócio além do tipo (`PositiveIntegerField`), e reduzir a capacidade abaixo do número de inscritos confirmados não é bloqueado na atualização do evento.
- `DELETE /api/events/<id>/` não verifica se existem inscrições confirmadas antes de excluir o evento.
- `POST /api/events/<id>/register/` não impede o organizador de se inscrever no próprio evento, nem exige que o evento esteja com `status = "publicado"`.
- `GET /api/events/` lista eventos de qualquer status (inclusive `rascunho` e `encerrado`), sem filtro de data ou de categoria/busca por texto.
- Não há endpoint de logout/blacklist de token — o app `rest_framework_simplejwt.token_blacklist` não está instalado.
- `SECRET_KEY` tem um valor padrão embutido no código, usado apenas quando `DJANGO_SECRET_KEY` não está definida no ambiente — não usar esse padrão fora de desenvolvimento local.
