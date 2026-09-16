#!/usr/bin/env python3
"""Scan all .html files in repo root (except index.html), read their <title>,
and get the last commit date via git log. Then render a static index.html.
Runs locally and in GitHub Actions."""
import os, re, subprocess, datetime, html as htmllib, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# When run by Actions from repo root, .github/scripts/build_index.py -> ROOT is repo root.
# But during local dry-run we may point ROOT elsewhere; default to cwd if script is missing.
if not os.path.exists(os.path.join(ROOT, ".github")):
    ROOT = os.getcwd()

def git_last_date(path):
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", "--", path],
            cwd=ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
        return out or None
    except Exception:
        return None

def extract_title(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(8192)
        m = re.search(r"<title[^>]*>([\s\S]*?)</title>", content, re.I)
        if m and m.group(1).strip():
            return htmllib.unescape(m.group(1).strip())
    except Exception:
        pass
    return os.path.basename(path).rsplit(".", 1)[0]

posts = []
for name in sorted(os.listdir(ROOT)):
    full = os.path.join(ROOT, name)
    if not os.path.isfile(full): continue
    if not name.lower().endswith(".html"): continue
    if name == "index.html": continue
    title = extract_title(full)
    date = git_last_date(name)
    posts.append({"name": name, "title": title, "date": date})

posts.sort(key=lambda p: p["date"] or "", reverse=True)

def fmt_date(iso):
    if not iso: return ""
    try:
        d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return f"{d.year}-{d.month:02d}-{d.day:02d}"
    except Exception:
        return iso[:10]

items_html = ""
for p in posts:
    ds = fmt_date(p["date"])
    items_html += f'''      <a class="item" href="./{htmllib.escape(p["name"])}">
        <div class="info">
          <span class="title">{htmllib.escape(p["title"])}</span>
        </div>
        {f'<span class="date">{ds}</span>' if ds else ''}
      </a>\n'''

count_text = f"共 {len(posts)} 篇文章"

out = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jason 的小站 · 文章列表</title>
<style>
:root{{
  --bg:#f6f8fc; --card:#ffffff; --line:#e3e8f0;
  --ink:#16233b; --muted:#5b6b84; --muted-2:#8a97ad;
  --blue:#1d4ed8; --blue-bg:#eef4ff; --blue-deep:#0f2f86;
  --radius:14px; --shadow:0 1px 3px rgba(22,35,59,.06),0 8px 24px -12px rgba(22,35,59,.12);
  --font:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Segoe UI",sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:var(--font);color:var(--ink);background:var(--bg);line-height:1.7;min-height:100vh}}
a{{color:var(--blue);text-decoration:none}}
a:hover{{text-decoration:underline}}
.cover{{background:linear-gradient(135deg,#0d1f56 0%,#123a8f 45%,#1d4ed8 100%);color:#fff;padding:64px 24px 56px;position:relative;overflow:hidden}}
.cover::after{{content:"";position:absolute;right:-120px;top:-120px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.14),transparent 65%)}}
.cover::before{{content:"";position:absolute;left:-80px;bottom:-160px;width:380px;height:380px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.08),transparent 65%)}}
.cover-inner{{max-width:860px;margin:0 auto;position:relative;z-index:1}}
.cover .kicker{{display:inline-block;font-size:13px;letter-spacing:.14em;color:#bcd0ff;border:1px solid rgba(255,255,255,.25);border-radius:999px;padding:4px 14px;margin-bottom:18px}}
.cover h1{{font-size:clamp(28px,4.6vw,44px);line-height:1.2;font-weight:800;margin-bottom:12px}}
.cover p.lead{{font-size:clamp(15px,1.6vw,17px);color:#d7e3ff;max-width:680px}}
.wrap{{max-width:860px;margin:0 auto;padding:32px 24px 80px}}
.toolbar{{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}}
.toolbar .count{{font-size:14px;color:var(--muted)}}
.list{{display:flex;flex-direction:column;gap:14px}}
.item{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px 24px;box-shadow:var(--shadow);display:flex;align-items:center;justify-content:space-between;gap:20px;transition:transform .15s,box-shadow .15s}}
.item:hover{{transform:translateY(-2px);box-shadow:0 4px 10px rgba(22,35,59,.08),0 16px 32px -16px rgba(22,35,59,.18);text-decoration:none}}
.item .info{{min-width:0;flex:1}}
.item .title{{font-size:17px;font-weight:700;color:var(--ink);line-height:1.4}}
.item:hover .title{{color:var(--blue)}}
.item .date{{flex:none;font-size:13px;color:var(--blue-deep);background:var(--blue-bg);padding:6px 12px;border-radius:999px;white-space:nowrap;font-weight:600}}
footer{{max-width:860px;margin:0 auto;padding:24px;font-size:12.5px;color:var(--muted-2);text-align:center}}
footer a{{color:var(--muted)}}
</style>
</head>
<body>
<header class="cover">
  <div class="cover-inner">
    <span class="kicker">NOTES · ESSAYS · REPORTS</span>
    <h1>Jason 的小站</h1>
    <p class="lead">这里放着我写的一些长文和报告。点下面任意一篇就能读。</p>
  </div>
</header>
<main class="wrap">
  <div class="toolbar">
    <span class="count">{count_text}</span>
  </div>
  <div class="list">
{items_html}  </div>
</main>
<footer>
  Powered by <a href="https://pages.github.com/" target="_blank" rel="noopener">GitHub Pages</a> · 仓库 <a href="https://github.com/Jason-Super-Agent/Jason-Super-Agent.github.io" target="_blank" rel="noopener">Jason-Super-Agent/Jason-Super-Agent.github.io</a>
</footer>
</body>
</html>
'''

out_path = os.path.join(ROOT, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(out)
print(f"Generated index.html with {len(posts)} posts at {out_path}")

# ── Inject a "back to home" floating button into every sub HTML (idempotent) ──
NAV_MARKER = "<!-- blog-nav-injected -->"
NAV_SNIPPET = NAV_MARKER + """
<style>
.blog-nav-btn{position:fixed;top:14px;left:14px;z-index:9999;background:rgba(15,30,70,.88);color:#fff!important;padding:8px 14px;border-radius:10px;font-size:13px;line-height:1;text-decoration:none!important;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);box-shadow:0 2px 10px rgba(0,0,0,.25);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;display:inline-flex;align-items:center;gap:6px;transition:background .15s,transform .15s}
.blog-nav-btn:hover{background:rgba(29,78,216,.95);transform:translateY(-1px)}
@media(max-width:600px){.blog-nav-btn{top:10px;left:10px;padding:7px 12px;font-size:12.5px}}
</style>
<a href="/" class="blog-nav-btn">&#8592; 返回首页</a>
"""

injected = []
for name in sorted(os.listdir(ROOT)):
    full = os.path.join(ROOT, name)
    if not os.path.isfile(full): continue
    if not name.lower().endswith(".html"): continue
    if name == "index.html": continue
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if NAV_MARKER in content:
            continue  # already injected, skip
        # Insert right before </body> (case-insensitive)
        m = re.search(r"</body\s*>", content, re.I)
        if not m:
            continue
        new_content = content[:m.start()] + NAV_SNIPPET + "\n" + content[m.start():]
        with open(full, "w", encoding="utf-8") as f:
            f.write(new_content)
        injected.append(name)
    except Exception as e:
        print(f"  ! inject skipped for {name}: {e}", file=sys.stderr)

if injected:
    print(f"Injected back-to-home nav into: {', '.join(injected)}")
else:
    print("No new pages needed nav injection.")

# ── Inject giscus comment widget into every sub HTML (idempotent) ──
GISCUS_MARKER = "<!-- giscus-injected -->"
GISCUS_SNIPPET = GISCUS_MARKER + """
<section class="giscus-section" style="max-width:860px;margin:48px auto 24px;padding:0 24px;">
  <div class="giscus"></div>
</section>
<script src="https://giscus.app/client.js"
        data-repo="Jason-Super-Agent/Jason-Super-Agent.github.io"
        data-repo-id="R_kgDOUdAxLQ"
        data-category="Announcements"
        data-category-id="DIC_kwDOUdAxLc4DFuw7"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="light"
        data-lang="zh-CN"
        crossorigin="anonymous"
        async>
</script>
"""

giscus_injected = []
for name in sorted(os.listdir(ROOT)):
    full = os.path.join(ROOT, name)
    if not os.path.isfile(full): continue
    if not name.lower().endswith(".html"): continue
    if name == "index.html": continue
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if GISCUS_MARKER in content:
            continue
        m = re.search(r"</body\s*>", content, re.I)
        if not m:
            continue
        new_content = content[:m.start()] + GISCUS_SNIPPET + "\n" + content[m.start():]
        with open(full, "w", encoding="utf-8") as f:
            f.write(new_content)
        giscus_injected.append(name)
    except Exception as e:
        print(f"  ! giscus inject skipped for {name}: {e}", file=sys.stderr)

if giscus_injected:
    print(f"Injected giscus comments into: {', '.join(giscus_injected)}")
else:
    print("No new pages needed giscus injection.")
