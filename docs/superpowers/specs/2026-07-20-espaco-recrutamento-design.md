# Espaco de Recrutamento e Shortlist Design

## Contexto

O CVLink ja tem perfis publicos aprovados, pesquisa por texto, filtros profissionais, contactos, favoritos e protecoes de privacidade. A fase anterior reforcou pesquisa, filtros e apresentacao dos perfis. A proxima fase deve transformar os favoritos numa area util para equipas de recursos humanos e recrutamento, sem expor dados privados dos candidatos e sem criar uma solucao complexa demais para o estado actual do produto.

## Objectivo

Criar uma area de trabalho de recrutamento para utilizadores autenticados guardarem candidatos, organizarem o estado do processo, adicionarem notas e etiquetas privadas, guardarem pesquisas frequentes, compararem perfis e exportarem uma shortlist em CSV.

## Decisao aprovada

A abordagem aprovada e a abordagem A: recrutar melhor com o que ja existe. Isto significa evoluir favoritos, pesquisa e dashboard antes de criar alertas automaticos, mensagens internas, recomendacoes por IA ou funis complexos.

## Publico-alvo

O publico principal sao consultores, empresas, equipas de recursos humanos, recrutadores independentes e coordenadores de projecto que precisam encontrar talento em comunidades lusofonas e mercados onde o CV formal nem sempre esta bem estruturado.

## Principios de produto

A interface deve ser profissional, directa e orientada a trabalho repetido. O utilizador deve conseguir pesquisar, filtrar, guardar, comparar e exportar candidatos sem perder contexto.

O sistema deve proteger os candidatos. A shortlist, notas, etiquetas e estados pertencem apenas ao recrutador autenticado. A exportacao nao deve incluir telefone, email, WhatsApp, morada privada ou qualquer dado que o candidato nao tornou publico.

O sistema deve continuar simples. Esta fase nao inclui alertas por email, entrevistas agendadas, ranking automatico, mensagens internas ou integracao com ATS externo.

## Funcionalidades

### Shortlist

Os favoritos passam a funcionar como shortlist de recrutamento.

Cada item da shortlist deve guardar:

- perfil associado
- recrutador dono do registo
- estado do processo
- notas privadas
- etiquetas privadas
- datas de criacao e actualizacao

Estados suportados:

- Guardado
- Para contactar
- Contactado
- Entrevista
- Proposta
- Contratado
- Arquivado

A pagina de shortlist deve permitir filtrar por estado e etiqueta, editar notas, mudar estado, remover candidato e abrir o perfil publico.

### Etiquetas privadas

As etiquetas ajudam a organizar candidatos por contexto interno, por exemplo "consultoria", "engenharia civil", "comunicacao", "remoto", "urgente" ou "bilingue".

As etiquetas devem ser privadas por utilizador. Um recrutador nao pode ver, editar ou reutilizar etiquetas de outro recrutador.

### Pesquisas guardadas

Um utilizador autenticado pode guardar uma pesquisa com nome proprio e conjunto de filtros. A pesquisa guardada deve conservar:

- texto pesquisado
- sector
- area profissional
- pais
- modalidade
- experiencia minima
- disponibilidade
- ordenacao

A pagina de dashboard deve mostrar pesquisas guardadas recentes. Cada pesquisa deve ter accao para executar, editar nome e apagar.

Nesta fase, pesquisa guardada nao envia alertas automaticos. O objectivo e reduzir trabalho repetido e dar uma base limpa para alertas numa fase futura.

### Comparacao de perfis

O recrutador pode comparar ate 4 perfis aprovados e publicos. A comparacao deve mostrar campos uteis para decisao rapida:

- nome publico
- titulo profissional
- sector e area
- pais publico, quando o candidato autorizou
- modalidade
- disponibilidade
- anos de experiencia
- competencias
- formacao
- idiomas
- indicacao de CV disponivel, sem forcar download

A comparacao deve excluir contactos privados e dados privados de localizacao.

### Exportacao CSV

A shortlist pode ser exportada para CSV pelo dono autenticado. O CSV deve conter informacao profissional publica e os dados privados criados pelo proprio recrutador.

Campos permitidos:

- nome publico
- titulo profissional
- sector
- area
- pais publico
- modalidade
- disponibilidade
- anos de experiencia
- competencias publicas
- idiomas publicos
- estado de recrutamento
- etiquetas privadas do recrutador
- notas privadas do recrutador
- URL do perfil publico

Campos excluidos:

- email
- telefone
- WhatsApp
- morada privada
- localizacao nao publica
- notas ou etiquetas de outros utilizadores

O CSV deve proteger contra formula injection em folhas de calculo, escapando valores que comecem por "=", "+", "-" ou "@".

## Arquitectura

O modulo `interactions` deve continuar a ser o dono das interaccoes do recrutador com perfis. A tabela existente de favoritos deve ser evoluida para guardar estado, notas e relacao com etiquetas. Isto preserva favoritos ja existentes e evita criar uma segunda entidade com o mesmo papel.

Devem ser adicionados dois modelos:

- `RecruitmentTag`, privado por utilizador, com nome normalizado para evitar duplicados como "Python" e " python "
- `SavedSearch`, privado por utilizador, com nome e parametros de pesquisa validados

A logica de exportacao deve ficar num servico de `interactions`, para ser testada isoladamente e reutilizada pela view. A view so deve validar permissao, aplicar filtros e devolver a resposta CSV.

## Fluxos

### Guardar candidato

O utilizador pesquisa talentos, abre um perfil ou usa o cartao de resultado e adiciona o candidato a shortlist. Se o candidato ja estiver guardado, a interface deve manter o registo existente e permitir actualizar estado, notas e etiquetas.

### Trabalhar a shortlist

O utilizador entra na area de shortlist, filtra por estado ou etiqueta, revê notas, muda candidatos de fase e remove os que ja nao interessam.

### Guardar pesquisa

O utilizador aplica filtros na pesquisa publica, inicia sessao se necessario e guarda a combinacao com um nome. Depois volta ao dashboard ou a pagina de pesquisas guardadas e executa a mesma pesquisa com um clique.

### Comparar candidatos

O utilizador selecciona ate 4 candidatos da shortlist e abre a pagina de comparacao. O sistema valida que todos os perfis pertencem a shortlist do utilizador e continuam aprovados/publicos.

### Exportar shortlist

O utilizador exporta a shortlist filtrada ou completa. O ficheiro gerado deve estar em UTF-8 com BOM para compatibilidade com Excel, sem dados privados do candidato.

## Permissoes e privacidade

Todas as operacoes de shortlist, etiquetas, pesquisas guardadas, comparacao e exportacao exigem autenticacao.

Um utilizador so pode ver e alterar os seus proprios registos.

Perfis nao aprovados, privados ou removidos nao devem aparecer em comparacoes ou exportacoes.

Dados privados do candidato continuam protegidos pelas regras ja existentes de visibilidade.

## Interface

A navegacao deve evitar redundancia. O menu principal nao deve depender de uma pagina "Pesquisar" duplicada se a pesquisa principal ja esta no inicio. A experiencia deve privilegiar:

- campo de pesquisa principal claro
- filtros visiveis e consistentes
- etiquetas de filtros activos removiveis
- botao "Guardar pesquisa"
- botao "Adicionar a shortlist"
- area "Shortlist" no painel
- estados de recrutamento com controlo simples
- accoes de comparar e exportar na shortlist

O texto deve estar em portugues correcto e sem caracteres corrompidos. A interface deve ser testada com nomes, sectores e areas com acentos.

## Testes obrigatorios

Devem existir testes automatizados para:

- criar e actualizar item da shortlist
- impedir acesso a shortlist de outro utilizador
- criar, listar, executar e apagar pesquisa guardada
- validar parametros permitidos de pesquisa guardada
- comparar apenas perfis da shortlist do utilizador
- limitar comparacao a 4 perfis
- exportar CSV com campos permitidos
- excluir email, telefone, WhatsApp e localizacao privada do CSV
- escapar formula injection no CSV
- manter pesquisa e filtros com acentos sem corrupcao de texto

Antes de alterar codigo de producao, cada comportamento novo deve ter teste a falhar pelo motivo esperado. Depois a implementacao deve ser minima ate o teste passar.

## Fora de escopo nesta fase

Esta fase nao inclui:

- alertas automaticos por email
- chat interno entre recrutador e candidato
- agenda de entrevistas
- ranking automatico por IA
- recomendacoes automaticas
- exportacao para PDF
- integracao com LinkedIn, Gmail, ATS ou calendarios
- gestao de equipas com multiplos recrutadores na mesma empresa

## Criterios de aceitacao

A fase esta concluida quando:

- a shortlist substitui a experiencia simples de favoritos sem perder favoritos existentes
- o recrutador consegue classificar candidatos por estado, notas e etiquetas privadas
- pesquisas guardadas funcionam com os filtros actuais
- comparacao de ate 4 perfis funciona e respeita privacidade
- exportacao CSV funciona e nao inclui dados privados do candidato
- a interface esta em portugues correcto, sem caracteres corrompidos
- os testes automatizados passam
- ha verificacao no browser com Playwright dos fluxos principais

