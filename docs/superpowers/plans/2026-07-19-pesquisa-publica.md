# Plano de implementação da pesquisa pública

> Para execução por agentes: usar obrigatoriamente `superpowers:executing-plans`. Cada tarefa usa teste em falha, implementação mínima, suite verde e commit.

Objetivo: entregar pesquisa filtrável e páginas públicas seguras para perfis aprovados e áreas ativas.

Arquitetura: `profiles.selectors` concentra a consulta pública. `profiles.public_views` trata pesquisa e detalhe. `taxonomy.views` serve o diretório de áreas. Templates próprios reutilizam o sistema visual e metadados do layout base.

Tecnologias: Django 5.2 LTS, ORM portátil para SQLite e PostgreSQL, Bootstrap 5.3 e testes nativos do Django.

## Tarefa 1: Identidade pública

Adicionar testes de slug estável e único em `profiles/tests/test_public_identity.py`. Adicionar `slug` ao perfil, gerar o valor no primeiro `save()` e criar migração. Confirmar que perfis com nomes iguais não colidem.

## Tarefa 2: Consulta e filtros

Adicionar testes em `profiles/tests/test_search.py` que criam perfis aprovados e privados. Exigir pesquisa por texto, competência e localização, exclusão de perfis não públicos e paginação. Implementar `public_profiles(params)` em `profiles/selectors.py`.

## Tarefa 3: Rotas e páginas

Adicionar testes para `/pesquisar/`, `/profissionais/<slug>/`, `/areas/` e `/areas/<slug>/`. Implementar vistas, URLs e templates com resultados, vazio, filtros persistentes, breadcrumbs e detalhe profissional.

## Tarefa 4: Integração visual e privacidade

Ligar a pesquisa da página inicial à rota real. Adicionar pesquisa e áreas à navegação. Garantir que email, telefone e currículo privados não aparecem no HTML público. Validar a interface a 375 píxeis e sem deslocamento horizontal.

## Tarefa 5: Entrega

Executar migrações, `python manage.py check`, `python manage.py test`, `git diff --check`, verificação no navegador e push para `origin/main`.
