```{=html}
<% 
function authorLine(author) {
  if (author == null || author === '') return '';
  if (typeof author === 'string') return author;
  if (Array.isArray(author)) {
    return author.map(function (a) {
      if (typeof a === 'string') return a;
      if (a && typeof a === 'object' && a.name) return a.name;
      return '';
    }).filter(Boolean).join(' y ');
  }
  return String(author);
}
%>
<% for (const item of items) { 
  const cats = item.categories || [];
  const catAttr = Array.isArray(cats) ? cats.join(' ') : String(cats || '');
%>
<div class="blog-entry" data-categories="<%- catAttr %>">
<h3><a href="<%- item.path %>"><%= item.title %></a></h3>
<div class="blog-entry-meta">
<span><%= item.date %></span>
<span><%= authorLine(item.author) %></span>
</div>
<div class="blog-entry-excerpt">
<%= item.description != null ? item.description : '' %>
</div>
<a href="<%- item.path %>" class="blog-entry-link">Leer más →</a>
</div>
<% } %>
```
