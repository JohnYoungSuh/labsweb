#!/usr/bin/env python3
"""
scripts/generate_site_json.py
Generates compact, token-efficient JSON mirrors of all HTML pages in suhlabs/lab-web.
Outputs:
  - site_manifest.json (root directory, master index of all pages)
  - data/pages/<page>.json (individual page structured representations)
"""

import glob
import json
import os
import re
from bs4 import BeautifulSoup

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    os.makedirs('data/pages', exist_ok=True)
    
    html_files = sorted(glob.glob('*.html'))
    site_corpus = {
        'generated_at': '2026-11-22T08:26:00Z',
        'repository': 'suhlabs/lab-web',
        'production_url': 'https://suhlabs.com',
        'total_pages': len(html_files),
        'pages': {}
    }

    for hf in html_files:
        with open(hf, 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        for s in soup(['script', 'style']):
            s.decompose()
            
        title = soup.title.string.strip() if soup.title else hf
        
        meta_desc = ''
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content'].strip()
            
        doc_id = hf.replace('.html', '')
        badge = soup.find(class_='badge-item') or soup.find(class_='pulse-dot')
        if badge and badge.parent:
            text = badge.parent.get_text()
            m = re.search(r'(POLICY-\d{4}-\d{2}|ARCH-\d{4}-\d{2}|MEMO-\d{4}-\d{2})', text)
            if m:
                doc_id = m.group(1)
                
        exec_summary = ''
        exec_box = soup.find(class_='exec-summary-box')
        if exec_box:
            exec_summary = ' '.join(exec_box.get_text().split())
        elif meta_desc:
            exec_summary = meta_desc
        else:
            p = soup.find('p')
            if p:
                exec_summary = ' '.join(p.get_text().split())
                
        sections = []
        for h in soup.find_all(['h2', 'h3']):
            htext = h.get_text().strip()
            if htext and not htext.startswith('//'):
                sections.append(htext)
                
        claims_boundary = ''
        for callout in soup.find_all(class_='callout-box'):
            if 'CLAIMS_BOUNDARY' in callout.get_text() or 'SCOPE' in callout.get_text():
                claims_boundary = ' '.join(callout.get_text().split())
                
        refs = []
        for li in soup.find_all('li'):
            bt = li.find(class_='bib-title')
            if bt:
                refs.append(bt.get_text().strip())
                
        page_data = {
            'id': doc_id,
            'file': hf,
            'url': f'https://suhlabs.com/{hf}',
            'title': title,
            'summary': exec_summary[:400] + ('...' if len(exec_summary) > 400 else ''),
            'sections': sections[:15],
            'claims_boundary': claims_boundary[:300] + ('...' if len(claims_boundary) > 300 else '') if claims_boundary else None,
            'primary_citations': refs[:8]
        }
        
        site_corpus['pages'][hf] = page_data
        
        page_json_path = f'data/pages/{hf.replace(".html", ".json")}'
        with open(page_json_path, 'w', encoding='utf-8') as pf:
            json.dump(page_data, pf, indent=2)

    with open('site_manifest.json', 'w', encoding='utf-8') as mf:
        json.dump(site_corpus, mf, indent=2)

    print(f'Successfully indexed {len(html_files)} HTML pages into site_manifest.json and data/pages/')

if __name__ == '__main__':
    main()
