# CVLink

Diretório profissional para ligar talentos a oportunidades.

## Requisitos

Python 3.10 ou superior e PostgreSQL para ambientes partilhados. O desenvolvimento local usa SQLite por defeito.

## Instalação local

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

A aplicação fica disponível em `http://127.0.0.1:8000/`.

## Configuração

As variáveis suportadas estão documentadas em `.env.example`. O projeto lê variáveis do processo.

Para PostgreSQL, define `DATABASE_ENGINE=postgresql` e preenche as variáveis `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST` e `DATABASE_PORT`.

## Testes

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

## Estrutura

`core` contém as páginas públicas e os endpoints operacionais. `accounts` gere autenticação e confirmação de email. `profiles` gere perfis e revisões. `taxonomy` organiza setores, áreas, especializações e competências. `moderation` concentra decisões administrativas e auditoria. `interactions` gere favoritos, gostos, contactos, denúncias e notificações.

## Funcionalidades disponíveis

1. Conta com confirmação de email, recuperação e alteração de palavra-passe.
2. Perfil completo com currículo PDF, pré-visualização e histórico de revisão.
3. Pesquisa pública, filtros, áreas e páginas profissionais.
4. Moderação, denúncias e auditoria administrativa.
5. Favoritos, gostos, contacto protegido e notificações.
6. Sitemap, robots.txt, metadados sociais e dados estruturados.
7. Configuração para SQLite e PostgreSQL, testes e integração contínua.

## Administração

Cria uma conta administrativa e inicia sessão em `http://127.0.0.1:8000/admin/`.

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Segurança de produção

Quando `DEBUG=False`, a variável `SECRET_KEY` é obrigatória. A aplicação activa redireccionamento HTTPS, cookies seguros e HSTS. Define `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` antes do arranque.

Configura um serviço SMTP através das variáveis `EMAIL_*`. O backend de consola serve apenas para desenvolvimento. Num ambiente com vários processos, substitui a cache local por um serviço partilhado para manter a limitação de login consistente.

Antes de publicar executa:

```powershell
$env:DEBUG='False'
$env:SECRET_KEY='uma-chave-longa-e-aleatoria'
$env:ALLOWED_HOSTS='cvlink.example.com'
.\.venv\Scripts\python.exe manage.py check --deploy
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

O endpoint `/saude/` valida a aplicação e a ligação à base de dados. O servidor `runserver` destina-se apenas ao desenvolvimento. Em produção usa um servidor WSGI ou ASGI, armazenamento persistente para ficheiros e cópias de segurança da base de dados.
