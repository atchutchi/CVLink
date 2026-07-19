# Moderação administrativa do CVLink

## Objetivo

Criar uma área administrativa própria para analisar perfis pendentes, aplicar decisões de moderação e consultar o histórico de ações críticas.

## Decisões de desenho

- A área fica em `/administracao/` e exige `is_staff`.
- A aprovação torna o perfil público e regista o administrador e a data.
- A rejeição, o pedido de correção e a suspensão exigem um motivo.
- A suspensão desativa a conta. A restauração volta a ativá-la, mas não publica automaticamente o perfil.
- Todas as decisões criam um registo de auditoria imutável na aplicação.
- Apenas superadministradores consultam a auditoria completa.
- A gestão detalhada de utilizadores e taxonomia continua disponível no Django Admin, com ligações a partir do painel próprio.

## Estados e transições

- `pending` pode passar para `approved`, `rejected` ou `draft` por pedido de correção.
- `approved`, `pending` ou `rejected` podem passar para `suspended`.
- `suspended` pode ser restaurado para `draft`.
- Aprovar define `is_public=True`.
- Rejeitar, pedir correção, suspender ou restaurar define `is_public=False`.

## Auditoria

Cada ação guarda o ator, a ação, o tipo e identificador do alvo, a data e apenas contexto estruturado necessário. A interface não permite alterar nem eliminar registos.

## Interface

O painel mostra contadores por estado, uma fila de perfis pendentes e atalhos para utilizadores e taxonomia. A página de revisão apresenta os dados profissionais, currículo e ações válidas para o estado atual.

