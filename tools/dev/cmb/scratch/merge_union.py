import re,sys
for p in sys.argv[1:]:
    s=open(p).read()
    def fix(m):
        a,b=m.group(1),m.group(2)
        if re.search(r'^DEF5\d=',a+b,re.M):
            def parts(t):
                com=[l for l in t.splitlines() if not re.match(r'DEF5\d=',l)]
                d=re.search(r"^(DEF5\d)='([^']*)'(.*)$",t,re.M)
                return com,(d.group(1) if d else None),(d.group(2).split() if d else []),(d.group(3).strip() if d else '')
            ca,na,da,ta=parts(a); cb,nb,db,tb=parts(b)
            name=na or nb
            keys=da+[k for k in db if k not in da]
            com=ca+[c for c in cb if c not in ca]+['# '+t.lstrip('# ') for t in (ta,tb) if t]
            return '\n'.join(com+[name+"='"+' '.join(keys)+"'"])+'\n'
        al=a.splitlines(True); bl=b.splitlines(True)
        i=0
        while i<min(len(al),len(bl)) and al[i]==bl[i]: i+=1
        return ''.join(al)+''.join(bl[i:])
    s2,n=re.subn(r"<<<<<<< [^\n]*\n(.*?)=======\n(.*?)>>>>>>> [^\n]*\n",fix,s,flags=re.S)
    open(p,'w').write(s2); print(p,'resolved',n)
