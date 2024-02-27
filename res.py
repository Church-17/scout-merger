from tempfile import gettempdir

title: str = "ScoutMerger"
author: str = "Matteo Chiesa"
version: str = "1.0"

spreadsheet_url: str = "https://docs.google.com/spreadsheets/d/1prvCn3L06m3A7_31DEKfzN9CowLZK_2Gu-A6Q3VI-TY"
sheet_name: str = "Località"
repo_url: str = "https://github.com/Church-17/scout_merger"

ftypes: dict[str, tuple[str, str]] = {
    "Word": ("Word document","*.docx"),
    "Excel": ("Excel document","*.xlsx"),
    "PDF": ("PDF document","*.pdf"),
    "*": ("All files", "*.*")
}
temp_dir: str = gettempdir()
temp_path: str = f"{temp_dir}/{title}_tmp.docx"
settings_path: str = f"{temp_dir}/{title}_settings.ini"
