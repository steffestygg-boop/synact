(async () => {
  const panel = document.querySelector('[data-visits]');
  if (!panel || location.hostname !== 'steffestygg-boop.github.io') return;
  const prefix = 'https://countapi.mileshilliard.com/api/v1/';
  const key = 'minaaktier_steffestygg_20261126_' + panel.dataset.visits;
  const day = new Intl.DateTimeFormat('sv-SE', {timeZone:'Europe/Stockholm'}).format(new Date());
  async function count(action, suffix) {
    const response = await fetch(prefix + action + '/' + key + '_' + suffix, {
      credentials:'omit', referrerPolicy:'no-referrer', cache:'no-store'
    });
    if (action === 'get' && response.status === 404) return 0;
    if (!response.ok) throw new Error('Counter unavailable');
    const data = await response.json();
    if (!/^\d+$/.test(String(data.value))) throw new Error('Invalid count');
    return Number(data.value);
  }
  async function display(id, result) {
    const field = document.getElementById(id);
    try { field.textContent = (await result).toLocaleString('sv-SE'); }
    catch { field.textContent = 'Ej tillgängligt'; }
  }
  const days = Array.from({length:7}, (_, offset) => {
    const date = new Date(Date.parse(day) - offset * 86400000).toISOString().slice(0,10);
    return count(offset === 0 ? 'hit' : 'get', date);
  });
  await Promise.all([
    display('visits-total', count('hit','total')),
    display('visits-week', Promise.all(days).then(values => values.reduce((a,b) => a+b, 0)))
  ]);
})();