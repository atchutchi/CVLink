# Qualidade final e fecho do MVP

## Auditoria de lacunas

O produto cobre o núcleo de perfis, pesquisa, moderação e interações. O fecho do MVP exige ainda completar a gestão de conta, a confirmação de email, a recuperação de palavra-passe, a pré-visualização privada, o fluxo seguro de alterações aprovadas e os requisitos técnicos de SEO.

## Bloco A: conta e segurança

- Guardar `email_verified_at`.
- Confirmar email com token temporário de uso único e permitir novo envio.
- Bloquear a submissão e o contacto enquanto o email não estiver confirmado.
- Disponibilizar recuperação e alteração de palavra-passe com respostas sem enumeração de contas.
- Permitir editar nome e email com nova confirmação quando o email muda.
- Permitir desactivar a conta após validação da palavra-passe.
- Limitar tentativas repetidas de início de sessão.

## Bloco B: integridade do perfil

- Criar pré-visualização privada e não indexável.
- Validar intervalos de datas.
- Permitir editar entradas repetíveis.
- Guardar uma versão pública aprovada separada das alterações em revisão.
- Manter a versão pública anterior durante a revisão e em caso de rejeição.
- Alinhar o limite do currículo com 10 MB e manter acesso privado por defeito.

## Bloco C: SEO e operação

- Adicionar canonical, Open Graph e regras `robots` por página.
- Adicionar dados estruturados para perfis públicos e página inicial.
- Criar `sitemap.xml` e `robots.txt` apenas com páginas indexáveis.
- Criar endpoint de saúde.
- Rever cabeçalhos, cookies, formulários, foco, contraste, teclado e largura mínima de 360 px.
- Documentar configuração de produção e variáveis de ambiente.

## Critério de conclusão

O MVP só é considerado concluído após testes automatizados, controlo de migrações, verificação de segurança do Django, validação visual em desktop e telemóvel e confirmação de que o ramo remoto está sincronizado.

