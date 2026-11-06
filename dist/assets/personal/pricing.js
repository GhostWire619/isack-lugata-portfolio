(() => {
  const exchange = {"date": "2026-11-06", "source": "https://www.bot.go.tz/ExchangeRate/excRates?lang=en", "TZS": 1, "USD": 2640.4435, "EUR": 2963.6337};
  const format = (value, currency) => currency === 'TZS' ? 'TSh ' + value.toLocaleString('en-US') : '≈ ' + new Intl.NumberFormat('en-US',{style:'currency',currency,maximumFractionDigits:0}).format(value / exchange[currency]);
  function select(currency) {
    if (!['TZS','USD','EUR'].includes(currency)) currency = 'TZS';
    document.querySelectorAll('[data-price]').forEach(node => { node.textContent = format(Number(node.dataset.price),currency); });
    document.querySelectorAll('[data-currency]').forEach(button => button.setAttribute('aria-pressed',String(button.dataset.currency === currency)));
    document.querySelectorAll('[data-package]').forEach(link => {
      const price = Number(link.dataset.packagePrice);
      link.dataset.packageDisplay = format(price,currency);
    });
    const note = document.getElementById('currency-note');
    note.replaceChildren(document.createTextNode(currency === 'TZS' ? 'Prices are in Tanzanian shillings. USD and EUR are approximate display conversions. ' : 'Approximate equivalents using Bank of Tanzania mean rates dated 6 November 2026. Final quotes are agreed in TZS; bank charges and exchange movements may differ. '));
    if (currency !== 'TZS') {
      const source = document.createElement('a'); source.href = exchange.source; source.target='_blank'; source.rel='noopener noreferrer'; source.textContent='Rate source'; note.append(source);
    }
    try { localStorage.setItem('portfolio-currency',currency); } catch {}
  }
  document.querySelectorAll('[data-currency]').forEach(button => button.addEventListener('click',() => select(button.dataset.currency)));
  let currency='TZS'; try { currency=localStorage.getItem('portfolio-currency') || 'TZS'; } catch {}
  select(currency);
})();
