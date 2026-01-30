async function carregarJSON(caminho) {
  try {
    const r = await fetch(caminho);
    if (!r.ok) return null;
    return await r.json();
  } catch (e) {
    console.error("Erro ao carregar:", caminho, e);
    return null;
  }
}

async function carregarKPIs() {
  const faturamento = await carregarJSON("site/dados/kpi_faturamento.json");
  const pedidos = await carregarJSON("site/dados/kpi_quantidade_pedidos.json");
  const kg = await carregarJSON("site/dados/kpi_kg_total.json");
  const ticket = await carregarJSON("site/dados/kpi_ticket_medio.json");
  const preco = await carregarJSON("site/dados/kpi_preco_medio.json");

  return { faturamento, pedidos, kg, ticket, preco };
}

function atualizarTela(d) {
  const fat = d.faturamento;
  const ped = d.pedidos;
  const kg = d.kg;
  const ticket = d.ticket;
  const preco = d.preco;

  /* ================================
     SLIDE 1 - FATURAMENTO
  ================================= */
  if (fat && ped) {
    // Quantidade de pedidos
    document.getElementById("fatQtdAtual").innerText =
      ped.atual?.toLocaleString("pt-BR") ?? "--";

    document.getElementById("fatQtdAnterior").innerText =
      ped.ano_anterior?.toLocaleString("pt-BR") ?? "--";

    // Valores de faturamento
    document.getElementById("fatValorAtual").innerText =
      fat.atual != null
        ? `R$ ${fat.atual.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "--";

    document.getElementById("fatValorAnterior").innerText =
      fat.ano_anterior != null
        ? `R$ ${fat.ano_anterior.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "--";

    // Datas
    document.getElementById("fatDataAtual").innerText =
      fat.data_atual ?? fat.data ?? "--";

    document.getElementById("fatDataAnterior").innerText =
      fat.data_ano_anterior ?? "--";

    // Variação
    document.getElementById("fatVariacao").innerText =
      fat.variacao != null ? `${fat.variacao}%` : "--";

    // Meta faturamento (se existir no JSON)
    if (fat.meta != null) {
      document.getElementById("fatMetaValor").innerText = `Meta mês: R$ ${fat.meta.toLocaleString(
        "pt-BR",
        { minimumFractionDigits: 2, maximumFractionDigits: 2 }
      )}`;
    } else {
      document.getElementById("fatMetaValor").innerText = "Meta mês: --";
    }

    if (fat.meta_perc != null) {
      document.getElementById("fatMetaPerc").innerText = `🎯 ${fat.meta_perc}% da meta`;
    } else if (fat.meta != null && fat.atual != null && fat.meta > 0) {
      const perc = ((fat.atual / fat.meta) * 100).toFixed(1);
      document.getElementById("fatMetaPerc").innerText = `🎯 ${perc}% da meta`;
    } else {
      document.getElementById("fatMetaPerc").innerText = "🎯 -- % da meta";
    }
  }

  /* ================================
     SLIDE 2 - KG TOTAL
  ================================= */
  if (kg && ped) {
    document.getElementById("kgQtdAtual").innerText =
      ped.atual?.toLocaleString("pt-BR") ?? "--";

    document.getElementById("kgQtdAnterior").innerText =
      ped.ano_anterior?.toLocaleString("pt-BR") ?? "--";

    document.getElementById("kgValorAtual").innerText =
      kg.atual != null
        ? `${kg.atual.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })} kg`
        : "--";

    document.getElementById("kgValorAnterior").innerText =
      kg.ano_anterior != null
        ? `${kg.ano_anterior.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })} kg`
        : "--";

    // Reaproveito as datas do faturamento (mesmo mês)
    if (fat) {
      document.getElementById("kgDataAtual").innerText =
        fat.data_atual ?? fat.data ?? "--";
      document.getElementById("kgDataAnterior").innerText =
        fat.data_ano_anterior ?? "--";
    } else {
      document.getElementById("kgDataAtual").innerText = "--";
      document.getElementById("kgDataAnterior").innerText = "--";
    }

    document.getElementById("kgVariacao").innerText =
      kg.variacao != null ? `${kg.variacao}%` : "--";

    if (kg.meta != null) {
      document.getElementById("kgMetaValor").innerText =
        `Meta mês: ${kg.meta.toLocaleString("pt-BR")} kg`;
    } else {
      document.getElementById("kgMetaValor").innerText = "Meta mês: --";
    }

    if (kg.meta_perc != null) {
      document.getElementById("kgMetaPerc").innerText =
        `🎯 ${kg.meta_perc}% da meta`;
    } else if (kg.meta != null && kg.atual != null && kg.meta > 0) {
      const perc = ((kg.atual / kg.meta) * 100).toFixed(1);
      document.getElementById("kgMetaPerc").innerText =
        `🎯 ${perc}% da meta`;
    } else {
      document.getElementById("kgMetaPerc").innerText =
        "🎯 -- % da meta";
    }
  }

  /* ================================
     SLIDE 3 - TICKET MÉDIO
  ================================= */
  if (ticket && ped) {
    document.getElementById("ticketAtual").innerText =
      ticket.atual != null
        ? `R$ ${ticket.atual.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "--";

    document.getElementById("ticketAnterior").innerText =
      ticket.ano_anterior != null
        ? `R$ ${ticket.ano_anterior.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "--";

    document.getElementById("ticketQtdAtual").innerText =
      ped.atual != null
        ? `${ped.atual.toLocaleString("pt-BR")} pedidos`
        : "--";

    document.getElementById("ticketQtdAnterior").innerText =
      ped.ano_anterior != null
        ? `${ped.ano_anterior.toLocaleString("pt-BR")} pedidos`
        : "--";

    document.getElementById("ticketVariacao").innerText =
      ticket.variacao != null ? `${ticket.variacao}%` : "--";
  }

  /* ================================
     SLIDE 4 - PREÇO MÉDIO KG / M²
  ================================= */
  if (preco) {
    document.getElementById("precoMedioKg").innerText =
      preco.preco_medio_kg != null
        ? `R$ ${preco.preco_medio_kg.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "--";

    document.getElementById("precoMedioM2").innerText =
      preco.preco_medio_m2 != null
        ? `R$ ${preco.preco_medio_m2.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}`
        : "--";

    const dataBase = preco.data ?? "";
    document.getElementById("precoKgBase").innerText =
      preco.total_kg != null
        ? `Base: ${preco.total_kg.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })} kg ${dataBase ? " - " + dataBase : ""}`
        : "--";

    document.getElementById("precoM2Base").innerText =
      preco.total_m2 != null
        ? `Base: ${preco.total_m2.toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })} m² ${dataBase ? " - " + dataBase : ""}`
        : "--";
  }
}

/* INICIAR */
(async () => {
  const dados = await carregarKPIs();
  atualizarTela(dados);
})();
