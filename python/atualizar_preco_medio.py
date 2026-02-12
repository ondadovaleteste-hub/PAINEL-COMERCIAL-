import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"
ARQ_JSON_1 = "dados/kpi_preco_medio.json"
ARQ_JSON_2 = "site/dados/kpi_preco_medio.json"

def excel_datetime_para_numero(dt):
    base = datetime(1899, 12, 30)
    return (dt - base).total_seconds() / 86400.0

def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    if isinstance(v, (int, float)):
        return float(v)

    if isinstance(v, (datetime, pd.Timestamp)):
        return float(excel_datetime_para_numero(v.to_pydatetime()))

    s = str(v).strip()

    try:
        dt = pd.to_datetime(s, errors="raise", dayfirst=True)
        if any(ch in s for ch in ["/", "-", ":"]):
            return float(excel_datetime_para_numero(dt.to_pydatetime()))
    except:
        pass

    s = re.sub(r"[^0-9,.\-]", "", s)

    if s in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
        return float(s)

    if "," in s:
        return float(s.replace(",", "."))

    if "." in s:
        partes = s.split(".")
        if len(partes[-1]) == 3:
            s = s.replace(".", "")
        return float(s)

    return float(s)

def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    for col in ["VALOR COM IPI", "KG", "TOTAL M2"]:
        df[col] = df[col].apply(limpar_numero)

    df["PEDIDO_NUM"] = df["PEDIDO"].apply(limpar_numero)

    if "TIPO DE PEDIDO" in df.columns:
        df["TIPO DE PEDIDO"] = df["TIPO DE PEDIDO"].astype(str).str.upper().str.strip()
        df = df[df["TIPO DE PEDIDO"] == "NORMAL"]

    df = df[(df["PEDIDO_NUM"] >= 30000) & (df["PEDIDO_NUM"] <= 50000)]
    df = df.drop_duplicates(subset=["PEDIDO_NUM"])

    return df

def resumo_preco(df, ano, mes, dia):
    inicio = datetime(ano, mes, 1)
    fim = datetime(ano, mes, dia)

    d = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)]

    total_valor = float(d["VALOR COM IPI"].sum())
    total_kg = float(d["KG"].sum())
    total_m2 = float(d["TOTAL M2"].sum())

    preco_kg = round(total_valor / total_kg, 2) if total_kg else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 else 0

    return {
        "preco_medio_kg": preco_kg,
        "preco_medio_m2": preco_m2,
        "total_kg": round(total_kg, 2),
        "total_m2": round(total_m2, 2),
        "data": f"{dia:02d}/{mes:02d}/{ano}"
    }

def salvar_json(dados):
    with open(ARQ_JSON_1, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(ARQ_JSON_2, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    df = carregar()

    ultima = df["DATA"].max()
    ano = ultima.year
    mes = ultima.month
    dia = ultima.day

    dados = {
        "atual": resumo_preco(df, ano, mes, dia),
        "ano_anterior": resumo_preco(df, ano - 1, mes, dia)
    }

    salvar_json(dados)

    print("Preço médio gerado (formato novo):")
    print(json.dumps(dados, ensure_ascii=False, indent=2))
