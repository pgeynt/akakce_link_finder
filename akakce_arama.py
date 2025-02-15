import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import time
import random
import logging
import sys
from duckduckgo_search import DDGS  # Using DDGS class for the new API

# Webshare.io rotating proxy credentials (example; use your own credentials)
PROXIES = {
    "http": "TYPE YOUR PROXY HERE",
    "https": "TYPE YOUR PROXY HERE"
}

# Logger settings: Logs are written to both file and terminal
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')

file_handler = logging.FileHandler('automation.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def log_message(message):
    """
    Writes message to GUI log screen, file, and terminal
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - {message}\n"
    log_text.insert(tk.END, log_entry)
    log_text.see(tk.END)
    root.update_idletasks()
    logger.info(message)

def search_duckduckgo(query):
    """
    Performs DuckDuckGo search using DDGS class.
    Returns the first link from search results that starts with "www.akakce.com" or "http://www.akakce.com".
    Applies exponential backoff if rate limit error occurs.
    """
    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        try:
            # Add proxy settings to DDGS constructor; "backend" parameter removed
            with DDGS(proxies=PROXIES) as ddgs:
                results = ddgs.text(query, max_results=10)
            if results:
                for result in results:
                    url = result.get("href", "")
                    log_message(f"URL found for query: {url}")
                    if url.startswith("https://www.akakce.com") or url.startswith("http://www.akakce.com"):
                        return url
            return ""
        except Exception as e:
            error_message = str(e)
            if "Ratelimit" in error_message:
                wait_time = 30 * (attempts + 1)
                log_message(f"Ratelimit error: {e}. Waiting {wait_time} seconds on attempt {attempts+1}...")
                time.sleep(wait_time)
            else:
                log_message(f"Error occurred: {e}")
                break
            attempts += 1
    return ""

def process_excel():
    log_message("Starting Excel file selection process.")
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )
    if not file_path:
        log_message("No file selected, operation cancelled.")
        return

    log_message(f"Selected file: {file_path}")
    try:
        log_message("Reading Excel file...")
        df = pd.read_excel(file_path)
        # If column "A" exists use it, otherwise use the first column
        if "A" in df.columns:
            queries = df["A"].dropna().tolist()
            log_message("Found column 'A' in Excel file, retrieving data.")
        else:
            queries = df.iloc[:, 0].dropna().tolist()
            log_message("Column 'A' not found in Excel file, using first column.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not read Excel file:\n{e}")
        log_message(f"Could not read Excel file: {e}")
        return

    results = []
    total_queries = len(queries)
    log_message(f"Found {total_queries} queries, starting search process.")

    for idx, query in enumerate(queries, start=1):
        log_message(f"[{idx}/{total_queries}] Processing query: {query}")
        # Search query: Excel data + " akakce"
        search_query = f"{query} akakce"
        found_link = search_duckduckgo(search_query)
        if not found_link:
            log_message(f"No suitable link found for query: {query}")
        results.append({"Search": query, "Link": found_link})
        time.sleep(random.uniform(2, 4))
    
    log_message("Search process completed, preparing results.")
    output_df = pd.DataFrame(results)
    save_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx *.xls")],
        title="Save Results"
    )
    if not save_path:
        log_message("Save operation cancelled.")
        return
    try:
        output_df.to_excel(save_path, index=False)
        messagebox.showinfo("Success", "Process completed. Results saved.")
        log_message(f"Results successfully saved to: {save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save results:\n{e}")
        log_message(f"Could not save results: {e}")

# GUI Setup
root = tk.Tk()
root.title("DuckDuckGo Search Automation (DDGS with Rotating Proxy)")

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack()

btn = tk.Button(main_frame, text="Load and Process Excel File", command=process_excel, width=30, height=2)
btn.pack(pady=(0, 10))

log_frame = tk.Frame(root)
log_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(log_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

log_text = tk.Text(log_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15)
log_text.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=log_text.yview)

root.mainloop()
