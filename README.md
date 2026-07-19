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

`core` contém as páginas públicas comuns. `accounts` ficará responsável pelas contas. `profiles` guardará perfis profissionais. `taxonomy` organizará setores, áreas, especializações e competências.
