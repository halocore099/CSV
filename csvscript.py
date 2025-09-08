import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

# --- Encoding detection ---
def detect_encoding(file_path):
    encodings_to_try = ['utf-8', 'latin-1', 'windows-1252', 'cp1252', 'iso-8859-1']

    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1024)  # Read first 1KB to test encoding
            return encoding
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Could not decode file {file_path} with any of the attempted encodings: {encodings_to_try}")

# --- Delimiter detection ---
def detect_delimiter(file_path, default=','):
    possible_delimiters = [',', ';', '|', '\t']
    encoding = detect_encoding(file_path)

    with open(file_path, 'r', encoding=encoding) as f:
        first_line = f.readline()

    counts = {d: first_line.count(d) for d in possible_delimiters}
    detected = max(counts, key=counts.get)
    return detected if counts[detected] > 0 else default

# --- CSV Merge Function ---
def merge_csvs(total_path, apple_path, manual_delimiter=None):
    # Detect encodings for both files
    encoding_total = detect_encoding(total_path)
    encoding_apple = detect_encoding(apple_path)

    delim_total = manual_delimiter if manual_delimiter else detect_delimiter(total_path)
    delim_apple = manual_delimiter if manual_delimiter else detect_delimiter(apple_path)

    total_df = pd.read_csv(total_path, delimiter=delim_total, encoding=encoding_total)
    apple_df = pd.read_csv(apple_path, delimiter=delim_apple, encoding=encoding_apple)

    total_df['Brand Type'] = "Non-Apple"
    apple_df['Brand Type'] = "Apple"

    merged = pd.concat([total_df, apple_df], ignore_index=True)
    merged.to_csv("merged_output.csv", sep=delim_total, index=False)
    return "merged_output.csv"

# --- GUI ---
def browse_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def run_merge():
    total_path = entry_total.get()
    apple_path = entry_apple.get()
    manual_delimiter = delimiter_var.get().strip() or None

    if not total_path or not apple_path:
        messagebox.showerror("Error", "Please select both CSV files.")
        return

    try:
        status_label.config(text="Merging CSVs...", foreground="blue")
        root.update_idletasks()
        output_file = merge_csvs(total_path, apple_path, manual_delimiter)
        status_label.config(text=f"Merge complete! Saved to: {output_file}", foreground="green")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- Main Window ---
root = tk.Tk()
root.title("CSV Merger")
root.geometry("600x250")
root.resizable(True, True)

# Center the window
root.eval('tk::PlaceWindow . center')

# --- Styles ---
style = ttk.Style(root)
style.theme_use("clam")

frame = ttk.Frame(root, padding=15)
frame.pack(fill=tk.BOTH, expand=True)

# File selection rows
ttk.Label(frame, text="Total CSV:").grid(row=0, column=0, sticky="w", pady=5)
entry_total = ttk.Entry(frame, width=40)
entry_total.grid(row=0, column=1, pady=5)
ttk.Button(frame, text="Browse", command=lambda: browse_file(entry_total)).grid(row=0, column=2, padx=5)

ttk.Label(frame, text="Apple CSV:").grid(row=1, column=0, sticky="w", pady=5)
entry_apple = ttk.Entry(frame, width=40)
entry_apple.grid(row=1, column=1, pady=5)
ttk.Button(frame, text="Browse", command=lambda: browse_file(entry_apple)).grid(row=1, column=2, padx=5)

# Delimiter
ttk.Label(frame, text="Delimiter (leave blank for auto-detect):").grid(row=2, column=0, columnspan=3, sticky="w", pady=(15, 5))
delimiter_var = tk.StringVar()
ttk.Entry(frame, textvariable=delimiter_var, width=10).grid(row=3, column=0, sticky="w")

# Run button
ttk.Button(frame, text="Merge CSVs", command=run_merge).grid(row=4, column=0, columnspan=3, pady=20)

# Status label
status_label = ttk.Label(frame, text="", foreground="blue")
status_label.grid(row=5, column=0, columnspan=3)

root.mainloop()
