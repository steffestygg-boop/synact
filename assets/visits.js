(async () => {
  const counters = document.querySelector('[data-visits]');
  if (!counters || location.hostname !== 'steffestygg-boop.github.io') return;
  const endpoint = 'https://counterapi.com/api/steffestygg-boop.github.io/view/' + counters.dataset.visits;
  async function display(id, query) {
    const field = document.getElementById(id);
    try {
      const response = await fetch(endpoint + query, {cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer'});
      if (!response.ok) throw new Error('Counter unavailable');
      const {value} = await response.json();
      if (value == null || !/^\d+$/.test(String(value))) throw new Error('Invalid count');
      field.textContent = Number(value).toLocaleString('sv-SE');
    } catch {
      field.textContent = 'Ej tillgängligt';
    }
  }
  await display('visits-total', '');
  await display('visits-week', '?readOnly=true&timeline=7d');
})();