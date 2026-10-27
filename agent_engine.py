import json,csv,re,shutil
from pathlib import Path
MAX_STEPS=5
def scoped(root,name):
    base=Path(root).resolve()
    p=(base/str(name)).resolve()
    if p!=base and base not in p.parents:raise ValueError("Accesso fuori dalla cartella autorizzata")
    return p
def tools(app):
    return ["list_files","read_text","finish"]+{
      "polarwriter":["save_text"],"polardocs-ai":["search_text","save_text"],
      "polarfiles-ai":["move_file"],"polardata-ai":["csv_summary","save_text"],
      "polarcode-ai":["replace_text"],"polarmail-ai":["save_text"],"polartasks-ai":["save_text"]}[app]
def run_tool(tool,args,folder,approve):
    path=scoped(folder,args.get("path","."))
    if tool=="list_files":
        return json.dumps([{"name":p.name,"folder":p.is_dir()} for p in list(path.iterdir())[:200]])
    if tool in ("read_text","search_text"):
        if path.stat().st_size>200000:raise ValueError("Dimensione massima 200KB")
        value=path.read_text(encoding="utf-8")
        if tool=="search_text":
            q=str(args.get("query","")).lower()
            return "\n".join(str(i+1)+": "+line[:200] for i,line in enumerate(value.splitlines()) if q in line.lower())[:15000]
        return value
    if tool=="csv_summary":
        if path.stat().st_size>200000:raise ValueError("CSV troppo grande")
        with path.open(encoding="utf-8-sig",newline="") as f:
            rdr=csv.DictReader(f)
            rows=list(rdr)[:2000]
            return json.dumps({"columns":rdr.fieldnames,"rows":len(rows),"sample":rows[:5]},ensure_ascii=False)
    if tool=="save_text":
        if path.suffix.lower() not in (".txt",".md",".json",".csv"):raise ValueError("Estensione non consentita")
        content=str(args.get("content",""))[:200000]
        if not approve("Scrivere",str(path),content[:500]):return "RIFIUTATO"
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists():shutil.copy2(path,str(path)+".bak")
        path.write_text(content,encoding="utf-8")
        return "SCRITTO "+str(path)
    if tool=="move_file":
        dest=scoped(folder,args.get("destination",""))
        if not path.is_file() or dest.exists():raise ValueError("Percorso non valido")
        if not approve("Spostare",str(path),str(dest)):return "RIFIUTATO"
        dest.parent.mkdir(parents=True,exist_ok=True);path.rename(dest)
        return "SPOSTATO"
    if tool=="replace_text":
        old=str(args.get("find",""));new=str(args.get("replace",""))
        data=path.read_text(encoding="utf-8")
        if not old or old not in data:raise ValueError("Testo non trovato")
        if not approve("Modificare",str(path),old[:300]+" => "+new[:300]):return "RIFIUTATO"
        shutil.copy2(path,str(path)+".bak")
        path.write_text(data.replace(old,new,1),encoding="utf-8")
        return "MODIFICATO"
    raise ValueError("Strumento non valido")
def execute(goal,app,folder,model_fn,approve,log):
    allowed=tools(app)
    system=("Sei un agente PolarLabs. Restituisci ESCLUSIVAMENTE JSON nella forma "
      + '{"tool":"nome","args":{}}'+". Un passo alla volta. Strumenti: "+", ".join(allowed)
      +". Schemi: list_files {path}; read_text {path}; search_text {path,query}; csv_summary {path}; "
      +"save_text {path,content}; move_file {path,destination}; replace_text {path,find,replace}; finish {answer}. "
      +"Usa percorsi relativi alla cartella indicata. Non inventare i risultati.")
    history=[{"role":"system","content":system},{"role":"user","content":goal}]
    for index in range(MAX_STEPS):
        result=model_fn(history).strip()
        try:
            action=json.loads(result)
            if not isinstance(action,dict):raise ValueError("Not object")
        except ValueError:
            action={"tool":"finish","args":{"answer":result}}
        name=action.get("tool","finish");args=action.get("args",{})
        if not isinstance(args,dict):args={}
        if name=="finish":return str(args.get("answer",result))
        if name not in allowed:out="STRUMENTO NON CONSENTITO"
        else:
            try:out=run_tool(name,args,folder,approve)
            except Exception as err:out="ERRORE: "+str(err)
        log(str(index+1)+": "+name+" => "+out[:200])
        history.extend([{"role":"assistant","content":json.dumps(action)},{"role":"user","content":"Risultato reale dello strumento: "+out[:30000]}])
    return "Limite di passaggi raggiunto."
