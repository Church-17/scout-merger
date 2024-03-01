from tkinter import Listbox, Event, Frame
from tkinter.ttk import Combobox, Scrollbar

class AutoCombobox(Combobox):
    def __init__(self, *args, **kwargs):
        self.is_posted: bool = False
        self.is_select_restored: bool = True
        self.highlighted = -1
        self.selected = ""

        if "postcommand" in kwargs:
            self.old_postcommand = kwargs["postcommand"]
        else:
            self.old_postcommand = None
        kwargs["postcommand"] = self.postcommand

        super().__init__(*args, **kwargs)
        toplevel = self.winfo_toplevel()
        self.listbox_values = self["values"]

        self.frame = Frame(toplevel, background="white", highlightbackground="grey48", highlightthickness=1)
        self.listbox = Listbox(self.frame, activestyle="none", width=self["width"], borderwidth=0, highlightthickness=0)
        self.scrollbar = Scrollbar(self.frame, command=self.listbox.yview)
        self.listbox.grid(row=0, column=0, padx=(1, 3), pady=1)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.insert(0, *self["values"])
        self.resize_listbox()
        self.listbox.config(yscrollcommand = self.scrollbar.set)

        toplevel.bind("<Button-1>", self.click_event)
        toplevel.bind("<Configure>", self.click_event)
        self.bind("<KeyRelease>", self.type_event)
        self.listbox.bind("<Motion>", self.motion_event)
        self.listbox.bind("<Leave>", self.leave_event)

    def postcommand(self):
        if self.old_postcommand:
            self.old_postcommand()
        if self.is_posted:
            self.after(0, self.hide_listbox)
        self.after(0, lambda: self.tk.call("ttk::combobox::Unpost", self))

    def show_listbox(self):
        self.is_posted = True
        toplevel = self.winfo_toplevel()
        self.frame.place(x=self.winfo_rootx()-toplevel.winfo_rootx(), y=self.winfo_rooty()-toplevel.winfo_rooty()+self.winfo_height())
        self.frame.lift()

    def hide_listbox(self):
        self.is_posted = False
        self.frame.place_forget()

    def update_values(self, text):
        self.listbox_values = [opt for opt in self["values"] if text in opt.lower()]
        self.listbox.delete(0, "end")
        self.listbox.insert(0, *self.listbox_values)
        self.resize_listbox()
        if self.selected in self.listbox_values:
            self.is_select_restored = False
            self.highlight(self.listbox_values.index(self.selected))

    def select(self):
        selection = self.listbox.curselection()
        if selection:
            self.selected = self.listbox_values[selection[0]]
            self.set(self.listbox.selection_get())
            self.hide_listbox()
            self.event_generate("<<ComboboxSelected>>")

    def highlight(self, index):
        self.listbox.itemconfig(index, {"bg": "#0078d7"})
        self.listbox.itemconfig(index, {"fg": "white"})

    def unhighlight(self, index):
        self.listbox.itemconfig(index, {"bg": "white"})
        self.listbox.itemconfig(index, {"fg": "black"})

    def resize_listbox(self):
        if self.listbox.size() <= int(self["height"]):
            height = self.listbox.size()
            self.scrollbar.grid_forget()
        else:
            height = self["height"]
            self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(height=height)

    def click_event(self, event: Event):
        if self.is_posted and event.widget != self and event.widget != self.listbox and event.widget != self.scrollbar and event.widget != self.frame:
            self.hide_listbox()
        elif event.widget == self:
            if self.is_posted:
                self.type_event(None)
            else:
                self.show_listbox()
                if self.get().lower() in list(map(lambda s: s.lower(), self["values"])):
                    self.update_values("")
                    self.select_range(0, "end")
                if self.selected in self.listbox_values:
                    self.listbox.see(self.listbox_values.index(self.selected))
        elif event.widget == self.listbox:
            self.select()

    def type_event(self, event):
        if not self.is_posted:
            self.show_listbox()
        typed_text = self.get().lower()
        self.update_values(typed_text)

    def motion_event(self, event: Event):
        if not self.is_select_restored:
            self.is_select_restored = True
            if self.selected in self.listbox_values:
                self.unhighlight(self.listbox_values.index(self.selected))
        index = self.listbox.index(f"@{event.x},{event.y}")
        if self.highlighted != index:
            if self.highlighted != -1 and self.highlighted < self.listbox.size():
                self.unhighlight(self.highlighted)
            self.highlight(index)
        self.highlighted = index

    def leave_event(self, event):
        if self.highlighted != -1 and self.highlighted < self.listbox.size():
            self.unhighlight(self.highlighted)
            self.highlighted = -1
