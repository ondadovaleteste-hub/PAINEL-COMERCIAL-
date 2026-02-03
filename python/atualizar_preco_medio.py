import pandas as pd
import json
from datetime import datetime
import re

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"
CAMINHO_JSON_PRECO = "dados/kpi_preco_medio.json"
CAMINHO_JSON_SITE = "site/dados/kpi_preco_medio.json"

def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper()

    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Falta coluna: {c}")

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    def limpar(v):
        if pd.isna(v):
            return 0
        v = re.sub(r"[^0-9,.-]", "", str(v))
        v = v.replace(".", "").replace(",", ".")
        try:
            return float(v)
        except:
            return 0

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar)
    df["KG"] = df["KG"].apply(limpar)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar)

    return df

def obter_data_ref(df):
    datas = df["DATA"].dropna()
    return datas.max()

def calcular_preco_medio(df, data_ref):
    mes = data_ref.month
    ano = data_ref.year

    df_mes = df[(df["DATA"].dt.month == mes) & (df["DATA"].dt.year == ano)]

    total_valor = df_mes["VALOR COM IPI"].sum()
    total_kg = df_mes["KG"].sum()
    total_m2 = df_mes["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg > 0 else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 > 0 else 0

    return {
        "preco_medio_kg": preco_kg,
        "preco_medio_m2": preco_m2,
        "total_kg": round(total_kg, 2),
        "total_m2": round(total_m2, 2),
        "data": data_ref.strftime("%d/%m/%Y")
    }

def salvar_json(dados):
    with open(CAMINHO_JSON_PRECO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open(CAMINHO_JSON_SITE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    df = carregar_excel()
    data_ref = obter_data_ref(df)
    preco = calcular_preco_medio(df, data_ref)
    print(json.dumps(preco, indent=2, ensure_ascii=False))
    salvar_json(preco)
