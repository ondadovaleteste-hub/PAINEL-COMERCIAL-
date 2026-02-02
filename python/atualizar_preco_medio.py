import pandas as pd
import json
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"
CAMINHO_JSON_PRECO = "dados/kpi_preco_medio.json"
CAMINHO_JSON_SITE = "site/dados/kpi_preco_medio.json"

def carregar_excel():
    df = pd.read_excel(CAMINHO_EXCEL)

    # Corrigir nomes de colunas (normalizar)
    df.columns = df.columns.str.strip().str.upper()

    # Verificar colunas obrigatórias
    colunas_necessarias = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in colunas_necessarias:
        if c not in df.columns:
            raise Exception(f"❌ Coluna obrigatória não encontrada no Excel: {c}")

    # Converter DATA
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    # Converter numéricos
    df["VALOR COM IPI"] = pd.to_numeric(df["VALOR COM IPI"], errors="coerce").fillna(0)
    df["KG"] = pd.to_numeric(df["KG"], errors="coerce").fillna(0)
    df["TOTAL M2"] = pd.to_numeric(df["TOTAL M2"], errors="coerce").fillna(0)

    return df


def obter_data_referencia(df):
    """Pega a última data disponível na planilha e a usa como data de referência."""
    datas_validas = df["DATA"].dropna()
    if len(datas_validas) == 0:
        raise Exception("❌ Nenhuma data válida encontrada no Excel")

    return datas_validas.max()  # datetime.date


def calcular_preco_medio(df, data_ref):
    """Cálculo do preço médio por KG e preço médio por m²"""
    mes = data_ref.month
    ano = data_ref.year

    # filtrar mês
    df_mes = df[(df["DATA"].dt.month == mes) & (df["DATA"].dt.year == ano)]

    total_valor = df_mes["VALOR COM IPI"].sum()
    total_kg = df_mes["KG"].sum()
    total_m2 = df_mes["TOTAL M2"].sum()

    preco_kg = round(total_valor / total_kg, 2) if total_kg > 0 else 0
    preco_m2 = round(total_valor / total_m2, 2) if total_m2 > 0 else 0

    return {
        "preco_medio_kg": preco_kg,
        "preco_medio_m2": preco_m2,
        "total_kg": total_kg,
        "total_m2": total_m2,
        "data": data_ref.strftime("%d/%m/%Y")
    }


def salvar_json(dados):
    with open(CAMINHO_JSON_PRECO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open(CAMINHO_JSON_SITE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    df = carregar_excel()
    data_ref = obter_data_referencia(df)
    print("📅 Última data encontrada:", data_ref)

    preco = calcular_preco_medio(df, data_ref)

    print("Preço médio gerado:")
    print(json.dumps(preco, indent=2, ensure_ascii=False))

    salvar_json(preco)
