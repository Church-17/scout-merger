import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox

from res import title, version, author, spreadsheet_url, repo_url
from webbrowser import open as browse

infobox: dict[str, str] = {
    "db": "Il database contiene tutte le informazioni e i contatti riguardanti ogni località della Sardegna inserita. Ad ogni località è associato un gestore, ad ognuno di questi un'istituzione, ad ognuna di queste un ispettorato SIR.",
    "model": "Il modello deve essere un documento Word che fa da richiesta generica, composto di campi unione per le specifiche come il nome della località o il gestore. I campi unione che verranno riempiti automaticamente sono quelli con i nomi uguali a quelli del database, gli altri come le date o i numeri saranno richiesti all'utente.",
    "request": "La richiesta compilata deve essere poi mandata per email o PEC all'istituzione di competenza, mettendo l'indirizzo del SIR in CC"
}
errorbox: dict[str, str] = {
    "db": "Il database online è irraggiungibile"
}

def showinfo(info):
    messagebox.showinfo(title, infobox[info])

def showerror(err):
    messagebox.showerror(title, errorbox[err])

def view_credits(parent_win: tk.Tk):
    top_win = tk.Toplevel(parent_win)
    top_win.geometry("200x200")
    top_win.resizable(False, False)
    top_win.title(title)
    top_win.rowconfigure(6, weight=1)
    top_win.columnconfigure(0, weight=1)

    info_label = Label(top_win, text="Informazioni", font=("Segoe UI", 14))
    info_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
    version_label = Label(top_win, text=f"{title}")
    version_label.grid(row=1, column=0, padx=20, sticky=tk.W)
    version_label = Label(top_win, text=f"Versione {version}")
    version_label.grid(row=2, column=0, padx=20, sticky=tk.W)
    author_label = Label(top_win, text=f"Creato da {author}")
    author_label.grid(row=3, column=0, padx=20, sticky=tk.W)
    db_label = Label(top_win, text=f"Database", font=("TkDefaultFont", 9, "underline"), foreground="blue", cursor="hand2")
    db_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky=tk.W)
    db_label.bind("<Button-1>", lambda e: browse(spreadsheet_url))
    repo_label = Label(top_win, text=f"Codice sorgente", font=("TkDefaultFont", 9, "underline"), foreground="blue", cursor="hand2")
    repo_label.grid(row=5, column=0, padx=20, sticky=tk.W)
    repo_label.bind("<Button-1>", lambda e: browse(repo_url))

    ok_button = Button(top_win, text="Ok", command=top_win.destroy)
    ok_button.grid(row=6, column=0, pady=5, sticky=tk.S)

    top_win.update()
