# Desenho do perfil profissional completo

## Objetivo

Permitir que cada utilizador construa, guarde e submeta um perfil profissional completo sem o tornar público antes de aprovação administrativa.

## Domínio

O perfil principal recebe identificação profissional, localização, disponibilidade, preferências de trabalho, contactos, privacidade, currículo PDF e consentimentos. Experiência, formação, certificações e idiomas usam entidades próprias ligadas ao perfil.

O currículo aceita apenas PDF até 5 MB. Fica privado por defeito e nunca é exposto por uma rota pública nesta fase.

## Fluxo

O painel mostra a percentagem de conclusão e as secções em falta. O utilizador edita os dados principais e gere entradas repetíveis de experiência, formação, certificação e idioma. A submissão só é aceite quando os campos e secções mínimos estão preenchidos e os consentimentos obrigatórios foram registados.

Ao submeter, o perfil passa de `draft` ou `rejected` para `pending`. Perfis aprovados não são alterados diretamente nesta fase. Uma alteração futura usará `changes_pending` e revisão separada.

## Segurança

Todas as vistas exigem autenticação e filtram objetos pelo perfil da conta atual. Identificadores de terceiros devolvem 404. Uploads validam extensão, tipo declarado e tamanho. O nome público, telefone e currículo continuam privados.

## Testes

Os testes cobrem cálculo de conclusão, validação de PDF, propriedade dos registos, criação e eliminação das secções e regras de submissão.
