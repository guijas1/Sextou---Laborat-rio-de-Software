# Organizacao do backend

Este backend segue a organizacao natural do Django: cada dominio da aplicacao fica
em um app independente. Para quem vem de Java/Spring, a leitura aproximada e:

| Django | Papel parecido no Spring |
| --- | --- |
| `views.py` | Controller / endpoints HTTP |
| `serializers.py` | DTO + validacao de entrada/saida |
| `services.py` | Regras de negocio / casos de uso |
| `models.py` | Entidades ORM |
| `urls.py` | Rotas do modulo |
| `permissions.py` | Autorizacao |
| `migrations/` | Evolucao do schema do banco |

## Apps

- `accounts/`: cadastro, login JWT e usuario autenticado.
- `categories/`: categorias usadas pelos eventos.
- `events/`: eventos, comentarios, vagas e inscricoes via acoes do evento.
- `registrations/`: listagem das inscricoes do usuario logado.
- `config/`: configuracao global do Django, URLs raiz e tratamento padrao de erros.

## Convencoes usadas

- Views devem coordenar HTTP: ler request, chamar serializer/service e devolver response.
- Services concentram regra de negocio que pode crescer ou ser testada isoladamente.
- Serializers nao devem executar regra pesada; eles formatam e validam payloads.
- Arquivos locais como `.venv/`, `db.sqlite3`, `__pycache__/` e `.env` ficam fora do Git.

## Fluxo exemplo: inscricao em evento

1. `events/urls.py` registra o `EventViewSet`.
2. `EventViewSet.register()` recebe `POST /api/events/{id}/register/`.
3. A view chama `events.services.inscrever_usuario()`.
4. O service valida duplicidade, capacidade e salva a inscricao.
5. A view retorna a resposta HTTP para o frontend.
