# Plano de implementação do perfil profissional

> Para execução por agentes: usar obrigatoriamente `superpowers:executing-plans`. Executar cada comportamento com teste em falha, implementação mínima e teste a passar.

Objetivo: entregar edição completa e privada do perfil, secções curriculares, upload PDF e submissão para aprovação.

Arquitetura: modelos focados na aplicação `profiles`, formulários Django com validação do lado do servidor e vistas protegidas por propriedade. Templates renderizados no servidor reutilizam o sistema visual atual.

Tecnologias: Django 5.2 LTS, armazenamento local em desenvolvimento, PostgreSQL em produção e testes nativos do Django.

## Tarefa 1: Expandir o domínio

Criar testes em `profiles/tests/test_profile_completion.py` para os campos obrigatórios, percentagem e secções em falta. Criar testes em `profiles/tests/test_resume.py` para PDF, tipo e limite de 5 MB. Implementar os novos campos de `Profile` e os modelos `Experience`, `Education`, `Certification` e `ProfileLanguage`. Criar migração e confirmar a suite.

## Tarefa 2: Editar dados principais

Criar testes em `profiles/tests/test_views.py` para acesso autenticado, gravação de dados, proteção contra contas alheias e upload. Implementar `ProfileForm`, rota `profiles:edit` e template `profiles/edit.html`.

## Tarefa 3: Gerir secções repetíveis

Criar testes de criação e eliminação para experiência, formação, certificação e idioma. Implementar formulários e vistas genéricas que recebem apenas modelos permitidos e filtram sempre pelo perfil autenticado. Criar templates de lista, formulário e confirmação.

## Tarefa 4: Submeter para aprovação

Criar testes para bloqueio de perfil incompleto, consentimentos obrigatórios e transição para `pending`. Implementar a rota POST `profiles:submit` e atualizar o painel com progresso, secções em falta e ação de submissão.

## Tarefa 5: Verificar e publicar

Executar migrações, `python manage.py check`, `python manage.py test`, validação de uploads, teste visual móvel e `git diff --check`. Fazer commits por unidade e push da fase para `origin/main`.
