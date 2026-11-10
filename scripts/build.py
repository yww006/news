#!/usr/bin/env python3
"""
静态站点生成器：从 data/articles.json 生成 index.html、分类页、详情页、历史归档
"""
import json
import os
from datetime import datetime
from pathlib import Path
from string import Template

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "articles.json"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 构建版本号（用于静态资源缓存失效）
BUILD_VERSION = datetime.now().strftime('%Y%m%d%H%M')

def format_date(dt_str):
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.strftime('%Y年%m月%d日')

def format_datetime(dt_str):
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%dT%H:%M:%S%z')

def get_category_info(data, cat_id):
    for cat in data['categories']:
        if cat['id'] == cat_id:
            return cat
    return {'name': cat_id, 'color': '#667eea', 'icon': ''}

def render_template(template_name, context):
    with open(TEMPLATES_DIR / template_name, 'r', encoding='utf-8') as f:
        template = Template(f.read())
    return template.safe_substitute(context)

def generate_index(data):
    site = data['site']
    featured = next((a for a in data['articles'] if a.get('featured')), data['articles'][0])
    other_articles = [a for a in data['articles'] if not a.get('featured')]

    # 首页显示今日日期（仅可见日期，schema.org 保持原文日期）
    now = datetime.now()
    today_display = format_date(now.isoformat())
    today_iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')

    # Hero article
    cat = get_category_info(data, featured['category'])
    hero_html = f'''
    <article class="hero-article" itemscope itemtype="https://schema.org/NewsArticle">
        <meta itemprop="datePublished" content="{format_datetime(featured['publishedAt'])}">
        <meta itemprop="dateModified" content="{format_datetime(featured['updatedAt'])}">
        <span class="category" style="background: {cat['color']};" itemprop="articleSection">{cat['icon']} {cat['name']}</span>
        <h2 itemprop="headline">{featured['title']}</h2>
        <p class="excerpt" itemprop="description">{featured['excerpt']}</p>
        <div class="meta">
            <span class="time" itemprop="datePublished" content="{today_iso}">{today_display}</span>
            <span class="source" itemprop="author" itemscope itemtype="https://schema.org/Person"><span itemprop="name">{featured['author']}</span></span>
            <span class="read-time">📖 {featured['readTime']} 分钟阅读</span>
        </div>
        <a href="{featured['slug']}.html" class="read-more" itemprop="url">阅读全文 →</a>
    </article>'''

    # Grid cards
    grid_articles = other_articles[:4]
    grid_html = ''
    for art in grid_articles:
        cat = get_category_info(data, art['category'])
        grid_html += f'''
        <article class="news-card" itemscope itemtype="https://schema.org/NewsArticle">
            <meta itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">
            <div class="card-image" style="background-image: url('{art['heroImage']}');"></div>
            <div class="card-content">
                <span class="category" style="background: {cat['color']}20; color: {cat['color']};" itemprop="articleSection">{cat['icon']} {cat['name']}</span>
                <h3 itemprop="headline"><a href="{art['slug']}.html" itemprop="url">{art['title']}</a></h3>
                <p itemprop="description">{art['excerpt']}</p>
                <div class="meta">
                    <span class="time" itemprop="datePublished" content="{today_iso}">{today_display}</span>
                    <span class="source" itemprop="author" itemscope itemtype="https://schema.org/Person"><span itemprop="name">{art['author']}</span></span>
                </div>
            </div>
        </article>'''

    # List items
    list_articles = other_articles[4:]
    list_html = ''
    for art in list_articles:
        cat = get_category_info(data, art['category'])
        list_html += f'''
        <article class="list-item" itemscope itemtype="https://schema.org/NewsArticle">
            <meta itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">
            <div class="list-image" style="background-image: url('{art['heroImage']}');"></div>
            <div class="list-content">
                <span class="category" style="background: {cat['color']}20; color: {cat['color']};" itemprop="articleSection">{cat['icon']} {cat['name']}</span>
                <h3 itemprop="headline"><a href="{art['slug']}.html" itemprop="url">{art['title']}</a></h3>
                <p itemprop="description">{art['excerpt']}</p>
                <div class="meta">
                    <span class="time" itemprop="datePublished" content="{today_iso}">{today_display}</span>
                    <span class="source" itemprop="author" itemscope itemtype="https://schema.org/Person"><span itemprop="name">{art['author']}</span></span>
                    <span class="read-time">📖 {art['readTime']} 分钟</span>
                </div>
            </div>
        </article>'''

    # Navigation
    nav_html = '<a href="index.html" class="active">首页</a>'
    for cat in data['categories']:
        nav_html += f'<a href="category/{cat["id"]}.html">{cat["icon"]} {cat["name"]}</a>'
    nav_html += '<a href="history/">历史</a>'

    # JSON-LD structured data for homepage
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site['name'],
        "url": site['url'],
        "potentialAction": {
            "@type": "SearchAction",
            "target": {"@type": "EntryPoint", "urlTemplate": site['url'] + "search?q={search_term_string}"},
            "query-input": "required name=search_term_string"
        }
    }

    context = {
        'site_name': site['name'],
        'site_description': site['description'],
        'site_url': site['url'],
        'page_title': site['name'],
        'page_description': site['description'],
        'canonical_url': site['url'],
        'og_image': featured['heroImage'],
        'json_ld': json.dumps(json_ld, ensure_ascii=False),
        'nav_links': nav_html,
        'hero_article': hero_html,
        'grid_cards': grid_html,
        'list_items': list_html,
        'current_year': datetime.now().year,
        'build_version': BUILD_VERSION,
    }

    html = render_template('index.html', context)
    with open(OUTPUT_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Generated index.html")

def generate_category_pages(data):
    for cat in data['categories']:
        cat_articles = [a for a in data['articles'] if a['category'] == cat['id']]
        
        nav_html = '<a href="../index.html">首页</a>'
        for c in data['categories']:
            active = ' class="active"' if c['id'] == cat['id'] else ''
            nav_html += f'<a href="../category/{c["id"]}.html"{active}>{c["icon"]} {c["name"]}</a>'
        nav_html += '<a href="../history/">历史</a>'

        articles_html = ''
        for art in cat_articles:
            articles_html += f'''
            <article class="news-card" itemscope itemtype="https://schema.org/NewsArticle">
                <meta itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">
                <div class="card-image" style="background-image: url('{art['heroImage']}');"></div>
                <div class="card-content">
                    <span class="category" style="background: {cat['color']}20; color: {cat['color']};" itemprop="articleSection">{cat['icon']} {cat['name']}</span>
                    <h3 itemprop="headline"><a href="../{art['slug']}.html" itemprop="url">{art['title']}</a></h3>
                    <p itemprop="description">{art['excerpt']}</p>
                    <div class="meta">
                        <span class="time" itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">{format_date(art['publishedAt'])}</span>
                        <span class="source" itemprop="author" itemscope itemtype="https://schema.org/Person"><span itemprop="name">{art['author']}</span></span>
                        <span class="read-time">📖 {art['readTime']} 分钟</span>
                    </div>
                </div>
            </article>'''

        json_ld = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f"{cat['name']} - {data['site']['name']}",
            "description": f"{data['site']['name']}{cat['name']}分类下的所有文章",
            "mainEntity": {
                "@type": "ItemList",
                "itemListElement": [
                    {"@type": "ListItem", "position": i+1, "item": {"@type": "NewsArticle", "url": f"{data['site']['url']}{art['slug']}.html", "headline": art['title']}}
                    for i, art in enumerate(cat_articles)
                ]
            }
        }

        context = {
            'site_name': data['site']['name'],
            'site_description': data['site']['description'],
            'site_url': data['site']['url'],
            'page_title': f"{cat['name']} - {data['site']['name']}",
            'page_description': f"{data['site']['name']}{cat['name']}分类最新资讯",
            'canonical_url': f"{data['site']['url']}category/{cat['id']}.html",
            'og_image': cat_articles[0]['heroImage'] if cat_articles else '',
            'json_ld': json.dumps(json_ld, ensure_ascii=False),
            'nav_links': nav_html,
            'category_name': cat['name'],
            'category_icon': cat['icon'],
            'category_color': cat['color'],
            'articles': articles_html,
            'current_year': datetime.now().year,
        }

        html = render_template('category.html', context)
        cat_dir = OUTPUT_DIR / 'category'
        cat_dir.mkdir(exist_ok=True)
        with open(cat_dir / f"{cat['id']}.html", 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Generated category/{cat['id']}.html")

def generate_article_pages(data):
    for art in data['articles']:
        cat = get_category_info(data, art['category'])
        
        nav_html = '<a href="index.html">首页</a>'
        for c in data['categories']:
            nav_html += f'<a href="category/{c["id"]}.html">{c["icon"]} {c["name"]}</a>'
        nav_html += '<a href="history/">历史</a>'

        # Related articles (same category, exclude current)
        related = [a for a in data['articles'] if a['category'] == art['category'] and a['id'] != art['id']][:3]
        related_html = ''
        for r in related:
            related_html += f'''
            <a href="{r['slug']}.html" class="related-card">
                <img src="{r['heroImage']}" alt="" loading="lazy">
                <span>{r['title']}</span>
            </a>'''

        json_ld = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": art['title'],
            "description": art['excerpt'],
            "image": art['heroImage'],
            "datePublished": format_datetime(art['publishedAt']),
            "dateModified": format_datetime(art['updatedAt']),
            "author": {"@type": "Person", "name": art['author']},
            "publisher": {"@type": "Organization", "name": data['site']['name'], "logo": {"@type": "ImageObject", "url": f"{data['site']['url']}favicon.ico"}},
            "mainEntityOfPage": {"@type": "WebPage", "@id": f"{data['site']['url']}{art['slug']}.html"},
            "articleSection": cat['name'],
            "keywords": ','.join(art['tags']),
            "wordCount": len(art['content']) // 2,
            "timeRequired": f"PT{art['readTime']}M"
        }

        context = {
            'site_name': data['site']['name'],
            'site_description': data['site']['description'],
            'site_url': data['site']['url'],
            'page_title': f"{art['title']} - {data['site']['name']}",
            'page_description': art['excerpt'],
            'canonical_url': f"{data['site']['url']}{art['slug']}.html",
            'og_image': art['heroImage'],
            'og_type': 'article',
            'article_published': format_datetime(art['publishedAt']),
            'article_modified': format_datetime(art['updatedAt']),
            'article_section': cat['name'],
            'article_tags': ','.join(art['tags']),
            'json_ld': json.dumps(json_ld, ensure_ascii=False),
            'nav_links': nav_html,
            'article_title': art['title'],
            'article_category': f'<span class="category" style="background: {cat["color"]}20; color: {cat["color"]};">{cat["icon"]} {cat["name"]}</span>',
            'article_author': art['author'],
            'article_date': format_date(art['publishedAt']),
            'article_read_time': str(art['readTime']),
            'article_hero_image': art['heroImage'],
            'article_content': art['content'],
            'related_articles': related_html,
            'current_year': datetime.now().year,
            'build_version': BUILD_VERSION,
        }

        html = render_template('article.html', context)
        with open(OUTPUT_DIR / f"{art['slug']}.html", 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Generated {art['slug']}.html")

def generate_rss(data):
    items = []
    for art in sorted(data['articles'], key=lambda x: x['publishedAt'], reverse=True):
        cat = get_category_info(data, art['category'])
        items.append(f'''    <item>
      <title><![CDATA[{art['title']}]]></title>
      <link>{data['site']['url']}{art['slug']}.html</link>
      <guid isPermaLink="true">{data['site']['url']}{art['slug']}.html</guid>
      <description><![CDATA[{art['excerpt']}]]></description>
      <pubDate>{datetime.fromisoformat(art['publishedAt'].replace('Z', '+00:00')).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
      <category>{cat['name']}</category>
      <author>{art['author']}</author>
      <enclosure url="{art['heroImage']}" type="image/jpeg" />
    </item>''')

    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{data['site']['name']}</title>
    <link>{data['site']['url']}</link>
    <description>{data['site']['description']}</description>
    <language>{data['site']['language']}</language>
    <atom:link href="{data['site']['url']}rss.xml" rel="self" type="application/rss+xml" />
    <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>
    <generator>Custom Static Site Generator</generator>
{''.join(items)}
  </channel>
</rss>'''

    with open(OUTPUT_DIR / 'rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss)
    print("✅ Generated rss.xml")

def generate_sitemap(data):
    urls = [
        {'url': data['site']['url'], 'changefreq': 'daily', 'priority': '1.0'},
        {'url': f"{data['site']['url']}rss.xml", 'changefreq': 'daily', 'priority': '0.5'},
    ]
    for cat in data['categories']:
        urls.append({'url': f"{data['site']['url']}category/{cat['id']}.html", 'changefreq': 'daily', 'priority': '0.8'})
    for art in data['articles']:
        urls.append({'url': f"{data['site']['url']}{art['slug']}.html", 'changefreq': 'weekly', 'priority': '0.9', 'lastmod': art['publishedAt'][:10]})

    sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'''
    for u in urls:
        sitemap += f'''
  <url>
    <loc>{u['url']}</loc>
    <changefreq>{u['changefreq']}</changefreq>
    <priority>{u['priority']}</priority>'''
        if 'lastmod' in u:
            sitemap += f'''
    <lastmod>{u['lastmod']}</lastmod>'''
        sitemap += '''
  </url>'''
    sitemap += '''
</urlset>'''

    with open(OUTPUT_DIR / 'sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print("✅ Generated sitemap.xml")

def generate_history_index(data):
    """生成历史归档索引页"""
    nav_html = '<a href="../index.html">首页</a>'
    for c in data['categories']:
        nav_html += f'<a href="../category/{c["id"]}.html">{c["icon"]} {c["name"]}</a>'
    nav_html += '<a href="../history/" class="active">历史</a>'

    # 扫描历史目录
    history_dir = OUTPUT_DIR / 'history'
    if not history_dir.exists():
        years_html = '<p class="empty-history">暂无历史归档</p>'
    else:
        years = sorted([d.name for d in history_dir.iterdir() if d.is_dir()], reverse=True)
        years_html = ''
        for year in years:
            year_dir = history_dir / year
            months = sorted([d.name for d in year_dir.iterdir() if d.is_dir()], reverse=True)
            years_html += f'''
            <details class="year-group" open>
                <summary><span class="year-badge">{year}年</span></summary>
                <div class="month-list">'''
            for month in months:
                month_dir = year_dir / month
                days = sorted([f.stem for f in month_dir.glob('*.html')], reverse=True)
                years_html += f'''
                    <details class="month-group">
                        <summary>{int(month)}月</summary>
                        <ul class="day-list">'''
                for day in days:
                    years_html += f'''
                            <li><a href="{year}/{month}/{day}.html">{int(day)}日</a></li>'''
                years_html += '''
                        </ul>
                    </details>'''
            years_html += '''
                </div>
            </details>'''

    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"历史归档 - {data['site']['name']}",
        "description": f"{data['site']['name']}历史每日首页归档，按年月日分类浏览",
    }

    context = {
        'site_name': data['site']['name'],
        'site_description': data['site']['description'],
        'site_url': data['site']['url'],
        'page_title': f"历史归档 - {data['site']['name']}",
        'page_description': f"{data['site']['name']}历史每日首页归档",
        'canonical_url': f"{data['site']['url']}history/",
        'og_image': '',
        'json_ld': json.dumps(json_ld, ensure_ascii=False),
        'nav_links': nav_html,
        'years_html': years_html,
        'current_year': datetime.now().year,
        'build_version': BUILD_VERSION,
    }

    html = render_template('history.html', context)
    history_dir = OUTPUT_DIR / 'history'
    history_dir.mkdir(exist_ok=True)
    with open(history_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ Generated history/index.html")

def archive_today(data):
    """将今日首页归档到 history/YYYY/MM/DD.html"""
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')

    # 生成今日首页内容（复用 generate_index 的逻辑，但不写入 index.html）
    site = data['site']
    featured = next((a for a in data['articles'] if a.get('featured')), data['articles'][0])
    other_articles = [a for a in data['articles'] if not a.get('featured')]

    cat = get_category_info(data, featured['category'])
    # 归档页使用今日日期作为显示日期
    today_display = format_date(now.isoformat())
    today_iso = now.strftime('%Y-%m-%dT%H:%M:%S%z')
    hero_html = f'''
    <article class="hero-article" itemscope itemtype="https://schema.org/NewsArticle">
        <meta itemprop="datePublished" content="{format_datetime(featured['publishedAt'])}">
        <meta itemprop="dateModified" content="{format_datetime(featured['updatedAt'])}">
        <span class="category" style="background: {cat['color']};" itemprop="articleSection">{cat['icon']} {cat['name']}</span>
        <h2 itemprop="headline">{featured['title']}</h2>
        <p class="excerpt" itemprop="description">{featured['excerpt']}</p>
        <div class="meta">
            <span class="time" itemprop="datePublished" content="{today_iso}">{today_display}</span>
            <span class="source" itemprop="author" itemscope itemtype="https://schema.org/Person"><span itemprop="name">{featured['author']}</span></span>
            <span class="read-time">📖 {featured['readTime']} 分钟阅读</span>
        </div>
        <a href="../../{featured['slug']}.html" class="read-more" itemprop="url">阅读全文 →</a>
    </article>'''

    grid_articles = other_articles[:4]
    grid_html = ''
    for art in grid_articles:
        cat = get_category_info(data, art['category'])
        grid_html += f'''
        <article class="news-card" itemscope itemtype="https://schema.org/NewsArticle">
            <meta itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">
            <div class="card-image" style="background-image: url('{art['heroImage']}');"></div>
            <div class="card-content">
                <span class="category" style="background: {cat['color']}20; color: {cat['color']};" itemprop="articleSection">{cat['icon']} {cat['name']}</span>
                <h3 itemprop="headline"><a href="../../{art['slug']}.html" itemprop="url">{art['title']}</a></h3>
                <p itemprop="description">{art['excerpt']}</p>
                <div class="meta">
                    <span class="time" itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">{format_date(art['publishedAt'])}</span>
                    <span class="source" itemprop="author" itemscope itemtype="https://schema.org/Person"><span itemprop="name">{art['author']}</span></span>
                </div>
            </div>
        </article>'''

    list_articles = other_articles[4:]
    list_html = ''
    for art in list_articles:
        cat = get_category_info(data, art['category'])
        list_html += f'''
        <article class="list-item" itemscope itemtype="https://schema.org/NewsArticle">
            <meta itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">
            <div class="list-image" style="background-image: url('{art['heroImage']}');"></div>
            <div class="list-content">
                <span class="category" style="background: {cat['color']}20; color: {cat['color']};" itemprop="articleSection">{cat['icon']} {cat['name']}</span>
                <h3 itemprop="headline"><a href="../../{art['slug']}.html" itemprop="url">{art['title']}</a></h3>
                <p itemprop="description">{art['excerpt']}</p>
                <div class="meta">
                    <span class="time" itemprop="datePublished" content="{format_datetime(art['publishedAt'])}">{format_date(art['publishedAt'])}</span>
                    <span class="source" itemprop="author" itemscope itemtype="https://schema.org/Person"><span itemprop="name">{art['author']}</span></span>
                    <span class="read-time">📖 {art['readTime']} 分钟</span>
                </div>
            </div>
        </article>'''

    # 归档页导航（返回历史索引）
    nav_html = '<a href="../../index.html">首页</a>'
    for c in data['categories']:
        nav_html += f'<a href="../../category/{c["id"]}.html">{c["icon"]} {c["name"]}</a>'
    nav_html += '<a href="../../history/" class="active">历史</a>'

    # 归档页标题
    archive_date = f"{year}年{int(month)}月{int(day)}日"

    context = {
        'site_name': site['name'],
        'site_description': site['description'],
        'site_url': site['url'],
        'page_title': f"{archive_date} - 历史归档 - {site['name']}",
        'page_description': f"{site['name']} {archive_date} 首页快照",
        'canonical_url': f"{site['url']}history/{year}/{month}/{day}.html",
        'og_image': featured['heroImage'],
        'json_ld': json.dumps({
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": f"{archive_date} 首页快照",
            "description": f"{site['name']} {archive_date} 的首页内容归档",
            "datePublished": now.strftime('%Y-%m-%dT%H:%M:%S%z'),
        }, ensure_ascii=False),
        'nav_links': nav_html,
        'archive_date': archive_date,
        'hero_article': hero_html,
        'grid_cards': grid_html,
        'list_items': list_html,
        'current_year': datetime.now().year,
        'build_version': BUILD_VERSION,
    }

    html = render_template('archive.html', context)
    archive_dir = OUTPUT_DIR / 'history' / year / month
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_file = archive_dir / f"{day}.html"
    with open(archive_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Archived today to history/{year}/{month}/{day}.html")

    return archive_file

def main():
    data = load_data()
    generate_index(data)
    generate_category_pages(data)
    generate_article_pages(data)
    generate_rss(data)
    generate_sitemap(data)
    archive_today(data)
    generate_history_index(data)
    print("\n🎉 All pages generated successfully!")

if __name__ == '__main__':
    main()