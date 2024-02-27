from os import remove, path
from threading import Thread
from webbrowser import open as browse
import tkinter as tk
from tkinter.ttk import *
from tkinter import Menu, filedialog
from mailmerge import MailMerge
from docx2pdf import convert as docx2pdf

from sheet import GoogleSheet
from res import title, spreadsheet_url, sheet_name, ftypes, temp_path, settings_path
from top_window import view_credits, showinfo, showerror

class ScoutMergerGUI:
    def __init__(self) -> None:
        self.loc_picked: bool = False
        self.model_picked: bool = False
        self.field_to_insert: dict[str, tuple[Label, Entry]] = {}

        thread = Thread(target=self.connect_spreadsheet)
        thread.start()

        self.loadbar_win = tk.Tk()
        self.loadbar_win.geometry("300x50")
        self.loadbar_win.resizable(False, False)
        self.loadbar_win.title(title)
        loadbar = Progressbar(self.loadbar_win, orient=tk.HORIZONTAL, length=280, mode="indeterminate")
        loadbar.grid(row=0, column=0, padx=10, pady=10)
        loadbar.start()
        self.loadbar_win.mainloop()
        loadbar.stop()

        thread.join()
        if self.spreadsheet == None:
            showerror("db")
            return

        self.loadbar_win.destroy()
        self.setup_window()
        if path.isfile(settings_path):
            with open(settings_path, "r") as settings_file:
                prev_model = settings_file.readline().strip()
                if path.isfile(prev_model):
                    self.upload_model(prev_model)
        self.window.mainloop()

    def connect_spreadsheet(self):
        self.spreadsheet = GoogleSheet(spreadsheet_url)
        try:
            self.load_db()
        except:
            self.spreadsheet = None

        self.loadbar_win.quit()

    def load_db(self):
        self.loc_info = self.spreadsheet.read(sheet_name)
        self.header = list(self.loc_info.columns.values)
        self.loc_info = self.loc_info.dropna(subset=self.header[0]).sort_values(self.header[0]).fillna("")

    def setup_window(self):
        self.window = tk.Tk()
        self.window.geometry("700x400")
        self.window.minsize(700, 400)
        self.window.title(title)
        self.window.focus_force()
        self.window.rowconfigure(1, weight=1)
        self.window.columnconfigure(0, weight=1)

        self.menu_bar = Menu(self.window)
        self.instruction_menu = Menu(self.menu_bar, tearoff=False)
        self.database_menu = Menu(self.menu_bar, tearoff=False)
        self.database_menu.add_command(label="Apri database", command=lambda:browse(spreadsheet_url))
        self.database_menu.add_command(label="Aggiorna database", command=self.update_db)
        self.database_menu.add_command(label="Download database", command=self.download_db)
        self.menu_bar.add_cascade(label="Database", menu=self.database_menu)
        self.instruction_menu.add_command(label="Database", command=lambda:showinfo("db"))
        self.instruction_menu.add_command(label="Modello", command=lambda:showinfo("model"))
        self.instruction_menu.add_command(label="Richiesta", command=lambda:showinfo("request"))
        self.instruction_menu.add_separator()
        self.instruction_menu.add_command(label="Informazioni", command=lambda:view_credits(self.window))
        self.menu_bar.add_cascade(label="Guida", menu=self.instruction_menu)
        self.window.config(menu=self.menu_bar)

        self.loc_frame = Frame(self.window)
        self.loc_frame.grid(row=0, column=0, columnspan=2, pady=8, sticky=tk.N)
        self.loc_label = Label(self.loc_frame, text="Località:")
        self.loc_label.grid(row=0, column=0, padx=5)
        self.loc_combo = Combobox(self.loc_frame, values=list(self.loc_info[self.header[0]]), width=30)
        self.loc_combo.grid(row=0, column=1, padx=5)
        self.loc_combo.bind("<<ComboboxSelected>>", self.update_recap)
        
        self.recap_frame = Frame(self.window)
        self.recap_frame.grid(row=1, column=0, rowspan=2, padx=10, pady=8, sticky=tk.NW)
        self.recap_frame.columnconfigure(1, weight=1)
        self.recap_frame.rowconfigure(0, weight=1)
        self.header_frame = Frame(self.recap_frame)
        self.header_frame.grid(row=0, column=0, sticky=tk.NW)
        self.data_frame = Frame(self.recap_frame)
        self.data_frame.grid(row=0, column=1, sticky=tk.NW)
        self.recap_labels = [Label(self.header_frame, text=f"{head}:") for head in self.header]
        self.recap_values = [Label(self.data_frame, text="") for _ in range(len(self.header))]
        for row in range(len(self.header)):
            self.recap_labels[row].grid(row=row, column=0, padx=5)
            self.recap_values[row].grid(row=row, column=0, padx=5, sticky=tk.W)
        
        self.model_frame = Frame(self.window)
        self.model_frame.grid(row=1, column=1, padx=10, pady=8, sticky=tk.NE)
        self.model_frame.columnconfigure(0, minsize=110)
        self.model_frame.columnconfigure(1, minsize=140)
        self.model_label = Label(self.model_frame, text="Modello:")
        self.model_label.grid(row=0, column=0, padx=5)
        self.upload_button = Button(self.model_frame, text="Carica", command=self.upload_model)
        self.upload_button.grid(row=0, column=1, padx=5, pady=3, sticky=tk.W)
        self.model_name = Label(self.model_frame)
        self.model_name.grid(row=1, column=0, columnspan=2, padx=5, pady=3)

        self.notify_frame = Frame(self.window)
        self.notify_frame.grid(row=2, column=0, padx=20, pady=10, sticky=tk.SW)
        self.notify_label = Label(self.notify_frame, font=("Segoe UI", 12))
        self.notify_label.grid(row=0, column=0, pady=5)

        self.button_frame = Frame(self.window)
        self.button_frame.grid(row=2, column=1, padx=10, pady=12, sticky=tk.SE)
        self.save_button = Button(self.button_frame, text="Salva", state=tk.DISABLED, command=self.save)
        self.save_button.grid(row=0, column=0, padx=5)
        self.close_button = Button(self.button_frame, text="Chiudi", command=self.window.destroy)
        self.close_button.grid(row=0, column=1, padx=5)

    def try_enable_save(self):
        if self.loc_picked and self.model_picked:
            self.save_button.config(state=tk.ACTIVE)

    def update_db(self):
        self.notify_label.config(text="Aggiornamento database...", foreground="blue")
        self.window.update_idletasks()
        try:
            self.load_db()
        except:
            self.notify_label.config(text="Aggiornamento annullato", foreground="red")
            return
        current_index = self.loc_combo.current()
        self.loc_combo.config(values=list(self.loc_info[self.header[0]]))
        if current_index >= 0:
            self.loc_combo.current(current_index)
        self.update_recap(None)
        self.notify_label.config(text="Database aggiornato", foreground="green")

    def download_db(self):
        download_path: str = filedialog.asksaveasfilename(initialfile = f"{title}", defaultextension=ftypes["Excel"], filetypes=[ftypes["Excel"], ftypes["*"]])
        if download_path == "":
            self.notify_label.config(text="Download annullato", foreground="red")
            return
        self.notify_label.config(text="Download in corso...", foreground="blue")
        self.window.update_idletasks()

        try:
            self.spreadsheet.download(download_path)
        except:
            self.notify_label.config(text="Errore di connessione", foreground="red")
            return
        self.notify_label.config(text="Dowload completato", foreground="green")

    def update_recap(self, event):
        if self.loc_combo.current() < 0:
            return
        self.loc_dict = self.loc_info.loc[self.loc_info[self.header[0]] == self.loc_combo.get()].iloc[0]
        for value, data in zip(self.recap_values, self.loc_dict.values):
            if data == True:
                data = "\U00002705"
            elif data == False:
                data = "\U0000274c"
            value.config(text=data)
        
        self.loc_picked = True
        self.try_enable_save()
        self.notify_label.config(text="Località scelta", foreground="green")
        
    def upload_model(self, model_path: str = ""):
        if model_path == "":
            model_path = filedialog.askopenfilename(filetypes=[ftypes["Word"], ftypes["*"]])
            if model_path == "":
                self.notify_label.config(text="Caricamento annullato", foreground="red")
                return
            
        with open(settings_path, "w") as settings_file:
            print(model_path, file=settings_file)
        
        self.model = MailMerge(model_path)
        self.doc_field: list[str] = list(self.model.get_merge_fields())
        self.doc_field.sort(reverse=True)
        if self.doc_field == []:
            self.notify_label.config(text="Modello incorretto", foreground="red")
            return
        
        for label, entry in self.field_to_insert.values():
            label.destroy()
            entry.destroy()
        self.field_to_insert = {}
        row = 2
        for field in self.doc_field:
            if not (field in self.header):
                self.field_to_insert[field] = (Label(self.model_frame, text=field.replace("_", " ")), Entry(self.model_frame))
                self.field_to_insert[field][0].grid(row=row, column=0, padx=5)
                self.field_to_insert[field][1].grid(row=row, column=1, padx=5, pady=3)
                row += 1

        self.model_picked = True
        self.try_enable_save()
        self.model_name.config(text=model_path.split("/")[-1], foreground="blue")
        self.notify_label.config(text="Modello caricato", foreground="green")
                   
    def save(self):
        self.field_dict = {}
        for field in self.doc_field:
            if field in self.loc_dict.keys():
                self.field_dict[field] = self.loc_dict[field]
            else:
                self.field_dict[field] = self.field_to_insert[field][1].get()

        doc_path = filedialog.asksaveasfilename(initialfile = f"{self.loc_combo.get()}", defaultextension=ftypes["Word"], filetypes=[ftypes["Word"], ftypes["PDF"], ftypes["*"]])
        if doc_path == "":
            self.notify_label.config(text="Salvataggio annullato", foreground="red")
            return
        
        self.notify_label.config(text="Salvataggio in corso...", foreground="blue")
        self.window.update_idletasks()
        self.model.merge_templates([self.field_dict], "continuous_section")
        if doc_path.split(".")[-1] == "pdf":
            self.model.write(temp_path)
            docx2pdf(temp_path, doc_path)
            remove(temp_path)
        else:
            self.model.write(doc_path)

        self.notify_label.config(text="Richiesta salvata", foreground="green")



if __name__ == "__main__":
    ScoutMergerGUI()