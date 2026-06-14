from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

from .assets import GUI_COLORS
from .metadata import APP_NAME, APP_VERSION, DEFAULT_TABLE_MARKER
from .report import build_report

if TYPE_CHECKING:
    import tkinter as tk


def load_tkinter_gui_modules() -> None:
    global tk, filedialog, messagebox, ttk

    if "tk" in globals():
        return

    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk


class TableDiffGui:
    GUI_MIN_WIDTH = 780
    GUI_PREFERRED_WIDTH = 900
    GUI_SCREEN_MARGIN_X = 80
    GUI_SCREEN_MARGIN_Y = 120
    GUI_CONTENT_PADDING_Y = 32

    def __init__(self, root: tk.Tk) -> None:
        load_tkinter_gui_modules()
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.file_vars = [tk.StringVar() for _ in range(4)]
        self.marker_var = tk.StringVar(value=DEFAULT_TABLE_MARKER)
        self.output_var = tk.StringVar(value=str(Path.cwd() / "tablediff_report.html"))
        self.open_report_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Bitte 1 bis 4 HTML-Dateien auswählen.")
        self._configure_style()
        self._build()
        self._fit_window_to_content()

    def _configure_style(self) -> None:
        self.root.configure(background=GUI_COLORS["background"])
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        default_font = ("Arial", 10)
        title_font = ("Arial", 16)
        section_font = ("Arial", 11, "bold")

        style.configure(".", font=default_font, background=GUI_COLORS["background"], foreground=GUI_COLORS["text"])
        style.configure("Ui5Page.TFrame", background=GUI_COLORS["background"])
        style.configure("Ui5Panel.TFrame", background=GUI_COLORS["panel"], relief="solid", borderwidth=1)
        style.configure("Ui5PanelHeader.TFrame", background=GUI_COLORS["panel_header"])
        style.configure("Ui5Toolbar.TFrame", background=GUI_COLORS["panel"])
        style.configure("Ui5Label.TLabel", background=GUI_COLORS["panel"], foreground=GUI_COLORS["label"])
        style.configure("Ui5Text.TLabel", background=GUI_COLORS["panel"], foreground=GUI_COLORS["text"])
        style.configure("Ui5Title.TLabel", background=GUI_COLORS["panel"], foreground=GUI_COLORS["text"], font=title_font)
        style.configure(
            "Ui5Section.TLabel",
            background=GUI_COLORS["panel_header"],
            foreground=GUI_COLORS["text"],
            font=section_font,
        )
        style.configure("Ui5Status.TLabel", background=GUI_COLORS["background"], foreground=GUI_COLORS["label"])
        style.configure("Ui5.TEntry", fieldbackground="#ffffff", foreground=GUI_COLORS["text"], padding=5)
        style.configure(
            "Ui5.TButton",
            background="#ffffff",
            foreground=GUI_COLORS["link"],
            bordercolor=GUI_COLORS["link"],
            lightcolor="#ffffff",
            darkcolor="#ffffff",
            padding=(10, 6),
        )
        style.map("Ui5.TButton", background=[("active", GUI_COLORS["button_hover"])])
        style.configure(
            "Ui5Primary.TButton",
            background=GUI_COLORS["link"],
            foreground="#ffffff",
            bordercolor=GUI_COLORS["link"],
            lightcolor=GUI_COLORS["link"],
            darkcolor=GUI_COLORS["link"],
            padding=(14, 7),
        )
        style.map("Ui5Primary.TButton", background=[("active", "#0854a0")], foreground=[("active", "#ffffff")])
        style.configure("Ui5.TCheckbutton", background=GUI_COLORS["panel"], foreground=GUI_COLORS["text"])

    def _build(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        shellbar = tk.Frame(self.root, background=GUI_COLORS["shell"], height=48)
        shellbar.grid(row=0, column=0, sticky="ew")
        shellbar.grid_propagate(False)
        shellbar.columnconfigure(1, weight=1)
        tk.Label(
            shellbar,
            text=APP_NAME,
            background=GUI_COLORS["shell"],
            foreground=GUI_COLORS["shell_text"],
            font=("Arial", 11, "bold"),
            padx=20,
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            shellbar,
            text="Codeplug Vergleich",
            background=GUI_COLORS["shell"],
            foreground="#d3dce6",
            font=("Arial", 10),
        ).grid(row=0, column=1, sticky="w")

        page = ttk.Frame(self.root, padding=16, style="Ui5Page.TFrame")
        page.grid(row=1, column=0, sticky="nsew")
        page.columnconfigure(0, weight=1)
        page.rowconfigure(1, weight=1)

        header = ttk.Frame(page, padding=(18, 14), style="Ui5Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Codeplug Vergleich", style="Ui5Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="HTML-Dateien auswählen und einen UI5-ähnlichen Vergleichsreport erzeugen.",
            style="Ui5Label.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        panel = ttk.Frame(page, style="Ui5Panel.TFrame")
        panel.grid(row=1, column=0, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        panel_header = ttk.Frame(panel, padding=(14, 10), style="Ui5PanelHeader.TFrame")
        panel_header.grid(row=0, column=0, sticky="ew")
        ttk.Label(panel_header, text="Vergleichsparameter", style="Ui5Section.TLabel").grid(row=0, column=0, sticky="w")

        frame = ttk.Frame(panel, padding=14, style="Ui5Toolbar.TFrame")
        frame.grid(row=1, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="HTML-Dateien", style="Ui5Text.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")
        for index, file_var in enumerate(self.file_vars, start=1):
            row = index
            ttk.Label(frame, text=f"Datei {index}", style="Ui5Label.TLabel").grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(frame, textvariable=file_var, style="Ui5.TEntry").grid(
                row=row, column=1, sticky="ew", padx=10, pady=4
            )
            ttk.Button(
                frame,
                text="Auswählen",
                style="Ui5.TButton",
                command=lambda i=index - 1: self._select_input(i),
            ).grid(
                row=row, column=2, sticky="ew", pady=3
            )

        marker_row = 5
        ttk.Label(frame, text="Tabellen-Suchbegriff", style="Ui5Label.TLabel").grid(
            row=marker_row, column=0, sticky="w", pady=(14, 4)
        )
        ttk.Entry(frame, textvariable=self.marker_var, style="Ui5.TEntry").grid(
            row=marker_row, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=(14, 4)
        )

        output_row = 6
        ttk.Label(frame, text="Ausgabedatei", style="Ui5Label.TLabel").grid(row=output_row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.output_var, style="Ui5.TEntry").grid(
            row=output_row, column=1, sticky="ew", padx=10, pady=4
        )
        ttk.Button(frame, text="Speichern unter", style="Ui5.TButton", command=self._select_output).grid(
            row=output_row, column=2, sticky="ew", pady=4
        )

        ttk.Checkbutton(
            frame,
            text="Report nach dem Erzeugen öffnen",
            variable=self.open_report_var,
            style="Ui5.TCheckbutton",
        ).grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 4))

        action_frame = ttk.Frame(frame, style="Ui5Toolbar.TFrame")
        action_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(14, 4))
        action_frame.columnconfigure(0, weight=1)
        ttk.Button(action_frame, text="Vergleich starten", style="Ui5Primary.TButton", command=self._run_compare).grid(
            row=0, column=1
        )
        ttk.Button(action_frame, text="Beenden", style="Ui5.TButton", command=self.root.destroy).grid(
            row=0, column=2, padx=(8, 0)
        )

        ttk.Label(page, textvariable=self.status_var, style="Ui5Status.TLabel").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )

    def _fit_window_to_content(self) -> None:
        self.root.update_idletasks()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        max_width = max(self.GUI_MIN_WIDTH, screen_width - self.GUI_SCREEN_MARGIN_X)
        max_height = max(480, screen_height - self.GUI_SCREEN_MARGIN_Y)

        requested_width = self.root.winfo_reqwidth()
        requested_height = self.root.winfo_reqheight() + self.GUI_CONTENT_PADDING_Y
        window_width = min(max(self.GUI_PREFERRED_WIDTH, requested_width), max_width)
        window_height = min(requested_height, max_height)

        min_width = min(self.GUI_MIN_WIDTH, window_width)
        min_height = min(requested_height, window_height)
        self.root.minsize(min_width, min_height)

        position_x = max(0, (screen_width - window_width) // 2)
        position_y = max(0, (screen_height - window_height) // 3)
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    def _select_input(self, index: int) -> None:
        filename = filedialog.askopenfilename(
            title="HTML-Datei auswählen",
            filetypes=[("HTML-Dateien", "*.html *.htm"), ("Alle Dateien", "*.*")],
        )
        if filename:
            self.file_vars[index].set(filename)
            if index == 0:
                self.output_var.set(str(Path(filename).with_name("tablediff_report.html")))

    def _select_output(self) -> None:
        filename = filedialog.asksaveasfilename(
            title="Vergleichsreport speichern",
            defaultextension=".html",
            initialfile=Path(self.output_var.get()).name,
            filetypes=[("HTML-Dateien", "*.html"), ("Alle Dateien", "*.*")],
        )
        if filename:
            self.output_var.set(filename)

    def _run_compare(self) -> None:
        input_files = [Path(file_var.get()) for file_var in self.file_vars if file_var.get().strip()]
        table_marker = self.marker_var.get()
        output_file = Path(self.output_var.get())

        if not 1 <= len(input_files) <= 4:
            messagebox.showerror("Fehler", "Bitte 1 bis 4 HTML-Dateien auswählen.")
            return

        if not table_marker:
            messagebox.showerror("Fehler", "Der Tabellen-Suchbegriff darf nicht leer sein.")
            return

        missing_files = [path for path in input_files if not path.is_file()]
        if missing_files:
            messagebox.showerror("Fehler", "Datei nicht gefunden:\n" + "\n".join(str(path) for path in missing_files))
            return

        try:
            self.status_var.set("Vergleich wird erzeugt ...")
            self.root.update_idletasks()
            output_file.parent.mkdir(parents=True, exist_ok=True)
            build_report(input_files, output_file, table_marker)
        except Exception as error:
            self.status_var.set("Fehler beim Erzeugen des Reports.")
            messagebox.showerror("Fehler", str(error))
            return

        self.status_var.set(f"Report geschrieben: {output_file}")
        if self.open_report_var.get():
            opened = webbrowser.open(output_file.resolve().as_uri())
            if not opened:
                messagebox.showinfo("Report erzeugt", f"Report wurde erzeugt:\n{output_file}")


def run_gui() -> int:
    load_tkinter_gui_modules()
    root = tk.Tk()
    TableDiffGui(root)
    root.mainloop()
    return 0
