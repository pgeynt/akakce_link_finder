# DuckDuckGo Search Automation

This Python application automates DuckDuckGo searches using queries from an Excel file. It leverages the [duckduckgo_search](https://pypi.org/project/duckduckgo_search/) library with rotating proxies and a Tkinter-based GUI.

## Features

- **Excel Input:** Reads queries from column "A" or the first column of the selected Excel file.
- **DuckDuckGo Search:** Appends "akakce" to each query and retrieves the first result that matches specific URL patterns.
- **Proxy Support:** Uses rotating proxy settings (update the `PROXIES` dictionary with your credentials).
- **Exponential Backoff:** Gracefully handles rate limit errors with increasing wait times.
- **Logging:** Logs messages in the GUI and writes them to `automation.log`.

## Requirements

- Python 3.x
- Packages: `pandas`, `duckduckgo_search`, `openpyxl`, and built-in `tkinter`

Install required packages with:

```bash
pip install pandas duckduckgo_search openpyxl
