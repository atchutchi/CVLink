# Interações privadas do CVLink

## Objetivo

Permitir que utilizadores autenticados guardem e valorizem perfis, contactem profissionais sem conhecer o respetivo email, denunciem abuso e recebam notificações internas.

## Modelos

- `Favorite`: relação única entre utilizador e perfil.
- `ProfileLike`: relação única entre utilizador e perfil.
- `ContactRequest`: assunto, mensagem, estado, remetente e perfil destinatário.
- `Report`: motivo, descrição, estado, atribuição e resolução administrativa.
- `Notification`: título, conteúdo, destino, tipo e data de leitura.

## Regras

- Todas as ações exigem autenticação e uma conta activa.
- Um utilizador não guarda, valoriza, contacta ou denuncia o próprio perfil.
- Favoritos e gostos funcionam como alternância por pedido POST.
- O contacto nunca expõe o email do profissional.
- Cada remetente pode enviar no máximo três pedidos ao mesmo perfil por hora.
- Assunto e mensagem são validados e o pedido fica registado.
- Só pode existir uma denúncia aberta ou em análise por utilizador e perfil.
- Um novo contacto ou denúncia cria uma notificação interna para o destinatário adequado.
- A resolução administrativa de denúncias cria auditoria e notifica o denunciante.

## Interface

O perfil público apresenta ações privadas. O painel pessoal mostra favoritos, contactos recebidos e notificações. O painel administrativo apresenta a fila de denúncias e o respectivo formulário de resolução.

## Limite conhecido

A confirmação formal do endereço de email será implementada na fase final de segurança. Nesta fase, o envio exige uma sessão autenticada e uma conta activa.

