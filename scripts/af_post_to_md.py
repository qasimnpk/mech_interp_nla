import json, re, sys, html
from html.parser import HTMLParser
class MD(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.o=[]; s.ls=[]; s.href=None; s.pre=False; s.skip=0; s.bq=0
    def handle_starttag(s,t,at):
        a=dict(at)
        if t in('script','style'): s.skip+=1; return
        if t in('h1','h2','h3','h4','h5','h6'): s.o.append('\n\n'+'#'*(int(t[1])+1)+' ')
        elif t=='p': s.o.append('\n\n'+('> ' if s.bq else ''))
        elif t=='br': s.o.append('  \n')
        elif t in('strong','b'): s.o.append('**')
        elif t in('em','i'): s.o.append('*')
        elif t=='a': s.href=a.get('href'); s.o.append('[')
        elif t=='ul': s.ls.append('ul'); s.o.append('\n')
        elif t=='ol': s.ls.append(1); s.o.append('\n')
        elif t=='li':
            ind='  '*(len(s.ls)-1); top=s.ls[-1] if s.ls else 'ul'
            if top=='ul': s.o.append('\n'+ind+'- ')
            else: s.o.append('\n'+ind+f'{top}. '); s.ls[-1]+=1
        elif t=='blockquote': s.bq+=1; s.o.append('\n\n> ')
        elif t=='pre': s.pre=True; s.o.append('\n\n```\n')
        elif t=='code' and not s.pre: s.o.append('`')
        elif t=='hr': s.o.append('\n\n---\n\n')
        elif t=='img': s.o.append(f"![{a.get('alt','')}]({a.get('src','')})")
    def handle_endtag(s,t):
        if t in('script','style'): s.skip-=1; return
        if t in('strong','b'): s.o.append('**')
        elif t in('em','i'): s.o.append('*')
        elif t=='a': s.o.append(f']({s.href})' if s.href else ']'); s.href=None
        elif t in('ul','ol'):
            if s.ls: s.ls.pop()
            s.o.append('\n')
        elif t=='blockquote': s.bq-=1; s.o.append('\n')
        elif t=='pre': s.pre=False; s.o.append('\n```\n')
        elif t=='code' and not s.pre: s.o.append('`')
        elif t in('h1','h2','h3','h4','h5','h6','p'): s.o.append('\n')
    def handle_data(s,d):
        if s.skip: return
        if s.pre: s.o.append(d); return
        d=re.sub(r'\s+',' ',d)
        s.o.append(d)
src=sys.argv[1]; url=sys.argv[2]; out=sys.argv[3]
body=None; meta={}
try:
    j=json.load(open(src)); r=j['data']['post']['result']
    body=r['htmlBody']; meta={'title':r['title'],'date':r['postedAt'][:10],'words':r.get('wordCount'),
      'authors':', '.join([r['user']['displayName']]+[c['displayName'] for c in (r.get('coauthors') or [])])}
except Exception as e:
    print('graphql parse failed:',e,file=sys.stderr); sys.exit(2)
p=MD(); p.feed(body); md=''.join(p.o)
md=re.sub(r'[ \t]+\n','\n',md); md=re.sub(r'\n{3,}','\n\n',md).strip()
hdr=(f"# {meta['title']}\n\n**Authors:** {meta['authors']}  \n**Posted:** {meta['date']}  \n**Source:** {url}  \n"
     f"**Words:** {meta['words']}  \n**Archived:** 2026-09-05 via the Alignment Forum GraphQL API, converted to markdown (stdlib parser; comments not included).\n\n---\n\n")
open(out,'w').write(hdr+md+'\n')
print('ok', meta, 'md chars', len(md))
