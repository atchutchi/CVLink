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

## Estrutura inicial

`core` contém as páginas públicas comuns. `accounts` gere a conta personalizada e a autenticação por email. `profiles` guarda os perfis profissionais privados. `taxonomy` organiza setores, áreas, especializações e competências.

## Funcionalidades disponíveis

1. Página inicial responsiva com identidade CVLink.
2. Criação de conta e autenticação por email.
3. Painel protegido do utilizador.
4. Perfil privado criado automaticamente em estado de rascunho.
5. Taxonomia extensível gerida através do Django Admin.
6. Configuração para SQLite e PostgreSQL.
7. Testes automáticos e validação contínua no GitHub.

## Limites da fundação

A pesquisa apresentada na página inicial é visual. Os resultados, edição completa do perfil, currículo, submissão para aprovação, contacto e favoritos serão introduzidos nas fases seguintes.

## Administração

Cria uma conta administrativa e inicia sessão em `http://127.0.0.1:8000/admin/`.

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Segurança de produção

Quando `DEBUG=False`, a variável `SECRET_KEY` é obrigatória. A aplicação ativa redirecionamento HTTPS, cookies seguros e HSTS. Define `ALLOWED_HOSTS` antes do arranque.
