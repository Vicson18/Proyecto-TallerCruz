import pyodbc

def conectar():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=(localdb)\\MSSQLLocalDB;'
        'DATABASE=taller;'
        'Trusted_Connection=yes;'
        'Encrypt=no;'
        'TrustServerCertificate=yes;'
    )


def asegurar_esquema():
    """Agrega columnas nuevas a tablas existentes si todavía no existen.
    Se ejecuta una vez al iniciar la app para no depender de scripts de
    migración manuales: Duration (tiempo estándar del trabajo por refacción,
    sin importar cuántas unidades se usen) e IsDeleted (baja lógica, para
    poder quitar una refacción de INVENTARIO sin borrar los servicios que
    ya la usaron)."""
    try:
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Inventory') AND name = 'Duration')
                ALTER TABLE dbo.Inventory ADD Duration NVARCHAR(50) NULL
        """)
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Inventory') AND name = 'IsDeleted')
                ALTER TABLE dbo.Inventory ADD IsDeleted BIT NOT NULL CONSTRAINT DF_Inventory_IsDeleted DEFAULT 0
        """)
        conn.commit(); conn.close()
    except Exception as e:
        print("No se pudo verificar/actualizar el esquema:", e)