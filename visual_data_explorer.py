import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt


class VisualDataExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visual Data Explorer")
        self.geometry("1100x650")

        self.df = None
        self.filtered_df = None

        self._build_ui()

    def _build_ui(self):
       
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="Seçili dosya:").pack(side=tk.LEFT)
        self.file_label = ttk.Label(top_frame, text="(Henüz dosya seçilmedi)")
        self.file_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(top_frame, text="CSV Yükle", command=self.load_csv).pack(side=tk.RIGHT)

        
        middle_frame = ttk.Frame(self, padding=5)
        middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

       
        table_frame = ttk.LabelFrame(middle_frame, text="Veri Önizleme")
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        
        right_panel = ttk.Frame(middle_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

       
        filter_frame = ttk.LabelFrame(right_panel, text="Filtreleme", padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(filter_frame, text="Sütun:").grid(row=0, column=0, sticky="w")
        self.filter_column_cb = ttk.Combobox(filter_frame, state="readonly")
        self.filter_column_cb.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(filter_frame, text="İçerir:").grid(row=1, column=0, sticky="w")
        self.filter_value_entry = ttk.Entry(filter_frame)
        self.filter_value_entry.grid(row=1, column=1, sticky="ew", padx=5)

        filter_frame.columnconfigure(1, weight=1)

        ttk.Button(
            filter_frame,
            text="Filtreyi Uygula",
            command=self.apply_filter
        ).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        ttk.Button(
            filter_frame,
            text="Filtreyi Temizle",
            command=self.clear_filter
        ).grid(row=3, column=0, columnspan=2, sticky="ew")

        
        plot_frame = ttk.LabelFrame(right_panel, text="Grafik", padding=5)
        plot_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(plot_frame, text="Sayısal sütun:").grid(row=0, column=0, sticky="w")
        self.plot_column_cb = ttk.Combobox(plot_frame, state="readonly")
        self.plot_column_cb.grid(row=0, column=1, sticky="ew", padx=5)
        plot_frame.columnconfigure(1, weight=1)

        ttk.Button(
            plot_frame,
            text="Çiz (Index - Değer)",
            command=self.plot_line
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 2))

        ttk.Button(
            plot_frame,
            text="Histogram",
            command=self.plot_hist
        ).grid(row=2, column=0, columnspan=2, sticky="ew")

        
        stats_frame = ttk.LabelFrame(right_panel, text="Özet İstatistik", padding=5)
        stats_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Button(
            stats_frame,
            text="Özet İstatistik Göster",
            command=self.show_stats
        ).pack(fill=tk.X)

        self.stats_text = tk.Text(stats_frame, height=15, wrap="none")
        self.stats_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Alt bilgi
        bottom_frame = ttk.Frame(self, padding=5)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(
            bottom_frame,
            text="Visual Data Explorer – CSV yükle, filtrele, özet istatistik al, grafik çiz."
        ).pack(side=tk.LEFT)

    
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="CSV dosyası seç",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not file_path:
            return

        try:
            self.df = pd.read_csv(file_path)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okunurken hata oluştu:\n{e}")
            return

        self.filtered_df = self.df.copy()
        self.file_label.config(text=file_path)

        self.update_column_choices()
        self.show_dataframe()
        self.stats_text.delete("1.0", tk.END)

    def update_column_choices(self):
        if self.df is None:
            return

        cols = list(self.df.columns)
        self.filter_column_cb["values"] = cols
        if cols:
            self.filter_column_cb.current(0)

        numeric_cols = list(self.df.select_dtypes(include="number").columns)
        self.plot_column_cb["values"] = numeric_cols
        if numeric_cols:
            self.plot_column_cb.current(0)
        else:
            self.plot_column_cb.set("")


    def show_dataframe(self):
        df_to_show = self.filtered_df if self.filtered_df is not None else self.df
        if df_to_show is None:
            return

        
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df_to_show.columns)

        for col in df_to_show.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="w")

        max_rows = 500
        for _, row in df_to_show.head(max_rows).iterrows():
            values = [str(v) for v in row.values]
            self.tree.insert("", tk.END, values=values)

   
    def apply_filter(self):
        if self.df is None:
            messagebox.showwarning("Uyarı", "Önce bir CSV dosyası yükleyin.")
            return

        col = self.filter_column_cb.get()
        val = self.filter_value_entry.get()

        if not col or not val:
            messagebox.showinfo("Bilgi", "Filtre için sütun ve değer girin.")
            return

        try:
            mask = self.df[col].astype(str).str.contains(val, case=False, na=False)
            self.filtered_df = self.df[mask].copy()
            self.show_dataframe()
        except Exception as e:
            messagebox.showerror("Hata", f"Filtre uygulanırken hata oluştu:\n{e}")

    def clear_filter(self):
        if self.df is None:
            return
        self.filtered_df = self.df.copy()
        self.filter_value_entry.delete(0, tk.END)
        self.show_dataframe()


    def _get_current_numeric_series(self):
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showwarning("Uyarı", "Veri bulunamadı.")
            return None

        col = self.plot_column_cb.get()
        if not col:
            messagebox.showinfo("Bilgi", "Önce sayısal bir sütun seçin.")
            return None

        if col not in self.filtered_df.columns:
            messagebox.showerror("Hata", "Seçili sütun geçerli değil.")
            return None

        try:
            series = pd.to_numeric(self.filtered_df[col], errors="coerce").dropna()
        except Exception as e:
            messagebox.showerror("Hata", f"Sütun sayısal değerlere dönüştürülemedi:\n{e}")
            return None

        if series.empty:
            messagebox.showinfo("Bilgi", "Bu sütunda kullanılabilir sayısal veri yok.")
            return None

        return series


    def plot_line(self):
        series = self._get_current_numeric_series()
        if series is None:
            return

        plt.figure()
        plt.plot(series.index, series.values)
        plt.xlabel("Index")
        plt.ylabel(self.plot_column_cb.get())
        plt.title("Çizgi Grafik")
        plt.tight_layout()
        plt.show()

    def plot_hist(self):
        series = self._get_current_numeric_series()
        if series is None:
            return

        plt.figure()
        plt.hist(series.values, bins=20)
        plt.xlabel(self.plot_column_cb.get())
        plt.ylabel("Frekans")
        plt.title("Histogram")
        plt.tight_layout()
        plt.show()

    
    def show_stats(self):
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showwarning("Uyarı", "Özet istatistik için veri bulunamadı.")
            return

        desc = self.filtered_df.describe(include="all").transpose()
        with pd.option_context("display.max_cols", None, "display.width", 1000):
            text = desc.to_string()

        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, text)


if __name__ == "__main__":
    app = VisualDataExplorer()
    app.mainloop()
