import json
import sys
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from threading import Thread
from polarai_core import list_models,generate
from agent_engine import execute
from polarai_core import generate_messages
from threading import Event

APP_SLUG='polarwriter'
TITLE='PolarWriter'
SYSTEM='Scrivi, correggi o riassumi il testo.'
def main():
    root=tk.Tk()
    root.title(TITLE+" | PolarLabs")
    try:
        icon_root=Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent))
        root.iconbitmap(default=str(icon_root/("polarwriter"+".ico")))
    except (OSError,tk.TclError):pass
    root.geometry("900x820")
    root.minsize(650,520)
    root.configure(bg="#F7FAFC")
    navy="#09263B"; teal="#138A91"; bg="#F7FAFC"
    header=tk.Frame(root,bg=bg)
    header.pack(fill="x",padx=24,pady=(20,12))
    tk.Label(header,text=TITLE,font=("Segoe UI",23,"bold"),fg=navy,bg=bg).pack(anchor="w")
    tk.Label(header,text="AI locale · PolarLabs OSS",fg="#617D8F",bg=bg).pack(anchor="w")
    settings=tk.Frame(root,bg=bg)
    settings.pack(fill="x",padx=24)
    tk.Label(settings,text="Server AI",fg=navy,bg=bg).grid(row=0,column=0,sticky="w")
    tk.Label(settings,text="Modello",fg=navy,bg=bg).grid(row=0,column=1,sticky="w")
    address=tk.StringVar(value="http://127.0.0.1:1234/v1")
    url_entry=tk.Entry(settings,textvariable=address,font=("Segoe UI",10))
    url_entry.grid(row=1,column=0,sticky="ew",padx=(0,10),ipady=6)
    chosen=tk.StringVar()
    config_path=Path.home()/".polaragents"/(APP_SLUG+".json")
    try:
        saved=json.loads(config_path.read_text(encoding="utf-8"))
        address.set(saved.get("url",address.get()))
        chosen.set(saved.get("model",""))
    except (OSError,ValueError,TypeError):pass
    def save_config():
        config_path.parent.mkdir(parents=True,exist_ok=True)
        config_path.write_text(json.dumps({"url":address.get(),"model":chosen.get()},indent=2),encoding="utf-8")
    picker=ttk.Combobox(settings,textvariable=chosen,width=22)
    picker.grid(row=1,column=1,sticky="ew",padx=(0,10))
    settings.grid_columnconfigure(0,weight=2);settings.grid_columnconfigure(1,weight=1)
    status=tk.StringVar(value="Pronto. Avvia un server AI locale.")
    workspace=tk.StringVar(value=str(Path.home()/"Documents"))
    def select_folder():
        selected=filedialog.askdirectory(initialdir=workspace.get())
        if selected:workspace.set(selected)
    workspace_row=tk.Frame(root,bg=bg);workspace_row.pack(fill="x",padx=24,pady=6)
    tk.Label(workspace_row,text="Cartella autorizzata:",fg=navy,bg=bg).pack(side="left")
    tk.Entry(workspace_row,textvariable=workspace,fg=navy).pack(side="left",fill="x",expand=True,padx=8)
    tk.Button(workspace_row,text="Scegli",command=select_folder,bg="#EEF5F8",fg=navy).pack(side="right")
    def background(fn):
        def run():
            try:fn()
            except Exception as exc:
                message=str(exc)
                def failed():
                    working["busy"]=False
                    status.set("Errore: "+message)
                root.after(0,failed)
        Thread(target=run,daemon=True).start()
    def connect():
        status.set("Connessione…")
        def work():
            found=list_models(address.get())
            def done():
                picker["values"]=found
                if found and chosen.get() not in found:chosen.set(found[0])
                save_config()
                status.set("Connesso: "+str(len(found))+" modelli disponibili")
            root.after(0,done)
        background(work)
    tk.Button(settings,text="Connetti",command=connect,bg=teal,fg="white",relief="flat",padx=14,pady=7).grid(row=1,column=2)
    tk.Label(root,text="Richiesta / contenuto",fg=navy,bg=bg,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=24,pady=(16,5))
    inputbox=tk.Text(root,height=10,wrap="word",font=("Segoe UI",10),bg="white",fg=navy)
    inputbox.pack(fill="both",expand=True,padx=24)
    actions=tk.Frame(root,bg=bg);actions.pack(fill="x",padx=24,pady=10)
    def load():
        filename=filedialog.askopenfilename(filetypes=[("Testo e dati","*.txt *.md *.csv *.json *.py *.xml"),("Tutti","*.*")])
        if not filename:return
        try:
            if Path(filename).stat().st_size>2000000:raise ValueError("File troppo grande (massimo 2 MB)")
            inputbox.delete("1.0","end")
            inputbox.insert("1.0",Path(filename).read_text(encoding="utf-8"))
        except Exception as exc:messagebox.showerror(TITLE,str(exc))
    tk.Button(actions,text="Apri file",command=load,relief="flat",bg="#EEF5F8",fg=navy,padx=13,pady=8).pack(side="left")
    stop_event=Event()
    working={'busy':False}
    def submit():
        prompt=inputbox.get("1.0","end-1c").strip()
        if not prompt or not chosen.get():
            messagebox.showwarning(TITLE,"Inserisci il testo e seleziona un modello.")
            return
        if working['busy']:return
        working['busy']=True
        stop_event.clear()
        save_config()
        status.set("Generazione…")
        def approval(action,path,details):
            ready=Event();answer={"allowed":False}
            def show():
                answer["allowed"]=messagebox.askyesno(TITLE+" - Conferma operazione",
                    action+"\n"+path+"\n\nAnteprima:\n"+details[:900])
                ready.set()
            root.after(0,show)
            ready.wait()
            return answer["allowed"] and not stop_event.is_set()
        def log(text):
            def update():
                status.set(text)
                logbox.configure(state="normal")
                logbox.insert("end",text+"\n")
                logbox.see("end")
                logbox.configure(state="disabled")
            root.after(0,update)
        def work():
            response=execute(prompt,APP_SLUG,workspace.get(),
                lambda messages: generate_messages(address.get(),chosen.get(),messages),
                approval,log,stop_event.is_set,specialty=SYSTEM)
            def done():
                working['busy']=False
                output.delete("1.0","end");output.insert("1.0",response)
                status.set("Attività completata")
            root.after(0,done)
        background(work)
    tk.Button(actions,text="Interrompi",command=stop_event.set,bg="#E8EBF2",fg=navy,relief="flat",padx=14,pady=8).pack(side="right",padx=(8,0))
    tk.Button(actions,text="Avvia agente",command=submit,bg=teal,fg="white",relief="flat",padx=16,pady=8).pack(side="right")
    tk.Label(root,text="Risultato",fg=navy,bg=bg,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=24)
    output=tk.Text(root,height=10,wrap="word",font=("Segoe UI",10),bg="white",fg=navy)
    output.pack(fill="both",expand=True,padx=24,pady=(5,8))
    tk.Label(root,text="Registro delle operazioni",fg=navy,bg=bg,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=24)
    logbox=tk.Text(root,height=4,wrap="word",font=("Consolas",9),bg="#EEF5F8",fg=navy,state="disabled")
    logbox.pack(fill="x",padx=24,pady=(4,8))
    def export():
        filename=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Testo","*.txt"),("Markdown","*.md")])
        if filename:Path(filename).write_text(output.get("1.0","end-1c"),encoding="utf-8")
    tk.Button(root,text="Esporta TXT",command=export,relief="flat",bg="#EEF5F8",fg=navy,padx=14,pady=7).pack(anchor="e",padx=24)
    tk.Label(root,textvariable=status,fg="#617D8F",bg=bg,anchor="w").pack(fill="x",padx=24,pady=12)
    root.mainloop()
if __name__=="__main__":main()
