# Script para generar dataset de prueba (opcional)
# Si no tienes el dataset real, puedes generar uno sintético para probar

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("Generando dataset sintético de prueba...")

# Configuración
np.random.seed(42)
n_customers = 500
n_transactions = 5000

# Generar CustomerIDs
customer_ids = np.random.choice(range(10000, 10000 + n_customers), n_transactions)

# Generar fechas
start_date = datetime(2010, 12, 1)
end_date = datetime(2011, 12, 9)
dates = [start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days)) 
         for _ in range(n_transactions)]

# Generar otros campos
invoice_nos = [f"{10000 + i}" for i in range(n_transactions)]
stock_codes = [f"SKU{np.random.randint(1000, 9999)}" for _ in range(n_transactions)]
descriptions = [f"Product {i}" for i in range(n_transactions)]
quantities = np.random.randint(1, 50, n_transactions)
unit_prices = np.round(np.random.uniform(1, 100, n_transactions), 2)
countries = np.random.choice(['United Kingdom', 'France', 'Germany', 'Spain'], 
                             n_transactions, p=[0.8, 0.1, 0.05, 0.05])

# Crear DataFrame
df_synthetic = pd.DataFrame({
    'InvoiceNo': invoice_nos,
    'StockCode': stock_codes,
    'Description': descriptions,
    'Quantity': quantities,
    'UnitPrice': unit_prices,
    'InvoiceDate': dates,
    'CustomerID': customer_ids,
    'Country': countries
})

# Guardar
df_synthetic.to_excel('data/Online_Retail_Test.xlsx', index=False)

print(f"✓ Dataset sintético generado: data/Online_Retail_Test.xlsx")
print(f"  - {n_transactions:,} transacciones")
print(f"  - {n_customers} clientes únicos")
print("\nPuedes usar este archivo para probar el dashboard.")
print("Para producción, descarga el dataset real desde UCI.")
