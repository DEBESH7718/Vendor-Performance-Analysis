import pandas as pd
import numpy as np
import time
import logging
from sqlalchemy import create_engine
from ingestion_db import ingest_db

logging.basicConfig(
    filename = "logs/get_vendor_summary.log",
    level = logging.DEBUG,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    filemode = 'a'
)

def create_vendor_summary(engine):
    '''this function will merge the different tables to get the overall vendor summary and adding new columns in the resultant data'''
    vendor_sales_summary = pd.read_sql_query("""WITH FreightSummary as(
select VendorNumber, SUM(Freight) as FreightCost
from vendor_invoice
Group BY VendorNumber
),
PurchaseSummary as(
select
p.VendorNumber,
p.VendorName,
p.Brand,
p.Description,
p.PurchasePrice,
pp.Volume,
pp.Price as ActualPrice,
SUM(p.Quantity) as TotalPurchaseQuantity,
SUM(p.Dollars) as TotalPurchaseDollars
From purchases p
Join purchase_prices pp
ON p.Brand = pp.Brand
where p.PurchasePrice > 0
Group BY 
p.VendorNumber,
p.VendorName,
p.Brand,
p.Description,
p.PurchasePrice,
pp.Volume,
pp.Price
),
SalesSummary as(
select
VendorNo,
Brand,
SUM(SalesDollars) as TotalSalesDollars,
SUM(SalesPrice) as TotalSalesPrice,
SUM(SalesQuantity) as TotalSalesQuantity,
SUM(ExciseTax) as TotalExciseTax
from sales
Group BY VendorNo, Brand
)

select
ps.VendorNumber,
ps.VendorName,
ps.Brand,
ps.Description,
ps.ActualPrice,
ps.Volume,
ps.TotalPurchaseQuantity,
ps.TotalPurchaseDollars,
ss.TotalSalesQuantity,
ss.TotalSalesDollars,
ss.TotalSalesPrice,
ss.TotalExciseTax,
fs.FreightCost
from PurchaseSummary ps
left join SalesSummary ss
on ps.VendorNumber = ss.VendorNo
and ps.Brand = ss.Brand
left join FreightSummary fs
on ps.VendorNumber = fs.VendorNumber
order by ps.TotalPurchaseDollars desc
""", engine)
    return vendor_sales_summary

def clean_data(df):
    '''this function will clean the data'''
    # changing datatype to float 
    df['Volume'] = df['Volume'].astype('float64')

    #filling missing value with 0
    df.fillna(0, inplace = True)

    # removing spaces fro categorical columns
    df['VendorName'] = df['VendorName'].str.strip()
    df['Description'] = df['Description'].str.strip()

    # creating new columns for better analysis
    df['GrossProfit'] = df['TotalSalesDollars'] - df['TotalPurchaseDollars']

    df['ProfitMargin'] = np.where(
        df['TotalSalesDollars'] != 0,
        (df['GrossProfit'] / df['TotalSalesDollars']) * 100,
        0
    )
    
    df['StockTurnover'] = np.where(
        df['TotalPurchaseQuantity'] != 0,
        df['TotalSalesQuantity'] / df['TotalPurchaseQuantity'],
        0
    )
    
    df['SalestoPurchaseRatio'] = np.where(
        df['TotalPurchaseDollars'] != 0,
        df['TotalSalesDollars'] / df['TotalPurchaseDollars'],
        0
    )

    return df

if __name__ == '__main__':
    try:
        logging.info("Creating MySQL engine...")
        # creating database connetion
        engine = create_engine(
        "mysql+mysqlconnector://root:091005@127.0.0.1:3306/vendor_performance_analysis",
        pool_pre_ping=True,
        )

        logging.info("Creating vendor summary...")
         # Create the summary dataframe
        summary_df = create_vendor_summary(engine)

        logging.info(f"Vendor summary created with {summary_df.shape[0]} rows.")

        logging.info("Cleaning data...")
        # Clean and create new columns
        clean_df = clean_data(summary_df)
        logging.info(f"DataFrame Shape: {clean_df.shape}")

        if np.isinf(clean_df.select_dtypes(include=np.number)).any().any():
            logging.error("DataFrame contains infinite values.")
            raise ValueError("DataFrame contains infinite values.")

        logging.info("Loading vendor summary into MySQL...")

        start = time.time()
        
        ingest_db(clean_df, "vendor_sales_summary", engine)
        
        end = time.time()
        
        logging.info(f"Upload completed in {end-start:.2f} seconds")

        logging.info("Vendor summary table created successfully.")
        print("Vendor summary table created successfully.")

    except Exception as e:
        logging.exception("Error while creating vendor summary.")
        print(e)

    finally:
        engine.dispose()