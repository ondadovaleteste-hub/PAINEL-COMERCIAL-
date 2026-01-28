fetch('dados/kpi_faturamento.json')
  .then(response => response.json())
  .then(data => {

    document.getElementById('fatAtual').innerText =
      `R$ ${data.atual.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} de 01/01/2026 até ${data.data_atual}`;

    document.getElementById('qtdAtual').innerText =
      `${data.qtd_atual} pedidos`;

    document.getElementById('fatAnoAnterior').innerText =
      `R$ ${data.ano_anterior.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} de 01/01/2025 até ${data.data_ano_anterior}`;

    document.getElementById('qtdAnoAnterior').innerText =
      `${data.qtd_ano_anterior} pedidos`;

    const variacaoEl = document.getElementById('fatVariacao');
    const perc = Number(data.variacao);

    if (perc >= 0) {
      variacaoEl.className = 'variacao positivo';
      variacaoEl.innerText = `▲ ${perc}% vs ano anterior`;
    } else {
      variacaoEl.className = 'variacao negativo';
      variacaoEl.innerText = `▼ ${Math.abs(perc)}% vs ano anterior`;
    }

    document.getElementById('fatMeta').innerText =
      `Meta mês: R$ ${data.meta.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

    const metaPercEl = document.getElementById('fatMetaPerc');
    metaPercEl.innerText = `🎯 ${data.meta_perc}% da meta`;

    if (data.meta_perc >= 100) {
      metaPercEl.className = 'meta-perc ok';
    } else if (data.meta_perc >= 80) {
      metaPercEl.className = 'meta-perc atencao';
    } else {
      metaPercEl.className = 'meta-perc ruim';
    }
  });
