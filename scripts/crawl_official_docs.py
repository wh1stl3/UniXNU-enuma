"""Inventory unixnu.com HTML routes and cache evidence under this repo's out/.

Traverse both locales, navbar/sidebar/body links, plus routes enumerated from
the pinned official docs source tree. Never follow external repositories,
download binaries or execute page scripts. Page content remains untrusted data.
"""
import concurrent.futures
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out/official-docs'


def route(url):
    p = urlsplit(url)
    if p.scheme not in ('http', 'https') or p.netloc.lower() != 'unixnu.com' or p.query:
        return None
    path = p.path
    if Path(path).suffix not in ('', '.html'):
        return None
    if path.endswith('.html'):
        path = path[:-5]
    return urlunsplit(('https', 'unixnu.com', path.rstrip('/') or '/', '', ''))


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = self.in_title = False
        self.ignored = 0
        self.content_depth = 0
        self.content_text = []
        self.text, self.title, self.headings, self.links, self.ids = [], [], [], [], set()
        self.heading = self.link = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'div':
            if values.get('id') == 'VPContent': self.content_depth = 1
            elif self.content_depth: self.content_depth += 1
        if tag == 'main': self.in_main = True
        if tag == 'title': self.in_title = True
        if tag in ('script', 'style'): self.ignored += 1
        if values.get('id'): self.ids.add(values['id'])
        if tag == 'a' and values.get('href'):
            self.link = {'href': values['href'], 'in_main': self.in_main, 'label': []}
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and self.in_main:
            self.heading = {'level': int(tag[1]), 'id': values.get('id'), 'text': []}
        if self.in_main and tag in ('p', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'pre', 'br'):
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag == 'main': self.in_main = False
        if tag == 'div' and self.content_depth: self.content_depth -= 1
        if tag == 'title': self.in_title = False
        if tag in ('script', 'style'): self.ignored -= 1
        if tag == 'a' and self.link:
            self.link['label'] = ''.join(self.link['label']).replace('\u200b', '').strip()
            self.links.append(self.link)
            self.link = None
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and self.heading:
            self.heading['text'] = ''.join(self.heading['text']).replace('\u200b', '').strip()
            self.headings.append(self.heading)
            self.heading = None
        if self.in_main and tag in ('p', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'pre'):
            self.text.append('\n')

    def handle_data(self, data):
        if self.ignored: return
        if self.in_title: self.title.append(data)
        if self.in_main: self.text.append(data)
        if self.content_depth: self.content_text.append(data)
        if self.heading: self.heading['text'].append(data)
        if self.link: self.link['label'].append(data)


def fetch(url):
    before = time.monotonic()
    entry = {'url': url, 'fetched_at_utc': datetime.now(timezone.utc).isoformat()}
    try:
        try:
            response = urlopen(Request(url, headers={'User-Agent': 'UniXNU-enuma documentation audit'}), timeout=25)
        except HTTPError as error:
            response = error
        with response:
            blob = response.read(2_000_001)
            if len(blob) > 2_000_000: raise ValueError('HTML size limit exceeded')
            entry.update(status=response.code, final_url=response.url, bytes=len(blob),
                         content_type=response.headers.get('Content-Type'))
        doc = Document()
        doc.feed(blob.decode('utf-8'))
        key = hashlib.sha256(url.encode()).hexdigest()[:20]
        (OUT / 'html' / (key + '.html')).write_bytes(blob)
        main = ''.join(doc.text).replace('\u200b', '').strip()
        entry['text_extraction'] = 'main'
        if not main:
            main = ''.join(doc.content_text).replace('\u200b', '').strip()
            entry['text_extraction'] = 'VPContent fallback for home'
        (OUT / 'text' / (key + '.txt')).write_text(main, encoding='utf-8')
        entry.update(sha256=hashlib.sha256(blob).hexdigest(), title=''.join(doc.title),
                     headings=doc.headings, links=doc.links, ids=sorted(doc.ids),
                     main_characters=len(main), cache_key=key)
    except Exception as error:
        entry['error'] = str(error)
    entry['elapsed_seconds'] = round(time.monotonic() - before, 3)
    return entry


def source_index():
    """Use an existing pinned index, or obtain the current official tree via gh."""
    index, routes = OUT / 'source-tree.json', OUT / 'source-routes.json'
    if index.exists() and routes.exists():
        return json.loads(index.read_text()), json.loads(routes.read_text())
    def api(endpoint):
        return json.loads(subprocess.check_output(['gh', 'api', endpoint], encoding='utf-8', timeout=60))
    commit = api('repos/UniXNU/UniXNU/commits/main')
    tree = api('repos/UniXNU/UniXNU/git/trees/' + commit['sha'] + '?recursive=1')
    if tree['truncated']: raise ValueError('Official source tree was truncated')
    files = [item for item in tree['tree'] if item['path'].startswith('docs/')]
    source = {'commit': commit['sha'], 'committed_at': commit['commit']['committer']['date'],
              'tree_truncated': False, 'files': files}
    urls = []
    for item in files:
        path = item['path']
        if not path.endswith('.md') or path.startswith('docs/.vitepress/'): continue
        path = path[len('docs/'):-3]
        if path == 'index': path = ''
        elif path.endswith('/index'): path = path[:-6]
        urls.append('https://unixnu.com/' + path)
    index.write_text(json.dumps(source, indent=2) + '\n')
    routes.write_text(json.dumps(sorted(urls), indent=2) + '\n')
    return source, urls


def main():
    for name in ('html', 'text'): (OUT / name).mkdir(parents=True, exist_ok=True)
    source, source_routes = source_index()
    seeds = ['https://unixnu.com/zh/porting/', 'https://unixnu.com/zh/devices/']
    pending = {route(u) for u in seeds + source_routes}
    pages, external = {}, set()
    while pending:
        batch = sorted(pending)[:12]
        pending.difference_update(batch)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            for result in pool.map(fetch, batch):
                pages[result['url']] = result
                if result.get('status') != 200: continue
                for link in result.get('links', []):
                    absolute = urljoin(result.get('final_url', result['url']), link['href'])
                    candidate = route(absolute)
                    if candidate and candidate not in pages: pending.add(candidate)
                    if urlsplit(absolute).netloc not in ('', 'unixnu.com'): external.add(absolute)
        pending.difference_update(pages)
        if len(pages) + len(pending) > 400: raise ValueError('Unexpected route expansion; inspect before proceeding')
        (OUT / 'crawl.json').write_text(json.dumps({'source_commit': source['commit'],
             'source_tree_truncated': source['tree_truncated'], 'seeds': seeds,
             'source_route_count': len(source_routes), 'pending': sorted(pending),
             'pages': [pages[u] for u in sorted(pages)], 'external_links': sorted(external)},
             ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Fetched ' + str(len(pages)) + '; pending ' + str(len(pending)), flush=True)
        time.sleep(0.15)
    errors = [{'url': u, 'status': p.get('status'), 'error': p.get('error')}
              for u, p in pages.items() if p.get('status') != 200 or p.get('error')]
    print(json.dumps({'pages': len(pages), 'errors': errors, 'external_links': len(external)}))


if __name__ == '__main__': main()
