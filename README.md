# Germany's Climate Responsibility Analyzer
A python based tool to load German greenhouse gas emissions data and global emission and population data, compute global carbon debt and budget using the fair share by global population method and produce figures and tables.

# Overview
This repository contains the datasets, source code, and documentation required to perform the historical carbon debt and future budget analysis for Germany. The project is organized into modular components separating the core computational logic, raw data, and narrative analysis.

### Directory Structure
```text
.
├── .vscode/          # Editor settings for automatic formatting
├── bin/              # Core Python modules and the main execution notebook
│   ├── Computational_Narrative.ipynb  # Main narrative analysis and execution file
│   ├── carbonbudget.py                # Logic for carbon fair-share budget and debt calculations
│   ├── futureanalysis.py              # BAU and Net-Zero pathway analysis
│   ├── maps.py                        # Geospatial visualization for global carbon debt
│   └── plotsectortable.py             # Sectoral emission trends analysis and plotting
├── data/             # Raw datasets required for the analysis
│   ├── 85111-0005_en_flat.csv         # Destatis: Germany GHG emissions by sector
│   ├── EDGAR_2025_GHG.csv             # EDGAR: Global historical GHG emissions
│   └── WPP2024_GEN_F01...csv          # UN DESA: Global population estimates and projections
├── docs/             # Additional project documentation
│   └── description.txt                # Detailed summary of the analytical methodology
├── .flake8           # Configuration for the Flake8 linter
└── requirements.txt  # List of Python dependencies
```

# Usage Guide
Install dependencies with: 
```pip install -r requirements.txt```

For Full Anaysis, run `bin/Computational_Narrative.ipynb` with a program supporting Jupyter notebooks.

# Coding Style
For checking the coding style, [flake8](https://flake8.pycqa.org/en/latest/index.html) is used as linter. Line length checking is ignored intentionally in `.flake8`. 

For trimming trailing white space and ensuring tabs insert 4 spaces automatically by `.vscode/settings.json`

# Contact Information
wonjin.kim@uni-potsdam.de
