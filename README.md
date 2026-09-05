Designed to address real-world retail operation bottlenecks, this end-to-end data pipeline automates the ingestion of raw transactional data, engineers critical business KPIs, and provides actionable insights. By pre-aggregating distributed data, it eliminates redundant database computations and powers an optimized visualization layer.

**Project Overview**
1. Automated Ingestion: Batch-loads raw inventory, sales, and invoice datasets into a relational database.

2. Profitability Tracking: Calculates Total Sales, Purchase Dollars, Gross Profit, and Profit Margins per vendor.

3. Inventory Efficiency: Computes Stock Turnover rates to identify fast-moving versus stagnant product lines.

4. Cost Analysis: Integrates freight costs and excise taxes into the final vendor performance summary.

**Pipeline Architecture**
1. Data Loading (ingestion_db.py): Utilizes Python and SQLAlchemy to parse local CSV files and populate the MySQL database.

2. ETL Processing (get_vendor_summary.py): Executes advanced SQL CTEs to aggregate distributed metrics and writes a clean, combined dataset back to the database.

3. Statistical Analysis (Jupyter Notebooks): Uses SciPy and Matplotlib for data profiling, distribution plotting, and hypothesis testing.

4. Dashboarding (.pbix): A Power BI visualization layer built directly on the pre-aggregated summary table for immediate reporting.

**Tech Stack**
1. Languages: Python, SQL

2. Libraries: Pandas, NumPy, SQLAlchemy, Matplotlib, Seaborn

3. Database: MySQL

4. Business Intelligence: Power BI

**Local Setup Instructions**
1. Clone the repository and ensure your raw datasets are placed in a folder named data/ in the root directory.

2. Update the MySQL database credentials (root:your_password@127.0.0.1:3306/vendor_performance_analysis) inside both Python scripts.

3. Run python ingestion_db.py to build the foundational database tables from your raw files.

4. Execute python get_vendor_summary.py to run the ETL process, calculate KPIs, and generate the final analytical table for Power BI.
