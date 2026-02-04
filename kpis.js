function carregarJSON(nome) {
  return fetch("site/dados/" + nome)
    .then(r => r.json())
    .catch(() => null);
}

function moeda(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function numero(v) {
  return v.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
}

function perc(v) {
  return v.toFixed(1).replace(".", ",") + "%";
}

function cor(el, v) {
  el.classList.remove("positivo", "negativo");
  if (v > 0) el.classList.add("positivo");
  if (v < 0) el.classList.add("negativo");
}

Promise.all([
  carregarJSON("kpi_faturamento.json"),
  carregarJSON("kpi_quantidade_pedidos.json"),
  carregarJSON("kpi_ticket_medio.json"),
  carregarJSON("kpi_kg_total.json"),
  carregarJSON("kpi_preco_medio.json")
]).then(([fat, qtd, ticket, kg, preco]) => {

  /* FAT */
  document.getElementById("fatQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("fatValorAtual").innerText = moeda(fat.atual);
  document.getElementById("fatDataAtual").innerText =
    "de 01/" + fat.data_atual.substring(3) + " até " + fat.data_atual;

  document.getElementById("fatQtdAnterior").innerText = qtd.ano_anterior + " pedidos";
  document.getElementById("fatValorAnterior").innerText = moeda(fat.ano_anterior);
  document.getElementById("fatDataAnterior").innerText =
    "de 01/" + fat.data_ano_anterior.substring(3) + " até " + fat.data_ano_anterior;

  const vFat = document.getElementById("fatVariacao");
  vFat.innerText = (fat.variacao >= 0 ? "▲ " : "▼ ") + perc(Math.abs(fat.variacao));
  cor(vFat, fat.variacao);

  /* KG */
  document.getElementById("kgQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("kgValorAtual").innerText = numero(kg.atual) + " kg";
  document.getElementById("kgDataAtual").innerText = document.getElementById("fatDataAtual").innerText;

  document.getElementById("kgQtdAnterior").innerText = qtd.ano_anterior + " pedidos";
  document.getElementById("kgValorAnterior").innerText = numero(kg.ano_anterior) + " kg";
  document.getElementById("kgDataAnterior").innerText = document.getElementById("fatDataAnterior").innerText;

  const vKg = document.getElementById("kgVariacao");
  vKg.innerText = (kg.variacao >= 0 ? "▲ " : "▼ ") + perc(Math.abs(kg.variacao));
  cor(vKg, kg.variacao);

  /* TICKET */
  document.getElementById("ticketAtual").innerText = moeda(ticket.atual);
  document.getElementById("ticketAnterior").innerText = moeda(ticket.ano_anterior);
  document.getElementById("ticketQtdAtual").innerText = qtd.atual + " pedidos";
  document.getElementById("ticketQtdAnterior").innerText = qtd.ano_anterior + " pedidos";

  const vTicket = document.getElementById("ticketVariacao");
  vTicket.innerText = (ticket.variacao >= 0 ? "▲ " : "▼ ") + perc(Math.abs(ticket.variacao));
  cor(vTicket, ticket.variacao);

  /* PREÇO MÉDIO */
  document.getElementById("precoMedioKG").innerText = moeda(preco.preco_medio_kg);
  document.getElementById("precoMedioM2").innerText = moeda(preco.preco_medio_m2);
  document.getElementById("precoDataKG").innerText = "Atualizado até " + preco.data;
  document.getElementById("precoDataM2").innerText = "Atualizado até " + preco.data;
});
