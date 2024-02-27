from tempfile import gettempdir
from tkinter import messagebox

title: str = "ScoutMerger"
version: str = "1.0"
spreadsheet_id: str = "1prvCn3L06m3A7_31DEKfzN9CowLZK_2Gu-A6Q3VI-TY"
sheet_name: str = "Località"

ftypes: dict[str, tuple[str, str]] = {
    "Word": ("Word document","*.docx"),
    "Excel": ("Excel document","*.xlsx"),
    "PDF": ("PDF document","*.pdf"),
    "*": ("All files", "*.*")
}
temp_dir: str = gettempdir()
temp_path: str = f"{temp_dir}/{title}_tmp.docx"
settings_path: str = f"{temp_dir}/{title}_settings.ini"

infobox: dict[str, str] = {
    "db": "Il database contiene tutte le informazioni e i contatti riguardanti ogni località della Sardegna inserita. Ad ogni località è associato un gestore, ad ognuno di questi un'istituzione, ad ognuna di queste un ispettorato SIR.",
    "model": "Il modello deve essere un documento Word che fa da richiesta generica, composto di campi unione per le specifiche, come il nome della località o il gestore. I campi unione che verranno riempiti automaticamente sono quelli con i nomi uguali a quelli del database, gli altri come le date o i numeri saranno richiesti all'utente.",
    "request": "La richiesta compilata deve essere poi mandata per email o PEC all'istituzione di competenza, mettendo l'indirizzo del SIR in CC"
}
errorbox: dict[str, str] = {
    "db": "Il database online è irraggiungibile"
}

def showerror(err):
    messagebox.showerror(title, errorbox[err])

def showinfo(info):
    messagebox.showinfo(title, infobox[info])