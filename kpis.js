document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ kpis.js carregado');

  const BASE = 'site/dados/';

  function el(id) {
    const e = document.getElementById(id);
    if (!e) console.error('❌ ID não encontrado:', id);
    return e;
  }

  function dinheiro(v) {
    if (v === null || v === undefined) return '--';
    return 'R$ ' + Number(v).toLocaleString('pt-BR', {
      minimumFractionDigits: 2
    });
  }

  /* ================================
     FATURAMENTO
  ================================= */
  fetch(BASE + 'kpi_faturamento.json', { cache: 'no-store' })
    .then(r => r.json())
    .then(fat => {
      console.log('📦 faturamento:', fat);

      el('fatAtual').innerText = dinheiro(fat.atual);
      el('periodoAtual').innerText = `(até ${fat.data_fim})`;

      el('fatAnoAnterior').innerText = dinheiro(fat.ano_anterior);
      el('periodoAnterior').innerText =
        `(até ${fat.data_fim.replace('2026', '2025')})`;

      el('fatVariacao').innerText =
        fat.variacao !== null
          ? `▲ ${fat.variacao.toFixed(1)}% vs ano anterior`
          : '--';
    })
    .catch(err => console.error('🔥 Erro faturamento:', err));

  /* ================================
     QUANTIDADE DE PEDIDOS
  ================================= */
  fetch(BASE + 'kpi_quantidade_pedidos.json', { cache: 'no-store' })
    .then(r => r.json())
    .then(qtd => {
      console.log('📦 quantidade:', qtd);

      el('qtdAtual').innerText = `${qtd.atual} pedidos`;
      el('qtdAnoAnterior').innerText = `${qtd.ano_anterior} pedidos`;
    })
    .catch(err => console.error('🔥 Erro quantidade:', err));

  /* ================================
     META (placeholder)
  ================================= */
  el('fatMeta').innerText = 'Meta mês: --';
  el('fatMetaPerc').innerText = '--';
});
