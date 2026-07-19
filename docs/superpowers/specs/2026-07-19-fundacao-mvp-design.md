# Desenho da fundação do MVP CVLink

## Objetivo

Criar a base técnica inicial do CVLink para suportar contas, perfis profissionais privados, uma taxonomia extensível e administração segura. Esta fase não publica perfis nem implementa a pesquisa funcional.

## Arquitetura

O sistema será um monólito Django com templates renderizados no servidor, Bootstrap e PostgreSQL em produção. O desenvolvimento local pode usar SQLite através de configuração por variáveis de ambiente.

O projeto será dividido nas seguintes aplicações:

1. `accounts` para o modelo de utilizador personalizado, autenticação e painel inicial.
2. `profiles` para o perfil profissional e o respetivo estado de moderação.
3. `taxonomy` para setor, área, especialização e competência.
4. `core` para a página inicial e componentes comuns.

## Componentes e responsabilidades

O modelo de utilizador personalizado será definido antes da primeira migração. Usará email como identificador de autenticação e manterá os campos necessários para permissões administrativas do Django.

Cada conta terá um perfil profissional associado por relação um para um. O perfil será criado automaticamente após a criação da conta. O estado inicial será `draft` e o perfil não será público nesta fase.

O perfil terá nome público, título profissional, biografia, localização e fotografia opcional. A representação pública, submissão para aprovação, upload de currículo, contacto, favoritos e pesquisa ficam fora do âmbito desta entrega.

A taxonomia terá quatro entidades independentes e extensíveis: setor, área, especialização e competência. A relação será setor para área, área para especialização e especialização para competência. Um perfil poderá ter várias especializações e competências.

O Django Admin será a interface inicial de administração. Apenas utilizadores com permissões de equipa terão acesso à gestão das taxonomias e dos perfis.

A página inicial será responsiva e usará o logótipo fornecido do CVLink. Mostrará uma pesquisa visual sem resultados funcionais, uma explicação clara do produto e ligações para criar conta e iniciar sessão.

## Fluxos

1. Um visitante abre a página inicial e pode iniciar sessão ou criar conta.
2. A criação de conta valida email e palavra-passe e cria um perfil profissional em rascunho.
3. Um utilizador autenticado acede ao painel inicial protegido.
4. Um administrador gere setores, áreas, especializações e competências no Django Admin.

## Segurança e erros

As palavras-passe serão tratadas pelos mecanismos do Django. As páginas protegidas exigirão autenticação. A administração exigirá permissões de equipa. Erros de formulários serão apresentados de forma clara e não exporão dados sensíveis.

Segredos e parâmetros de ambiente serão carregados por variáveis de ambiente e não serão guardados no Git. A configuração de produção será preparada para PostgreSQL, hosts permitidos e cookies seguros.

## Testes e validação

Os testes automatizados cobrirão a criação de conta, autenticação, proteção do painel, criação automática do perfil, relações da taxonomia, limitações de acesso ao admin e resposta das páginas públicas e de autenticação.

Cada comportamento novo será implementado por desenvolvimento orientado a testes: teste em falha, implementação mínima e validação da suite completa.

## Fora de âmbito

Não são incluídos nesta fase confirmação de email, recuperação de palavra-passe, edição completa de perfis, upload de PDF, pesquisa real, filtros, páginas públicas de perfil, favoritos, formulário de contacto, moderação, sitemap, SEO avançado ou relatórios.

## Critérios de aceitação

1. O projeto Django inicia em desenvolvimento com configuração por variáveis de ambiente.
2. O utilizador pode criar conta, iniciar sessão, terminar sessão e aceder a um painel protegido.
3. A criação de conta cria um perfil em rascunho.
4. A taxonomia pode ser gerida por um administrador autorizado.
5. A página inicial é responsiva e mostra a identidade do CVLink.
6. A suite de testes passa sem avisos relevantes.
