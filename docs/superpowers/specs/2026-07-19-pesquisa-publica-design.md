# Desenho da pesquisa e das páginas públicas

## Objetivo

Permitir que visitantes encontrem profissionais aprovados através de texto e filtros e consultem páginas públicas seguras de perfis e áreas.

## Regras de publicação

A pesquisa e as páginas públicas usam apenas perfis com `status=approved` e `is_public=True`. Perfis em rascunho, pendentes, rejeitados, suspensos, arquivados ou eliminados devolvem 404 e não entram em listagens.

Cada perfil recebe um slug estável e único. O slug é criado uma vez e não muda quando o nome público é editado, evitando ligações quebradas.

## Pesquisa

O MVP usa Django ORM com correspondência sem distinção entre maiúsculas e minúsculas. O texto procura nome público, título, biografia, localização, especializações e competências. Os filtros cobrem setor, área, especialização, competência, localização, disponibilidade e preferência de trabalho.

Os resultados são paginados em doze perfis e ordenados por atualização mais recente. Parâmetros inválidos são ignorados sem erro. A consulta usa `distinct()` para evitar duplicados causados pelas relações de competências.

## Páginas públicas

A página de perfil apresenta apenas dados profissionais autorizados. Email e telefone não aparecem quando a visibilidade está configurada para formulário. O currículo não tem ligação pública nesta fase.

A página de área mostra descrição, especializações e profissionais aprovados associados. A lista de áreas apresenta apenas entidades ativas.

## Experiência

Os filtros mantêm os valores na navegação e apresentam uma mensagem clara quando não existem resultados. A interface é móvel, usa etiquetas visíveis e mantém alvos interativos com pelo menos 44 píxeis.

## Testes

Os testes cobrem isolamento de perfis privados, pesquisa textual, filtros, paginação, slug único, páginas de área e ausência de contactos privados.
