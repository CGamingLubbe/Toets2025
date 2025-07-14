To run this program on another computer, you need the following requirements:

### 1. **Python Installation**
- Install Python 3.7 or newer (recommended: Python 3.8+).

### 2. **Required Python Packages**
Install these packages using pip:
```
pip install requests pandas openpyxl streamlit googlesearch-python
```
- `requests`
- `pandas`
- `openpyxl`
- `streamlit`
- `googlesearch-python` (sometimes called `googlesearch`)

### 3. **Other Requirements**
- **Internet access** (for web scraping and Google search).
- **Excel** (optional, for opening `.xlsx` files, but not required for saving).
- **Windows OS** (for `os.startfile` to open Excel results).

### 4. **How to Run**
- Save your script as web_scraper_app.py.
- Open a terminal in the script's folder.
- Run with Streamlit:
```
streamlit run web_scraper_app.py
```

### 5. **Permissions**
- Ensure you have write permissions in the folder to save `companies.xlsx`.

---

**Note:**  
If you get errors about missing packages, install them with pip as shown above.  
If you use a different OS, replace `os.startfile` with an appropriate command to open files.
