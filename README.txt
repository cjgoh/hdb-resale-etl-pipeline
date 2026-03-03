#HDB Resale Flat ETL Pipeline

This repository contains a Python-based ETL pipeline for processing HDB resale flat data (2012–2016).  
The pipeline is implemented in both a Jupyter Notebook (`ETL_Pipeline.ipynb`) and a Python script (`main.py`), with full documentation and reproducible outputs.

##Overview

The ETL pipeline performs the following steps:

1. **Extract**  
   - Load raw CSV files from the `raw_data/` folder.  
   - Ingestion is fully automated — no manual edits required.

2. **Transform**  
   - Data validation (town, flat type, storey range, etc.).  
   - Remaining lease calculation (based on 99-year lease assumption).  
   - Deduplication (keep higher resale price for duplicate records).  
   - Anomaly detection (Z-score heuristic).  
   - Resale identifier generation.  
   - Hashing resale identifiers with SHA-256.

3. **Load**  
   - Export datasets into the `output/` folder:  
     - `raw_master.csv` → Combined raw dataset  
     - `cleaned.csv` → Validated and cleaned dataset  
     - `transformed.csv` → Dataset with resale identifiers  
     - `hashed.csv` → Dataset with hashed identifiers  
     - `failed.csv` → Invalid or duplicate records  
     - `failed_anomalies.csv` → Anomalous records

##Repository Structure

├── raw_data/              # Input CSV files (2012–2016 resale flat data)
├── output/                # Generated datasets (created automatically)
├── ETL_Pipeline.ipynb     # Jupyter Notebook with code + documentation
├── main.py                # Script version of the pipeline (optional)
└── README.md              # Project documentation


---

##Dependencies

The pipeline requires the following Python packages:

- pandas  
- numpy  
- jupyter  
- hashlib (standard library)  
- glob (standard library)  
- logging (standard library)  

Install dependencies with:

```bash
pip install pandas numpy jupyter

