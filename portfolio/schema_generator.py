#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
schema_generator.py
Generated & Maintained by Agent 8 (SEO & GEO Specialist) for rezapython.ir
Produces valid JSON-LD schemas for TechArticle, FAQPage, Person, and Breadcrumbs.
Can be imported directly into Django views or run standalone.
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

DEFAULT_DB_PATH = Path("G:/me/sayet/db.sqlite3")
SITE_DOMAIN = "https://rezapython.ir"
AUTHOR_NAME = "Reza Mortazavi"
AUTHOR_TITLE = "Computer Science Student & Network Security/Python Engineer"

def extract_faqs_from_markdown(content: str):
    """
    Scans markdown text for FAQ questions/answers under H2/H3 headings
    or Q&A patterns.
    """
    if not content:
        return []
    faqs = []
    faq_pattern = re.compile(
        r'(?:###?|####?)\s*(.*?(?:چگونه|چطور|علت|چرا|آیا|راهنمای|نحوه|روش|\?|؟).*?)\n+([^#\n][\s\S]*?)(?=(?:###?|\Z))',
        re.MULTILINE
    )
    for match in faq_pattern.finditer(content):
        q = match.group(1).strip()
        a = match.group(2).strip()
        q_clean = re.sub(r'[*_`#]', '', q).strip()
        a_clean = re.sub(r'```[\s\S]*?```', '[کد و دستور در متن مقاله]', a)
        a_clean = re.sub(r'[*_`]', '', a_clean).strip()
        sentences = [s.strip() for s in a_clean.split('\n') if s.strip()]
        if sentences:
            faqs.append({
                "question": q_clean,
                "answer": sentences[0][:300]
            })
    return faqs[:5]

def generate_article_schema(article: dict, faqs=None):
    """
    Constructs TechArticle, BreadcrumbList, Person, and optional FAQPage JSON-LD.
    """
    created_at = article.get("created_at") or datetime.now().isoformat()
    slug = article.get("slug", "")
    url = f"{SITE_DOMAIN}/articles/{slug}"
    title = article.get("title", "")
    summary = article.get("summary", "")
    category = article.get("category", "python")
    raw_tags = article.get("tags", "") or ""
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()]

    graph = []

    # 1. Person Schema (Reza Mortazavi Entity)
    person_schema = {
        "@type": "Person",
        "@id": f"{SITE_DOMAIN}/#author",
        "name": AUTHOR_NAME,
        "jobTitle": AUTHOR_TITLE,
        "url": SITE_DOMAIN,
        "sameAs": [
            "https://t.me/rezapython_bot",
            "https://rezapython.ir",
            "https://github.com/reza1384mor-dot"
        ]
    }
    graph.append(person_schema)

    # 2. TechArticle Schema
    article_schema = {
        "@type": "TechArticle",
        "@id": f"{url}#article",
        "isPartOf": {
            "@type": "WebSite",
            "@id": f"{SITE_DOMAIN}/#website",
            "name": "Reza Python",
            "url": SITE_DOMAIN
        },
        "headline": title,
        "description": summary,
        "inLanguage": "fa-IR",
        "mainEntityOfPage": url,
        "url": url,
        "datePublished": created_at,
        "author": {"@id": f"{SITE_DOMAIN}/#author"},
        "publisher": {
            "@type": "Organization",
            "name": "Reza Python",
            "url": SITE_DOMAIN,
            "logo": {
                "@type": "ImageObject",
                "url": f"{SITE_DOMAIN}/static/images/logo.png"
            }
        },
        "articleSection": category,
        "keywords": tags,
        "proficiencyLevel": "Expert"
    }
    graph.append(article_schema)

    # 3. Breadcrumbs
    breadcrumb_schema = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "خانه",
                "item": SITE_DOMAIN
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "مقالات",
                "item": f"{SITE_DOMAIN}/articles/"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": title,
                "item": url
            }
        ]
    }
    graph.append(breadcrumb_schema)

    # 4. FAQ Schema (if available)
    if faqs and len(faqs) > 0:
        faq_schema = {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item["answer"]
                    }
                }
                for item in faqs
            ]
        }
        graph.append(faq_schema)

    schema_wrapper = {
        "@context": "https://schema.org",
        "@graph": graph
    }
    return schema_wrapper

def get_articles_from_db(db_path=DEFAULT_DB_PATH):
    if not db_path.exists():
        print(f"[!] Database file not found at: {db_path}")
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolio_article ORDER BY id DESC")
    rows = cursor.fetchall()
    articles = [dict(row) for row in rows]
    conn.close()
    return articles

if __name__ == "__main__":
    print("[*] Agent 8 - Schema Generator starting...")
    articles = get_articles_from_db()
    print(f"[*] Found {len(articles)} articles in database.")
    for art in articles[:2]:
        faqs = extract_faqs_from_markdown(art.get("content", ""))
        schema = generate_article_schema(art, faqs)
        print("\n" + "="*50)
        print(f"Schema for Article ID {art['id']}: {art['title']}")
        print("="*50)
        print(json.dumps(schema, ensure_ascii=False, indent=2))
