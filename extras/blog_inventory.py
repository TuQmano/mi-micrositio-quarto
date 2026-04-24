#!/usr/bin/env python3
"""Inventory CSV blog links vs posts/*.qmd: normalize URLs, dedupe, match repo, draft stubs."""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "extras" / "blog_posts_cepe.csv"
POSTS_DIR = ROOT / "posts"

TRACKING_PARAMS = frozenset(
    {
        "trackingid",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "r",
        "b",
        "triedredirect",
    }
)

DRAFT_BODY = """Borrador: incorporar aquí el texto completo del artículo con autorización de la fuente.

"""


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    p = urlparse(raw)
    if not p.scheme:
        return raw
    netloc = p.netloc.lower()
    path = p.path or ""
    if path.endswith("/"):
        path = path[:-1]
    q = parse_qs(p.query, keep_blank_values=False)
    filtered = []
    for k, vals in sorted(q.items()):
        lk = k.lower()
        if lk in TRACKING_PARAMS:
            continue
        for v in vals:
            filtered.append((k, v))
    query = "&".join(f"{k}={v}" for k, v in filtered)
    return urlunparse((p.scheme.lower(), netloc, path, "", query, ""))


def lanacion_nid(url: str) -> str | None:
    m = re.search(r"nid(\d+)", url, re.I)
    return m.group(1) if m else None


def canonical_hrefs_from_post(path: Path) -> list[str]:
    """Only hrefs in source blocks, not body cross-links."""
    text = path.read_text(encoding="utf-8", errors="replace")
    out: list[str] = []
    for block in re.split(r"(?:blog-source-link|::: blog-source-link)", text, flags=re.I)[1:]:
        for m in re.finditer(r'href="(https?://[^"]+)"', block[:1200]):
            out.append(m.group(1))
    if not out and "Publicado originalmente" in text:
        for m in re.finditer(
            r"Publicado originalmente[\s\S]{0,400}?href=\"(https?://[^\"]+)\"",
            text,
        ):
            out.append(m.group(1))
    return out


def short_title_for_slug(title: str, n: int = 150) -> str:
    if len(title) <= n:
        return title
    t = title[:n]
    if " " in t:
        return t.rsplit(" ", 1)[0].rstrip(",:;")
    return t


def title_slug_asci(title: str, max_len: int = 120) -> str:
    t = short_title_for_slug(title, 150)
    s = unicodedata.normalize("NFKD", t)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = "post"
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s


def slugify_title(title: str) -> str:
    return title_slug_asci(title, 120)


def date_from_lanacion_nid(nid: str) -> str | None:
    if len(nid) != 8 or not nid.isdigit():
        return None
    d, m, y = int(nid[:2]), int(nid[2:4]), int(nid[4:])
    if not (1 <= m <= 12 and 1 <= d <= 31):
        return None
    return f"{y}-{m:02d}-{d:02d}"


def infer_categories(title: str, link: str) -> list[str]:
    t = f"{title} {link}".lower()
    if any(
        x in t
        for x in (
            "education",
            "educación",
            "teacher",
            "classroom",
            "student",
            "escuela",
            "generative ai in education",
        )
    ):
        return ["Educación"]
    if any(
        x in t
        for x in (
            "regulat",
            "lawmaker",
            "policy",
            "sovereignty",
            "primer",
            "coalición",
            "gobiernos locales",
            "américa latina",
        )
    ):
        return ["Gobernanza"]
    if any(
        x in t
        for x in (
            "hiring",
            "job",
            "labour",
            "labor",
            "work",
            "employment",
            "finance",
            "credential",
            "footprints",
        )
    ):
        return ["Adopción"]
    if any(x in t for x in ("deepseek", "innovation", "gpt", "hybrid jobs")):
        return ["Innovación"]
    return ["Gobernanza"]


def source_label(link: str) -> str:
    host = urlparse(link).netloc.lower()
    if "lanacion.com" in host:
        return "La Nación"
    if "brookings.edu" in host:
        return "Brookings"
    if "cepr.org" in host:
        return "CEPR / VoxEU"
    if "linkedin.com" in host:
        return "LinkedIn"
    if "iadb.org" in host or "publications.iadb.org" in host:
        return "BID"
    if "utdt.edu" in host:
        return "UTDT"
    if "eldiarioar.com" in host:
        return "elDiarioAR"
    if "americasquarterly.org" in host:
        return "Americas Quarterly"
    if "infobae.com" in host:
        return "Infobae"
    if "clarin.com" in host:
        return "Clarín"
    if "ciiar.org" in host:
        return "CIIAR"
    if "automatizados.com" in host:
        return "AUTOMATIZADOS"
    if "substack.com" in host:
        return "Substack"
    if "humanfactormovement" in host:
        return "Human Factor Movement"
    return "Fuente original"


POST_FOOTER = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  const filterButtons = document.querySelectorAll('.blog-filter-btn');
  filterButtons.forEach(button => {
    button.addEventListener('click', function() {
      const category = this.getAttribute('data-category');
      window.location.href = '../blog.html?categoria=' + encodeURIComponent(category);
    });
  });
  const categoryElements = document.querySelectorAll('.quarto-category');
  categoryElements.forEach(cat => {
    cat.style.cursor = 'pointer';
    cat.style.textDecoration = 'underline';
    cat.addEventListener('click', function() {
      const category = this.textContent.trim();
      window.location.href = '../blog.html?categoria=' + encodeURIComponent(category);
    });
  });
});
</script>

<script>
document.addEventListener('DOMContentLoaded', function() {
  const headings = document.querySelectorAll('.quarto-title-meta-heading');
  headings.forEach(heading => {
    if (heading.textContent.trim() === 'Author') {
      heading.textContent = 'Autor';
    } else if (heading.textContent.trim() === 'Published') {
      heading.textContent = 'Publicado';
    }
  });
});
</script>

<footer class="site-footer">
  <img src="../NADIA-banners.png" alt="CEPE y Fundar" style="max-width: 100%; width: 100%; height: auto;">
</footer>
"""


def write_draft_qmd(
    path: Path,
    *,
    title: str,
    description: str,
    date: str,
    author: str,
    categories: list[str],
    canonical_url: str,
    source_name: str,
) -> None:
    cats_yaml = ", ".join(repr(c) for c in categories)
    body = f"""---
title: "{title.replace('"', '\\"')}"
description: "{description.replace('"', '\\"')[:280]}"
date: "{date}"
author: "{author.replace('"', '\\"')}"
categories: [{cats_yaml}]
draft: true
---

<div class="blog-layout">

<div class="blog-content">

{DRAFT_BODY}
<div class="blog-source-link">
Publicado originalmente en <a href="{canonical_url}">{source_name}</a>
</div>

</div>

<div class="blog-sidebar">

<div class="blog-filters" id="blog-filters">
  <button class="blog-filter-btn active" data-category="all">Todas</button>
  <button class="blog-filter-btn" data-category="Gobernanza">Gobernanza</button>
  <button class="blog-filter-btn" data-category="Adopción">Adopción</button>
  <button class="blog-filter-btn" data-category="Educación">Educación</button>
  <button class="blog-filter-btn" data-category="Innovación">Innovación</button>
</div>

</div>

</div>
{POST_FOOTER}
"""
    path.write_text(body, encoding="utf-8")


def main() -> None:
    norm_to_post: dict[str, str] = {}

    for path in sorted(POSTS_DIR.glob("*.qmd")):
        if path.name.startswith("_"):
            continue
        for h in canonical_hrefs_from_post(path):
            norm_to_post.setdefault(normalize_url(h), path.name)

    nid_to_post = {
        "10092025": "una-inteligencia-artificial-que-hable-nuestro-idioma.qmd",
        "09082025": "la-paradoja-de-tercerizar-el-pensamiento-en-la-ia.qmd",
        "22022025": "deepseek-atajo-a-la-soberanía-tecnológica-o-nueva-dependencia.qmd",
    }

    rows_out: list[dict[str, str]] = []
    seen_norm: dict[str, int] = {}
    seen_nid: dict[str, int] = {}
    seen_title_key: dict[str, int] = {}
    draft_qmd_names: set[str] = set()

    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)
        for i, row in enumerate(reader, start=2):
            if not row or not str(row[0]).strip().startswith("http"):
                continue
            link = row[0].strip()
            title = row[1].strip() if len(row) > 1 else ""
            author = row[2].strip() if len(row) > 2 else ""
            norm = normalize_url(link)
            nid = lanacion_nid(link)

            title_key = re.sub(r"\s+", " ", title.lower())[:120]
            internal_dup = ""
            if norm in seen_norm:
                internal_dup = f"dup_url_row_{seen_norm[norm]}"
            elif nid and nid in seen_nid:
                internal_dup = f"dup_nid_row_{seen_nid[nid]}"
            elif title_key and title_key in seen_title_key:
                internal_dup = f"dup_title_row_{seen_title_key[title_key]}"
            else:
                if norm:
                    seen_norm[norm] = i
                if nid:
                    seen_nid[nid] = i
                if title_key:
                    seen_title_key[title_key] = i

            repo_status = "candidate"
            matched = ""

            if norm in norm_to_post:
                repo_status = "published"
                matched = norm_to_post[norm]
            elif nid and nid in nid_to_post:
                repo_status = "published"
                matched = nid_to_post[nid]

            pertinence = "yes"
            notes: list[str] = []

            if "linkedin.com/in/" in link and "recent-activity" in link:
                pertinence = "no"
                repo_status = "exclude"
                notes.append("profile_not_article")

            if internal_dup.startswith("dup_"):
                notes.append(internal_dup)
                if repo_status == "candidate":
                    pertinence = "duplicate_csv_row"

            if "brookings.edu" in link.lower() and "non-degree credentials" in title.lower():
                notes.append("same_study_cepr_brookings_pick_one")
                if repo_status == "candidate":
                    pertinence = "duplicate_csv_row"

            if (
                "generative ai in education" in title.lower()
                and "framework" in title.lower()
            ):
                notes.append("same_title_pdf_and_utdt_pick_one")

            if "deepseek" in title.lower() and "crossroads" in title.lower():
                notes.append("related_topic_see_posts_deepseek-atajo")

            draft_eligible = (
                repo_status == "candidate"
                and pertinence == "yes"
                and internal_dup == ""
            )
            draft_qmd = ""
            if draft_eligible and title:
                base = title_slug_asci(title)
                candidate = f"{base}.qmd"
                suffix = 2
                while candidate in draft_qmd_names:
                    candidate = f"{base}-{suffix}.qmd"
                    suffix += 1
                draft_qmd_names.add(candidate)
                draft_qmd = candidate

            rows_out.append(
                {
                    "csv_row": str(i),
                    "link": link,
                    "title": title,
                    "author": author,
                    "normalized_url": norm,
                    "lanacion_nid": nid or "",
                    "internal_dup": internal_dup,
                    "repo_status": repo_status,
                    "matched_post_qmd": matched,
                    "pertinence": pertinence,
                    "draft_eligible": "yes" if draft_eligible else "no",
                    "draft_qmd": draft_qmd,
                    "suggested_slug": slugify_title(title) if title else "",
                    "notes": "; ".join(notes),
                }
            )

    out_path = ROOT / "extras" / "blog_posts_cepe_review.tsv"
    fieldnames = list(rows_out[0].keys())
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        w.writeheader()
        w.writerows(rows_out)

    new_header = [
        "Link",
        "Title",
        "Author",
        "normalized_url",
        "lanacion_nid",
        "internal_dup",
        "repo_status",
        "matched_post_qmd",
        "pertinence",
        "draft_eligible",
        "draft_qmd",
        "suggested_slug",
        "notes",
    ]
    out_csv = ROOT / "extras" / "blog_posts_cepe.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(new_header)
        for r in rows_out:
            w.writerow(
                [
                    r["link"],
                    r["title"],
                    r["author"],
                    r["normalized_url"],
                    r["lanacion_nid"],
                    r["internal_dup"],
                    r["repo_status"],
                    r["matched_post_qmd"],
                    r["pertinence"],
                    r["draft_eligible"],
                    r["draft_qmd"],
                    r["suggested_slug"],
                    r["notes"],
                ]
            )

    drafts_written = 0
    for r in rows_out:
        if r["draft_eligible"] != "yes" or not r.get("draft_qmd"):
            continue
        fn = POSTS_DIR / r["draft_qmd"]
        nid = r["lanacion_nid"]
        date_guess = date_from_lanacion_nid(nid) if nid else None
        date = date_guess or "2025-01-15"
        author = r["author"].strip() or "—"
        title = r["title"].strip() or "Sin título"
        desc = title[:280]
        cats = infer_categories(title, r["link"])
        write_draft_qmd(
            fn,
            title=title,
            description=desc,
            date=date,
            author=author,
            categories=cats,
            canonical_url=r["link"],
            source_name=source_label(r["link"]),
        )
        drafts_written += 1

    print(
        f"Wrote {out_path} and {out_csv} ({len(rows_out)} rows); "
        f"draft qmd files: {drafts_written}"
    )


if __name__ == "__main__":
    main()
