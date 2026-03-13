import pyodbc

def conectar():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  
        'DATABASE=taller;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )