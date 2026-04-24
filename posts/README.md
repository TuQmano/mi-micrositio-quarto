# Entradas del Blog

Esta carpeta contiene las entradas del blog.

## Cómo agregar una nueva entrada

1. Copia el archivo `_template.qmd` y renómbralo con un nombre descriptivo (ej: `mi-entrada.qmd`)

2. Edita el front matter (la sección entre `---` al inicio):
   - `title`: Título de la entrada
   - `description`: Breve descripción
   - `date`: Fecha en formato "YYYY-MM-DD"
   - `author`: Nombre del autor
   - `categories`: Lista de categorías (ej: `["Gobernanza"]`; deben coincidir con los filtros del blog)
   - Si copiás `_template.qmd`, quitá `draft: true` (o usá `draft: false`) cuando la entrada deba aparecer en el índice.

3. Escribe el contenido de tu entrada usando Markdown

4. El índice en `blog.qmd` se genera solo al renderizar: incluye todos los `.qmd` de esta carpeta salvo borradores (`draft: true`). No hace falta editar `blog.qmd` para cada nota nueva.

## Ejemplo

```markdown
---
title: "Mi nueva entrada"
description: "Descripción breve"
date: "2025-01-26"
author: "Tu nombre"
categories: ["IA"]
---

## Contenido

Aquí va tu contenido...
```

