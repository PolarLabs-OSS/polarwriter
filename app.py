import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from pathlib import Path
from threading import Thread
from polarai_core import list_models,generate

TITLE='PolarWriter'
SYSTEM='Scrivi, correggi o riassumi il testo.'
def main():
    root=tk.Tk()
    root.title(TITLE+" | PolarLabs")
    root.geometry("840x720")
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
    picker=ttk.Combobox(settings,textvariable=chosen,width=22)
    picker.grid(row=1,column=1,sticky="ew",padx=(0,10))
    settings.grid_columnconfigure(0,weight=2);settings.grid_columnconfigure(1,weight=1)
    status=tk.StringVar(value="Pronto. Avvia LM Studio, Ollama o altro server API compatibile.")
    def background(fn):
        def run():
            try:fn()
            except Exception as exc:
                message=str(exc)
                root.after(0,lambda:status.set("Errore: "+message))
        Thread(target=run,daemon=True).start()
    def connect():
        status.set("Connessione…")
        def work():
            found=list_models(address.get())
            def done():
                picker["values"]=found
                if found:chosen.set(found[0])
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
    def submit():
        prompt=inputbox.get("1.0","end-1c").strip()
        if not prompt or not chosen.get():
            messagebox.showwarning(TITLE,"Inserisci il testo e seleziona un modello.")
            return
        status.set("Generazione…")
        def work():
            response=generate(address.get(),chosen.get(),SYSTEM,prompt)
            def done():
                output.delete("1.0","end");output.insert("1.0",response)
                status.set("Risposta completata")
            root.after(0,done)
        background(work)
    tk.Button(actions,text="Genera",command=submit,bg=teal,fg="white",relief="flat",padx=16,pady=8).pack(side="right")
    tk.Label(root,text="Risultato",fg=navy,bg=bg,font=("Segoe UI",11,"bold")).pack(anchor="w",padx=24)
    output=tk.Text(root,height=10,wrap="word",font=("Segoe UI",10),bg="white",fg=navy)
    output.pack(fill="both",expand=True,padx=24,pady=(5,8))
    def export():
        filename=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Testo","*.txt"),("Markdown","*.md")])
        if filename:Path(filename).write_text(output.get("1.0","end-1c"),encoding="utf-8")
    tk.Button(root,text="Esporta TXT",command=export,relief="flat",bg="#EEF5F8",fg=navy,padx=14,pady=7).pack(anchor="e",padx=24)
    tk.Label(root,textvariable=status,fg="#617D8F",bg=bg,anchor="w").pack(fill="x",padx=24,pady=12)
    root.mainloop()
if __name__=="__main__":main()
