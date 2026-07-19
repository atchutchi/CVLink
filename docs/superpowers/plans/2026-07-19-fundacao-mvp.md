# Plano de implementação da fundação do MVP

> Para execução por agentes: usar obrigatoriamente `superpowers:executing-plans` e executar cada tarefa pela ordem indicada. Cada comportamento deve seguir o ciclo teste em falha, implementação mínima e teste a passar.

Objetivo: entregar uma aplicação Django funcional com autenticação por email, perfil privado automático, taxonomia administrável, página inicial responsiva e integração contínua.

Arquitetura: monólito Django com templates renderizados no servidor. As aplicações `accounts`, `profiles`, `taxonomy` e `core` separam responsabilidades e comunicam através de modelos e URLs internos.

Tecnologias: Python 3.13, Django 5.2 LTS, PostgreSQL, SQLite para desenvolvimento local, Bootstrap 5.3.8 e testes nativos do Django.

## Restrições globais

1. A interface e as mensagens ao utilizador usam português europeu.
2. O email é o identificador de autenticação.
3. O perfil nasce privado e no estado `draft`.
4. Segredos e configuração de produção não entram no Git.
5. O desenho é responsivo a partir de 360 píxeis.
6. O logótipo fornecido é usado como ativo da marca.
7. Esta fase não implementa pesquisa real nem publicação de perfis.

## Estrutura de ficheiros

`manage.py` inicia os comandos Django.

`config/settings.py` concentra configuração baseada no ambiente.

`config/urls.py` liga as rotas das aplicações e do admin.

`accounts/models.py` contém o utilizador e o respetivo gestor.

`accounts/forms.py` contém criação de conta e autenticação por email.

`accounts/views.py` contém registo e painel.

`profiles/models.py` contém o perfil profissional privado.

`profiles/signals.py` garante a criação automática do perfil.

`taxonomy/models.py` contém setor, área, especialização e competência.

`core/views.py` contém a página inicial.

`templates/` contém o layout, autenticação, painel e página inicial.

`static/` contém estilos, ícones e o logótipo.

## Tarefa 1: Base do projeto e configuração

Ficheiros:

1. Criar `requirements.txt`, `.env.example`, `.gitignore`, `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`, `config/asgi.py` e `config/wsgi.py`.
2. Criar `core/__init__.py`, `core/apps.py`, `core/views.py`, `core/urls.py` e `core/tests.py`.
3. Modificar `README.md`.

Interfaces:

1. `config.settings.database_config()` devolve o dicionário de configuração da base de dados.
2. `core.views.home(request)` devolve a página inicial com estado HTTP 200.

Passos:

1. Criar um ambiente virtual e instalar `Django==5.2.16`, `psycopg[binary]>=3.2,<3.4` e `Pillow>=11,<13`.
2. Escrever em `core/tests.py` um teste `HomeViewTests.test_home_page_is_available` que faz `self.client.get(reverse("home"))` e espera estado 200.
3. Executar `python manage.py test core` e confirmar a falha por ausência da rota ou da vista.
4. Criar a configuração mínima, a rota `path("", home, name="home")` e uma resposta renderizada por `core.views.home`.
5. Executar `python manage.py check` e `python manage.py test core` e confirmar sucesso.
6. Documentar instalação, variáveis, migrações e execução no README.
7. Fazer commit com a mensagem `chore: criar base do projeto Django`.

## Tarefa 2: Conta personalizada e autenticação

Ficheiros:

1. Criar `accounts/apps.py`, `accounts/managers.py`, `accounts/models.py`, `accounts/forms.py`, `accounts/views.py`, `accounts/urls.py`, `accounts/admin.py`, `accounts/tests/test_models.py` e `accounts/tests/test_auth.py`.
2. Criar `templates/registration/login.html`, `templates/registration/signup.html` e `templates/accounts/dashboard.html`.
3. Modificar `config/settings.py` e `config/urls.py`.

Interfaces:

1. `accounts.models.User` usa `email`, `first_name`, `last_name`, `is_active`, `is_staff`, `date_joined` e as permissões padrão.
2. `accounts.managers.UserManager.create_user(email, password=None, **extra_fields)` cria uma conta normal.
3. `accounts.managers.UserManager.create_superuser(email, password=None, **extra_fields)` cria uma conta administrativa.
4. `accounts.forms.SignUpForm` valida email único e duas palavras-passe.
5. As rotas nomeadas são `accounts:signup`, `login`, `logout` e `accounts:dashboard`.

Passos:

1. Escrever testes que exigem normalização do email, palavra-passe cifrada, email obrigatório e flags corretas no superutilizador.
2. Executar os testes dos modelos e confirmar falha por ausência do modelo personalizado.
3. Implementar `UserManager`, `User` e `AUTH_USER_MODEL = "accounts.User"`.
4. Criar e aplicar a primeira migração e repetir os testes dos modelos.
5. Escrever testes de registo, login por email, logout e redirecionamento do painel para utilizadores anónimos.
6. Executar os testes de autenticação e confirmar que falham por ausência dos fluxos.
7. Implementar formulários, vistas, URLs e templates mínimos.
8. Executar `python manage.py test accounts` e confirmar sucesso.
9. Fazer commit com a mensagem `feat: adicionar contas e autenticação`.

## Tarefa 3: Perfis privados e taxonomia

Ficheiros:

1. Criar `profiles/apps.py`, `profiles/models.py`, `profiles/signals.py`, `profiles/admin.py` e `profiles/tests/test_models.py`.
2. Criar `taxonomy/apps.py`, `taxonomy/models.py`, `taxonomy/admin.py` e `taxonomy/tests/test_models.py`.
3. Modificar `config/settings.py`.

Interfaces:

1. `profiles.models.Profile.Status` contém `DRAFT`, `PENDING`, `APPROVED`, `REJECTED`, `CHANGES_PENDING`, `SUSPENDED`, `ARCHIVED` e `DELETED`.
2. `Profile` contém `user`, `public_name`, `professional_title`, `bio`, `location`, `photo`, `status`, `is_public`, `specializations`, `skills`, `created_at` e `updated_at`.
3. `Sector`, `Area`, `Specialization` e `Skill` contêm `name`, `slug`, `is_active`, `created_at` e `updated_at`.
4. `Area` pertence a `Sector`, `Specialization` pertence a `Area` e `Skill` pode pertencer a várias especializações.

Passos:

1. Escrever testes para o estado inicial, privacidade, criação automática do perfil, unicidade de slugs e relações hierárquicas.
2. Executar os testes e confirmar falhas por ausência dos modelos.
3. Implementar os modelos, os sinais e o carregamento dos sinais em `ProfilesConfig.ready()`.
4. Criar e aplicar migrações.
5. Registar modelos no admin com pesquisa, filtros e preenchimento automático de slugs.
6. Executar `python manage.py test profiles taxonomy` e confirmar sucesso.
7. Fazer commit com a mensagem `feat: adicionar perfis e taxonomia`.

## Tarefa 4: Interface visual e identidade

Ficheiros:

1. Criar `templates/base.html`, `templates/core/home.html`, `static/css/app.css` e `static/img/cvlink-logo.png`.
2. Modificar templates de autenticação e painel.
3. Modificar `core/tests.py` e `accounts/tests/test_auth.py`.

Interfaces:

1. O layout fornece navegação responsiva, conteúdo principal e rodapé.
2. A pesquisa inicial usa um formulário GET com campo `q`, sem executar pesquisa nesta fase.
3. O painel mostra o estado do perfil da conta autenticada.

Passos:

1. Escrever testes para textos essenciais, campo de pesquisa, navegação autenticada e estado do perfil no painel.
2. Executar os testes e confirmar falha devido ao conteúdo em falta.
3. Copiar o logótipo fornecido para `static/img/cvlink-logo.png` sem alterar o original.
4. Implementar os templates com Bootstrap 5.3.8 e estilos próprios nas cores azul escuro e laranja da marca.
5. Garantir foco visível, etiquetas, texto alternativo, navegação por teclado e largura mínima de 360 píxeis.
6. Executar os testes de `core` e `accounts` e confirmar sucesso.
7. Fazer commit com a mensagem `feat: criar interface inicial do CVLink`.

## Tarefa 5: Qualidade, integração contínua e entrega

Ficheiros:

1. Criar `.github/workflows/tests.yml`.
2. Criar `tests/test_project_configuration.py`.
3. Modificar `README.md` e `.gitignore`.

Interfaces:

1. A integração contínua usa Python 3.13 e executa `python manage.py check` e `python manage.py test`.
2. A configuração de produção falha de forma explícita quando `SECRET_KEY` ou parâmetros necessários não são fornecidos.

Passos:

1. Escrever testes para hosts, base de dados configurável, diretórios de templates, ficheiros estáticos e modelo de utilizador.
2. Executar a suite e confirmar qualquer falha de configuração.
3. Completar a configuração mínima necessária para os testes passarem.
4. Executar `python manage.py makemigrations --check --dry-run`, `python manage.py check --deploy` com variáveis de produção de teste e `python manage.py test`.
5. Executar `git diff --check` e confirmar ausência de erros.
6. Atualizar o README com arquitetura, comandos e limites desta fase.
7. Fazer commit com a mensagem `ci: validar aplicação Django`.
8. Fazer push de todos os commits da fase para `origin/main`.

## Verificação final da fase

1. Todas as migrações estão versionadas.
2. Todos os testes passam num ambiente limpo.
3. Não existem segredos, base de dados local, uploads ou caches no Git.
4. A página inicial, registo, login, logout e painel funcionam.
5. O admin permite gerir contas, perfis e taxonomias.
6. O repositório remoto contém todos os commits da fase.
