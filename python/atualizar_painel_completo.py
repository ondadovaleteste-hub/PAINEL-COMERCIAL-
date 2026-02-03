import pandas as pd
import json
from datetime import datetime
import re

# ======================================================
# CARREGA EXCEL E PADRONIZA COLUNAS
# ======================================================
def carregar_excel():
    df = pd.read_excel("excel/PEDIDOS ONDA.xlsx")

    # padroniza nomes
    df.columns = df.columns.str.upper()

    # validações
    obrig = ["DATA", "VALOR COM IPI", "KG", "TOTAL M2"]
    for c in obrig:
        if c not in df.columns:
            raise Exception(f"❌ Coluna ausente no Excel: {c}")

    # converte datas
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    # limpeza avançada de números
    def limpar(valor):
        if pd.isna(valor):
            return 0
        # remove qualquer coisa que não seja número, vírgula ou ponto
        valor = re.sub(r"[^0-9,.-]", "", str(valor))
        # normaliza pt-BR
        valor = valor.replace(".", "").replace(",", ".")
        try:
            return float(valor)
        except:
            return 0

    df["VALOR COM IPI"] = df["VALOR COM IPI"].apply(limpar)
    df["KG"] = df["KG"].apply(limpar)
    df["TOTAL M2"] = df["TOTAL M2"].apply(limpar)

    return df

# ======================================================
# OBTÉM ÚLTIMA DATA DO EXCEL
# ======================================================
def obter_data_ref(df):
    datas = df["DATA"].dropna()
    if datas.empty:
        raise Exception("❌ Sem datas válidas no Excel.")
    return datas.max()

# ======================================================
# CALCULA KPIs PADRÃO
# ======================================================
def calcular_kpis_padrao(df, data_ref):
    ano = data_ref.year
    mes = data_ref.month

    atual = df[(df["DATA"].dt.year == ano) & (df["DATA"].dt.month == mes)]
    anterior = df[(df["DATA"].dt.year == ano - 1) & (df["DATA"].dt.month == mes)]

    soma_fat = lambda x: x["VALOR COM IPI"].sum()
    soma_kg = lambda x: x["KG"].sum()

    fat_at = soma_fat(atual)
    fat_ant = soma_fat(anterior)

    kg_at = soma_kg(atual)
    kg_ant = soma_kg(anterior)

    qtd_at = len(atual)
    qtd_ant = len(anterior)

    ticket_at = fat_at / qtd_at if qtd_at > 0 else 0
    ticket_ant = fat_ant / qtd_ant if qtd_ant > 0 else 0

    return {
        "faturamento": {
            "atual": fat_at,
            "ano_anterior": fat_ant,
            "variacao": ((fat_at / fat_ant - 1) * 100) if fat_ant > 0 else 0,
            "data_atual": data_ref.strftime("%d/%m/%Y"),
            "data_ano_anterior": data_ref.replace(year=data_ref.year - 1).strftime("%d/%m/%Y")
        },
        "kg": {
            "atual": kg_at,
            "ano_anterior": kg_ant,
            "variacao": ((kg_at / kg_ant - 1) * 100) if kg_ant > 0 else 0
        },
        "qtd": {
            "atual": qtd_at,
            "ano_anterior": qtd_ant,
            "variacao": ((qtd_at / qtd_ant - 1) * 100) if qtd_ant > 0 else 0
        },
        "ticket": {
            "atual": ticket_at,
            "ano_anterior": ticket_ant,
            "variacao": ((ticket_at / ticket_ant - 1) * 100) if ticket_ant > 0 else 0
        }
    }

# ======================================================
# CALCULA PREÇO MÉDIO
# ======================================================
def calcular_preco_medio(df, data_ref):
    df_mes = df[(df["DATA"].dt.month == data_ref.month) & (df["DATA"].dt.year == data_ref.year)]

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

# ======================================================
# SALVA JSON
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ======================================================
# EXECUÇÃO
# ======================================================
if __name__ == "__main__":
    df = carregar_excel()
    data_ref = obter_data_ref(df)

    print("📅 Última data encontrada:", data_ref)

    kpis = calcular_kpis_padrao(df, data_ref)
    preco = calcular_preco_medio(df, data_ref)

    salvar("kpi_faturamento.json", kpis["faturamento"])
    salvar("kpi_kg_total.json", kpis["kg"])
    salvar("kpi_quantidade_pedidos.json", kpis["qtd"])
    salvar("kpi_ticket_medio.json", kpis["ticket"])
    salvar("kpi_preco_medio.json", preco)

    print("✓ Arquivos JSON atualizados com sucesso.")
