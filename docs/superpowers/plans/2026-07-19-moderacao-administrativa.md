# Plano de implementação da moderação administrativa

## Tarefa 1: domínio e migração

- Criar testes para metadados de revisão e registos de auditoria.
- Adicionar ao perfil os campos de decisão administrativa.
- Criar o modelo imutável `AuditLog`.
- Gerar e validar a migração.

## Tarefa 2: serviço de moderação

- Criar testes para aprovação, rejeição, pedido de correção, suspensão e restauração.
- Implementar transições explícitas e validação obrigatória do motivo.
- Registar cada decisão num `AuditLog`.

## Tarefa 3: painel administrativo

- Criar testes de autorização, fila, revisão e decisões por POST.
- Implementar painel, lista de perfis, detalhe de revisão e auditoria.
- Restringir a auditoria completa a superadministradores.

## Tarefa 4: interface e administração Django

- Criar páginas responsivas para painel, fila, revisão e auditoria.
- Tornar os campos de decisão e auditoria apenas de leitura no Django Admin.
- Adicionar navegação administrativa para utilizadores e taxonomia.

## Tarefa 5: verificação e publicação

- Executar testes, verificação do Django e controlo de migrações.
- Validar o percurso principal no navegador em formato desktop e móvel.
- Criar o commit funcional e publicar no ramo principal.

