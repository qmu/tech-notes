# -*- coding: utf-8 -*-
"""10 本を静的サイトに書き出す。title の形だけが実験の変数で、他は機械的に揃える。"""
import json, os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import PAGES

HERE = os.path.dirname(os.path.abspath(__file__))
ASSIGN = json.load(open(os.path.join(HERE, "assign.json")))["assign"]
OUT = os.path.dirname(HERE)  # リポジトリ直下に書き出す（Pages のルート配信）
SITE = "技術ノート"
# Search Console の所有確認タグ。src/google-site-verification.txt に token を置いたときだけ全ページの head に出す
# （無ければ出力は一切変わらない）。token は Google アカウントに紐づく値で、ページの内容や順位には影響しない。
_VERIFY_FILE = os.path.join(HERE, "google-site-verification.txt")
VERIFY = ""
if os.path.exists(_VERIFY_FILE):
    _tok = open(_VERIFY_FILE, encoding="utf-8").read().strip()
    if _tok:
        VERIFY = f'\n<meta name="google-site-verification" content="{html.escape(_tok)}">'
ORG = "株式会社くむ"

CSS = """*{box-sizing:border-box}
:root{--bg:#fbfbf9;--fg:#1a1c1e;--dim:#5c6260;--rule:#e2e4df;--link:#1c5a52}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15171a;--fg:#e8ebe7;--dim:#98a09b;--rule:#2b2f32;--link:#6cb9ab}}
:root[data-theme=dark]{--bg:#15171a;--fg:#e8ebe7;--dim:#98a09b;--rule:#2b2f32;--link:#6cb9ab}
body{margin:0;background:var(--bg);color:var(--fg);font-family:"Hiragino Sans","Yu Gothic",system-ui,sans-serif;line-height:1.9;font-size:16px}
.wrap{max-width:44rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}
header.site{border-bottom:1px solid var(--rule);padding-bottom:1rem;margin-bottom:2.5rem;font-size:14px}
header.site a{color:var(--dim);text-decoration:none}
h1{font-size:1.65rem;line-height:1.45;margin:0 0 .5rem;text-wrap:balance}
.lede{color:var(--dim);margin:0 0 2.5rem;font-size:15px}
h2{font-size:1.05rem;margin:2.5rem 0 .6rem;padding-top:1.2rem;border-top:1px solid var(--rule)}
p{margin:0 0 1rem}
a{color:var(--link)}
ul.idx{list-style:none;padding:0;margin:0;display:flex;flex-direction:column}
ul.idx li{border-bottom:1px solid var(--rule)}
ul.idx a{display:block;padding:.9rem 0;text-decoration:none;color:var(--fg)}
ul.idx a:hover{color:var(--link)}
ul.idx .d{display:block;color:var(--dim);font-size:13.5px;line-height:1.7;margin-top:.15rem}
footer{margin-top:4rem;padding-top:1.2rem;border-top:1px solid var(--rule);color:var(--dim);font-size:13px}
"""

def shell(title, desc, canonical, body):
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">{VERIFY}
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="site"><a href="{'../' if canonical.count('/')>3 else ''}./">{SITE} — {ORG}</a></header>
{body}
<footer>{ORG}（qmu）の技術ノートです。設計の判断基準を、根拠つきで公開しています。</footer>
</div>
</body>
</html>
"""

def main():
    base = "https://qmu.github.io/tech-notes"
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for p in PAGES:
        arm = ASSIGN[p["slug"]]
        title_head = p["question"] if arm == "question" else p["noun"]
        title = f"{title_head} | {ORG}"
        # h1 は全ページ名詞形で固定する。差を <title> だけに閉じ込めるため。
        body = f"<h1>{html.escape(p['noun'])}</h1>\n<p class=\"lede\">{html.escape(p['desc'])}</p>\n"
        for h, t in p["body"]:
            body += f"<h2>{html.escape(h)}</h2>\n<p>{html.escape(t)}</p>\n"
        d = os.path.join(OUT, p["slug"]); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(
            shell(title, p["desc"], f"{base}/{p['slug']}/", body))
        rows.append((p, arm, title))

    idx = f"<h1>{SITE}</h1>\n<p class=\"lede\">設計と運用の判断基準を、根拠つきで公開しています。</p>\n<ul class=\"idx\">\n"
    for p, arm, title in rows:
        idx += (f'<li><a href="./{p["slug"]}/">{html.escape(p["noun"])}'
                f'<span class="d">{html.escape(p["desc"][:70])}…</span></a></li>\n')
    idx += "</ul>\n"
    open(os.path.join(OUT, "index.html"), "w").write(
        shell(f"{SITE} | {ORG}", f"{ORG}の技術ノート。設計と運用の判断基準を根拠つきで公開しています。", f"{base}/", idx))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
          f"<url><loc>{base}/</loc></url>"]
    sm += [f"<url><loc>{base}/{p['slug']}/</loc></url>" for p, _, _ in rows]
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")

    print(f"{'slug':18s} {'アーム':8s} <title>")
    for p, arm, title in rows:
        print(f"{p['slug']:18s} {('疑問形' if arm=='question' else '名詞形'):8s} {title}")

if __name__ == "__main__":
    main()
