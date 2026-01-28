# Entradas del Blog

Esta carpeta contiene las entradas del blog.

## Cómo agregar una nueva entrada

1. Copia el archivo `_template.qmd` y renómbralo con un nombre descriptivo (ej: `mi-entrada.qmd`)

2. Edita el front matter (la sección entre `---` al inicio):
   - `title`: Título de la entrada
   - `description`: Breve descripción
   - `date`: Fecha en formato "YYYY-MM-DD"
   - `author`: Nombre del autor
   - `categories`: Lista de categorías (ej: ["IA", "Políticas Públicas"])

3. Escribe el contenido de tu entrada usando Markdown

4. Agrega la entrada a `blog.qmd` siguiendo el formato de las entradas existentes

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

