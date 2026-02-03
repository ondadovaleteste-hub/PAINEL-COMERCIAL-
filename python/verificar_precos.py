import pandas as pd
import re
from datetime import datetime

CAMINHO = "excel/PEDIDOS ONDA.xlsx"

def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0
    v = str(valor).strip()
    v = re.sub(r"[^0-9,.-]", "", v)
    if v in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0
    if "." in v and "," in v:
        return float(v.replace(".", "").replace(",", "."))
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)

df = pd.read_excel(CAMINHO)
df.columns = df.columns.str.upper().str.strip()

df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df = df[df["DATA"].notna()]

df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
df["KG"] = df["KG"].apply(limpar_numero)
df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

ultima = df["DATA"].max()
ano = ultima.year
mes = ultima.month
df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
primeira = df_mes["DATA"].min()

df_periodo = df[(df["DATA"] >= primeira) & (df["DATA"] <= ultima)]

total_valor = df_periodo["VALOR COM IPI"].sum()
total_kg = df_periodo["KG"].sum()
total_m2 = df_periodo["TOTAL M2"].sum()
qtd = len(df_periodo)

preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

print("\n================ RESULTADOS VERDADEIROS ================")
print("Período:", primeira.strftime("%d/%m/%Y"), "→", ultima.strftime("%d/%m/%Y"))
print(f"Total Valor IPI: {total_valor:,.2f}")
print(f"Total KG......: {total_kg:,.2f}")
print(f"Total m2......: {total_m2:,.2f}")
print(f"Qtd Pedidos...: {qtd}")
print(f"Preço Médio KG: R$ {preco_kg}")
print(f"Preço Médio m2: R$ {preco_m2}")
print("=========================================================\n")
