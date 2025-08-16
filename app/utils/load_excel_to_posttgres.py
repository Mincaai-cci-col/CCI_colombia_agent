import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://neondb_owner:npg_2yMelBFq0xcr@ep-round-sunset-adbyuw53-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

# Load Excel
df = pd.read_excel("app/utils/data/contact.xlsx")

# Rename columns
df = df.rename(columns={
    "Empresa": "empresa",
    "Nombre": "nombre",
    "Apellido": "apellido",
    "Celular": "celular",
    "Cargo": "cargo",
    "Sector de Actividad": "sector",
    "Descripción": "descripcion"
})

# Clean 'celular' column
df['celular'] = (
    df['celular']
    .astype(str)
    .str.strip()
    .str.replace(r"\s+", "", regex=True)
)

# Replace the table if it exists
df.to_sql("whatsapp_numbers", engine, if_exists="replace", index=False)
