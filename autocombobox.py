from tkinter import Listbox, Event, Frame
from tkinter.ttk import Combobox, Scrollbar

class AutoCombobox(Combobox):
    """Autocomplete Combobox"""

    def __init__(self, *args, **kwargs):
        """
        Create an Autocomplete ttk Combobox.

        Options are the same as the normal ttk Combobox.
        """

        # Declare helper variables
        self._is_posted: bool = False
        self._is_select_restored: bool = True
        self._highlighted = -1
        self._selected = ""

        # Create Combobox object
        super().__init__(*args)
        self.configure(**kwargs)
        self.config = self.configure

        # Declare dependent variables
        toplevel = self.winfo_toplevel()
        self._listbox_values = self["values"]

        # Create & configure listbox frane
        self.frame = Frame(toplevel, background="white", highlightbackground="red", highlightthickness=1)
        self.listbox = Listbox(self.frame, activestyle="none", width=self["width"], borderwidth=0, highlightthickness=0)
        self.scrollbar = Scrollbar(self.frame, command=self.listbox.yview)
        self.listbox.grid(row=0, column=0, padx=(1, 3), pady=1)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.update_values("")
        self.listbox.config(yscrollcommand = self.scrollbar.set)

        # Bind events
        toplevel.bind("<Button-1>", self._click_event)      # Handle mouse click
        toplevel.bind("<Configure>", self._window_event)    # Handle window events
        self.bind("<KeyRelease>", self._type_event)         # Handle keyboard typing to display coherent options
        self.listbox.bind("<Motion>", self._motion_event)   # Handle mouse movement to control highlight
        self.listbox.bind("<Leave>", self._leave_event)     # Handle mouse movement to control highlight
        self.bind("<Up>", self._arrow_event)                # Handle UP key to control highlight
        self.bind("<Down>", self._arrow_event)              # Handle DOWN key to control highlight

    # Override configure method to always handle options
    def configure(self, *args, **kwargs):
        if "postcommand" in kwargs:
            self._old_postcommand = kwargs["postcommand"]
        else:
            self._old_postcommand = None
        kwargs["postcommand"] = self._postcommand
        return super().configure(*args, **kwargs)

    def show_listbox(self):
        """Open the Combobox popdown"""
        self._is_posted = True
        toplevel = self.winfo_toplevel()
        self.frame.place(x=self.winfo_rootx()-toplevel.winfo_rootx(), y=self.winfo_rooty()-toplevel.winfo_rooty()+self.winfo_height())
        self.frame.lift()
        self.update_values()

    def hide_listbox(self):
        """Hide the Combobox popdown"""
        self._is_posted = False
        self.frame.place_forget()

    def update_values(self, text: str | None = None):
        """Update listbox values to show coherent options"""

        if text == None:
            text = self.get()

        # Change listbox values
        self._listbox_values = [opt for opt in self["values"] if text.lower() in opt.lower()]
        self.listbox.delete(0, "end")
        self.listbox.insert(0, *self._listbox_values)

        # Adapt listbox geight and don't show scrollbar if it isn't needed
        if self.listbox.size() <= int(self["height"]):
            height = self.listbox.size()
            self.scrollbar.grid_forget()
        else:
            height = self["height"]
            self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(height=height)

        # Highlight _selected option if it is in listbox
        if self._selected in self._listbox_values:
            self._is_select_restored = False
            self.highlight(self._listbox_values.index(self._selected))

    def select(self):
        """Select a value"""

        # If something is _selected, set Combobox on that value
        selection = self.listbox.curselection()
        if selection:
            self._selected = self._listbox_values[selection[0]]
            self.set(self.listbox.selection_get())
            self.hide_listbox()
            self.event_generate("<<ComboboxSelected>>")

    def highlight(self, index: int):
        """Highlight the option corresponding to the given index"""
        self._highlighted = index
        self.listbox.itemconfig(index, {"bg": "#0078d7"})
        self.listbox.itemconfig(index, {"fg": "white"})

    def unhighlight(self, index):
        """Remove highlight from the option corresponding to the given index"""
        self._highlighted = -1
        self.listbox.itemconfig(index, {"bg": "white"})
        self.listbox.itemconfig(index, {"fg": "black"})

    def _click_event(self, event: Event):
        """Handle mouse click"""

        # Hide listbox if clicked outside
        if self._is_posted and event.widget != self and event.widget != self.listbox and event.widget != self.scrollbar and event.widget != self.frame:
            self.hide_listbox()

        elif event.widget == self:
            # If listbox is open, update it
            if self._is_posted:
                self.update_values()

            # If listbox is not opened, open it
            else:
                self.show_listbox()

                # If the current text is an option, reset listbox & select text
                if self.get().lower() in list(map(lambda s: s.lower(), self["values"])):
                    self.update_values("")
                    self.select_range(0, "end")

                # If the _selected option is in listbox, view it
                if self._selected in self._listbox_values:
                    self.listbox.see(self._listbox_values.index(self._selected))

        # If clicked on listobox select the option
        elif event.widget == self.listbox:
            self.select()

    def _window_event(self, event: Event):
        """Handle window events"""
        if self._is_posted and event.widget == self.winfo_toplevel():
            self.hide_listbox()

    def _type_event(self, event):
        """Handle keyboard typing"""
        if not self._is_posted:
            self.show_listbox()
        self.update_values()

    def _motion_event(self, event: Event):
        """Handel mouse movement"""
        # Restore highlight of _selected option if needed    
        if not self._is_select_restored:
            self._is_select_restored = True
            if self._selected in self._listbox_values:
                self.unhighlight(self._listbox_values.index(self._selected))

        # Highlight option under mouse and remove highlight from the old one
        index = self.listbox.index(f"@{event.x},{event.y}")
        if self._highlighted != index:
            if self._highlighted >= 0 and self._highlighted < self.listbox.size():
                self.unhighlight(self._highlighted)
            self.highlight(index)

    def _leave_event(self, event):
        """Handel mouse leaving listbox"""
        if self._highlighted >= 0 and self._highlighted < self.listbox.size():
            self.unhighlight(self._highlighted)

    def _arrow_event(self, event: Event):
        if event.keysym == "Down":
            direction = 1
        elif event.keysym == "Up":
            direction = -1
        
        new_highlight = self._highlighted + direction
        if new_highlight >= 0 and new_highlight < self.listbox.size():
            if self._highlighted >= 0:
                self.unhighlight(self._highlighted)
            self.highlight(new_highlight)
        return "break"

    def _postcommand(self):
        """Define new postcommand function to show only the new listbox and not the internal one"""
        # Execute user postcommand if there is one
        if self._old_postcommand:
            self._old_postcommand()
        
        # If the listbox is opened, hide it
        if self._is_posted:
            self.after(0, self.hide_listbox)

        # Hide internal listbox
        self.after(0, lambda: self.tk.call("ttk::combobox::Unpost", self))
