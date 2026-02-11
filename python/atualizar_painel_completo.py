import pandas as pd
import json
import re
from datetime import datetime

CAMINHO_EXCEL = "excel/PEDIDOS ONDA.xlsx"

# ======================================================
# 🔥 FUNÇÃO DEFINITIVA PARA LER NÚMEROS BRASILEIROS + DATAS CORROMPIDAS
# ======================================================
def limpar_numero(v):
    if pd.isna(v):
        return 0.0

    v_str = str(v).strip()

    # Se vier uma DATA no campo numérico → converter para número real
    # (exemplo: 1900-10-29 01:12:00 → usa dia*mes*hora = valor aproximado)
    try:
        # detectar formatação yyyy-mm-dd hh:mm:ss
        if re.match(r"^\d{4}-\d{2}-\d{2}", v_str):
            dt = pd.to_datetime(v_str, errors="coerce")
            if not pd.isna(dt):
                return round((dt.day * 10) + (dt.hour / 10), 2)
    except:
        pass

    # Limpar caracteres
    v_clean = re.sub(r"[^0-9,.-]", "", v_str)

    if v_clean in ["", "-", ",", ".", ",-", ".-"]:
        return 0.0

    # número tipo 9.999,99 → BR
    if "." in v_clean and "," in v_clean:
        return float(v_clean.replace(".", "").replace(",", "."))

    # número tipo 999,99
    if "," in v_clean:
        return float(v_clean.replace(",", "."))

    # número normal
    return float(v_clean)

# ======================================================
# 🔥 CARREGAR PLANILHA + TRATAR PEDIDOS VÁLIDOS
# ======================================================
def carregar():
    df = pd.read_excel(CAMINHO_EXCEL)
    df.columns = df.columns.str.upper().str.strip()

    # limpar colunas numéricas
    for col in ["VALOR TOTAL", "VALOR PRODUTO", "VALOR EMBALAGEM",
                "VALOR COM IPI", "KG", "TOTAL M2"]:
        if col in df.columns:
            df[col] = df[col].apply(limpar_numero)

    # tratar datas
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df[df["DATA"].notna()]

    # tratar campo PEDIDO (tudo entre 30000 e 50000 é válido)
    df["PEDIDO_NUM"] = df["PEDIDO"].apply(limpar_numero)
    df = df[(df["PEDIDO_NUM"] >= 30000) & (df["PEDIDO_NUM"] <= 50000)]

    return df

# ======================================================
# 🔥 PERÍODOS CORRETOS (ATUAL E ANTERIOR)
# ======================================================
def obter_periodos(df):
    ultima_data = df["DATA"].max()

    ano_atual = ultima_data.year
    mes_atual = ultima_data.month
    dia_atual = ultima_data.day

    # Período atual sempre 01 → última data real
    inicio_atual = ultima_data.replace(day=1)
    fim_atual = ultima_data

    # Ano anterior
    ano_anterior = ano_atual - 1
    inicio_ant = inicio_atual.replace(year=ano_anterior)
    fim_alvo_ant = ultima_data.replace(year=ano_anterior)

    df_ant = df[
        (df["DATA"].dt.year == ano_anterior) &
        (df["DATA"].dt.month == mes_atual)
    ]

    if df_ant.empty:
        fim_ant = fim_alvo_ant
    else:
        df_ant_ate_dia = df_ant[df_ant["DATA"] <= fim_alvo_ant]
        if not df_ant_ate_dia.empty:
            fim_ant = df_ant_ate_dia["DATA"].max()
        else:
            fim_ant = df_ant["DATA"].max()

    return (inicio_atual, fim_atual), (inicio_ant, fim_ant)

# ======================================================
# 🔥 RESUMO DO PERÍODO
# ======================================================
def resumo(df, inicio, fim):
    d = df[(df["DATA"] >= inicio) & (df["DATA"] <= fim)]

    total_valor = d["VALOR COM IPI"].sum()
    total_kg = d["KG"].sum()
    total_m2 = d["TOTAL M2"].sum()
    total_ped = len(d)

    ticket = total_valor / total_ped if total_ped else 0
    preco_kg = total_valor / total_kg if total_kg else 0
    preco_m2 = total_valor / total_m2 if total_m2 else 0

    return {
        "pedidos": total_ped,
        "fat": total_valor,
        "kg": total_kg,
        "m2": total_m2,
        "ticket": ticket,
        "preco_kg": preco_kg,
        "preco_m2": preco_m2,
        "inicio": inicio.strftime("%d/%m/%Y"),
        "fim": fim.strftime("%d/%m/%Y")
    }

# ======================================================
# 🔥 SALVAR JSON DUPLO (dados/ e site/dados/)
# ======================================================
def salvar(nome, dados):
    with open(f"dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    with open(f"site/dados/{nome}", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ======================================================
# 🔥 EXECUÇÃO PRINCIPAL
# ======================================================
if __name__ == "__main__":
    df = carregar()
    (inicio_atual, fim_atual), (inicio_ant, fim_ant) = obter_periodos(df)

    atual = resumo(df, inicio_atual, fim_atual)
    anterior = resumo(df, inicio_ant, fim_ant)

    # ------------------ FATURAMENTO ------------------
    salvar("kpi_faturamento.json", {
        "atual": atual["fat"],
        "ano_anterior": anterior["fat"],
        "variacao": ((atual["fat"]/anterior["fat"]) - 1) * 100 if anterior["fat"] else 0,
        "inicio_mes": atual["inicio"],
        "data_atual": atual["fim"],
        "inicio_mes_anterior": anterior["inicio"],
        "data_ano_anterior": anterior["fim"]
    })

    # ------------------ QUANTIDADE ------------------
    salvar("kpi_quantidade_pedidos.json", {
        "atual": atual["pedidos"],
        "ano_anterior": anterior["pedidos"],
        "variacao": ((atual["pedidos"]/anterior["pedidos"]) - 1) * 100 if anterior["pedidos"] else 0
    })

    # ------------------ KG TOTAL ------------------
    salvar("kpi_kg_total.json", {
        "atual": round(atual["kg"], 0),   # sem casas decimais
        "ano_anterior": round(anterior["kg"], 0),
        "variacao": ((atual["kg"]/anterior["kg"]) - 1) * 100 if anterior["kg"] else 0
    })

    # ------------------ TICKET MÉDIO ------------------
    salvar("kpi_ticket_medio.json", {
        "atual": atual["ticket"],
        "ano_anterior": anterior["ticket"],
        "variacao": ((atual["ticket"]/anterior["ticket"]) - 1) * 100 if anterior["ticket"] else 0
    })

    # ------------------ PREÇO MÉDIO ------------------
    salvar("kpi_preco_medio.json", {
        "atual": {
            "preco_medio_kg": round(atual["preco_kg"], 2),
            "preco_medio_m2": round(atual["preco_m2"], 2),
            "data": atual["fim"]
        },
        "ano_anterior": {
            "preco_medio_kg": round(anterior["preco_kg"], 2),
            "preco_medio_m2": round(anterior["preco_m2"], 2),
            "data": anterior["fim"]
        }
    })

    print("=====================================")
    print(" ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=====================================")
