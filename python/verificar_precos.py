import pandas as pd
import re

def limpar_numero(valor):
    if pd.isna(valor):
        return 0.0
    v = str(valor).strip()
    v = re.sub(r"[^0-9,.-]", "", v)
    if v == "" or v in ["-", ",", ".", ",-", ".-"]:
        return 0
    if "." in v and "," in v:
        v = v.replace(".", "").replace(",", ".")
        return float(v)
    if "," in v:
        return float(v.replace(",", "."))
    return float(v)

df = pd.read_excel("excel/PEDIDOS ONDA.xlsx")
df.columns = df.columns.str.upper()

df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df = df[df["DATA"].notna()]

df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar_numero)
df["KG"] = df["KG"].apply(limpar_numero)
df["TOTAL M2"] = df["TOTAL M2"].apply(limpar_numero)

data_ref = df["DATA"].max()
ano = data_ref.year
mes = data_ref.month

df_mes = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]

total_valor = df_mes["VALOR COM IPI"].sum()
total_kg = df_mes["KG"].sum()
total_m2 = df_mes["TOTAL M2"].sum()

preco_kg = round(total_valor / total_kg, 2) if total_kg > 0 else 0
preco_m2 = round(total_valor / total_m2, 2) if total_m2 > 0 else 0

print("\n============== RESULTADOS REAIS =================")
print("Data referência:", data_ref.strftime("%d/%m/%Y"))
print(f"Total Valor IPI........: {total_valor:,.2f}")
print(f"Total KG...............: {total_kg:,.2f}")
print(f"Total m2...............: {total_m2:,.2f}")
print(f"Preço médio KG.........: R$ {preco_kg}")
print(f"Preço médio m².........: R$ {preco_m2}")
print("=================================================\n")
