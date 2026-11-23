(function weeklyNews(){
 const current=document.getElementById('weekly-current');
 const status=document.getElementById('weekly-status');
 const history=document.getElementById('weekly-history-inside');
 const make=(tag,cls,text)=>{
  const e=document.createElement(tag);if(cls)e.className=cls;
  if(text!==undefined)e.textContent=String(text);return e;
 };
 const validUrl=url=>typeof url==='string'&&url.startsWith('https://');
 const dateString=v=>{
  const d=new Date(String(v||'')+'T12:00:00Z');
  return Number.isNaN(d.getTime())?String(v||''):
   d.toLocaleDateString('sv-SE',{timeZone:'Europe/Stockholm',day:'numeric',month:'short',year:'numeric'});
 };
 const stamp=v=>{
  const d=new Date(v);
  return Number.isNaN(d.getTime())?String(v||''):d.toLocaleString('sv-SE',{
   timeZone:'Europe/Stockholm',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});
 };
 const addLink=(parent,url,text)=>{
  if(!validUrl(url))return;
  const a=make('a','',text);a.href=url;a.target='_blank';a.rel='noopener noreferrer';parent.append(a);
 };


 const popup=document.getElementById('weekly-event-overlay');
 const closeButton=document.getElementById('weekly-event-close');
 let originalFocus=null;
 function hideEvent(){
  if(popup.hidden)return;
  popup.hidden=true;
  document.body.classList.remove('weekly-dialog-open');
  if(originalFocus&&originalFocus.isConnected)originalFocus.focus();
 }
 function openEvent(it,trigger){
  originalFocus=trigger;
  document.getElementById('weekly-event-meta').textContent=dateString(it.date)+' · '+(it.category||'Händelse')+
   ' · '+(it.editorial_verified||it.verified?'Källgranskad uppgift':'Nyhetsrubrik');
  document.getElementById('weekly-event-title').textContent=it.title||'Veckans händelse';
  document.getElementById('weekly-event-lead').textContent=it.summary||it.title||'';
  const facts=document.getElementById('weekly-event-facts');
  facts.replaceChildren();const bulletItems=Array.isArray(it.key_facts)?it.key_facts:[];
  facts.hidden=!bulletItems.length;
  if(bulletItems.length){
   facts.append(make('strong','','Viktigaste uppgifterna'));
   const ul=make('ul');
   for(const value of bulletItems){ul.append(make('li','',value));}
   facts.append(ul);
  }
  const details=document.getElementById('weekly-event-detail');
  details.replaceChildren();details.hidden=!it.details;
  if(it.details){details.append(make('strong','','Mer om händelsen'),make('p','',it.details));}
  const relevance=document.getElementById('weekly-event-importance');
  relevance.replaceChildren();relevance.hidden=!it.importance;
  if(it.importance){relevance.append(make('strong','','Varför det spelar roll'),make('p','',it.importance));}
  const links=document.getElementById('weekly-event-links');links.replaceChildren();
  addLink(links,it.url,'Läs originalkällan ↗');
  if(it.additional_source_url&&it.additional_source_url!==it.url){
   addLink(links,it.additional_source_url,'Se ytterligare publicering ↗');
  }
  popup.hidden=false;document.body.classList.add('weekly-dialog-open');closeButton.focus();
 }
 function items(parent,records){
  const grid=make('div','weekly-events');
  for(const it of records){
   const card=make('article','weekly-card'),button=make('button','weekly-event-open');
   button.type='button';
   button.setAttribute('aria-haspopup','dialog');
   button.setAttribute('aria-controls','weekly-event-overlay');
   button.setAttribute('aria-label','Visa fördjupning: '+(it.title||'Veckans händelse'));
   const meta=make('div','weekly-meta');
   meta.append(make('span','',dateString(it.date)),make('span','',it.category||'Händelse'));
   button.append(meta,make('h4','',it.title||'Händelse'));
   if(it.summary){button.append(make('p','',it.summary));}
   button.append(make('div','weekly-origin'+(it.editorial_verified||it.verified?' verified':''),
    (it.editorial_verified||it.verified?'Källgranskad uppgift':'Nyhetsrubrik')+' · '+(it.source||'Källa')));
   const cue=make('span','weekly-open-cue','→');cue.setAttribute('aria-hidden','true');button.append(cue);
   button.addEventListener('click',()=>openEvent(it,button));
   card.append(button);grid.append(card);
  }
  parent.append(grid);
 }
 closeButton.addEventListener('click',hideEvent);
 popup.addEventListener('click',event=>{if(event.target===popup)hideEvent();});
 document.addEventListener('keydown',event=>{
  if(popup.hidden)return;
  if(event.key==='Escape'){event.preventDefault();event.stopPropagation();hideEvent();return;}
  if(event.key!=='Tab')return;
  const focusables=[...popup.querySelectorAll('button:not([disabled]),a[href]')].filter(x=>x.getClientRects().length);
  if(!focusables.length)return;
  const first=focusables[0],last=focusables[focusables.length-1];
  if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
  else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
 });

 const formatSEK = value => value.toLocaleString('sv-SE', {maximumFractionDigits: 4});
 const percent = new Intl.NumberFormat('sv-SE', {maximumFractionDigits: 2, signDisplay: 'exceptZero'});
 const countNoun = (count, singular, plural) => count + ' ' + (count === 1 ? singular : plural);
 const eventCount = count => countNoun(count, 'händelse', 'händelser');
 const verified = item => Boolean(item.editorial_verified || item.verified);

 function currentChange() {
   const q = window.currentMarketQuote;
   if (!q || !(q.baseline > 0) || !q.baseline_date) return null;
   const difference = q.price - q.baseline;
   return {baseline: q.baseline, baseline_date: q.baseline_date, latest: q.price,
     latest_date: q.quote_time.slice(0, 10), change_sek: difference,
     change_percent: 100 * difference / q.baseline, source_url: q.source_url};
 }
 window.addEventListener('marketquote', () => {
   const panel = current.querySelector('.week-price');
   if (panel) panel.replaceWith(quotePanel(currentChange()));
 });
 function quotePanel(quote) {
   const box = make('div', 'week-price');
   box.append(make('h3', '', 'Kursutveckling · 5 handelsdagar'));
   if (!quote || quote.unavailable || !Number.isFinite(quote.change_percent)) {
     box.append(make('p', '', 'Jämförelsekurser saknas.'));
     return box;
   }
   const direction = quote.change_percent < 0 ? 'negative' : quote.change_percent > 0 ? 'positive' : '';
   box.append(make('strong', 'week-return ' + direction, percent.format(quote.change_percent) + ' %'));
   if (Number.isFinite(quote.change_sek)) {
     const signed = quote.change_sek > 0 ? '+' : '';
     box.append(make('span', 'week-absolute', signed + formatSEK(quote.change_sek) + ' kr per aktie'));
   }
   const values = make('dl', 'week-price-values');
   for (const [date, value] of [[quote.baseline_date, quote.baseline], [quote.latest_date, quote.latest]]) {
     if (!date || !Number.isFinite(value)) continue;
     values.append(make('dt', '', dateString(date)), make('dd', '', formatSEK(value) + ' kr'));
   }
   box.append(values);
   addLink(box, quote.source_url, 'Kurshistorik ↗');
   return box;
 }

 function analysisPanel(week) {
   const panel = make('div', 'weekly-analysis');
   panel.append(make('h3', '', 'Finansiering och milstolpar'));
   const snapshot = week.finance_snapshot || {};
   if (typeof snapshot.risk_6 === 'number') {
     panel.append(make('strong', 'week-risk', snapshot.risk_6.toLocaleString('sv-SE', {maximumFractionDigits: 1}) + ' %'),
       make('span', 'week-risk-label', 'Modellrisk för emission inom sex månader'));
   } else if (snapshot.emission_status) {
     panel.append(make('strong', 'week-finance-status', snapshot.emission_status.replace(/_/g, ' ')));
   }
   if (snapshot.explanation) panel.append(make('p', 'weekly-small', snapshot.explanation));
   if (snapshot.risk_as_of) panel.append(make('p', 'weekly-small', 'Avläst ' + stamp(snapshot.risk_as_of)));
   const updates = week.updates || [];
   if (updates.length) {
     const details = make('details', 'week-changes');
     details.append(make('summary', '', 'Analysändringar (' + updates.length + ')'));
     const list = make('ul', 'weekly-changes');
     for (const update of updates) {
       const item = make('li');
       item.append(make('strong', '', update.title || 'Uppdatering'), make('p', '', update.detail || ''));
       addLink(item, update.url, 'Källa ↗');
       list.append(item);
     }
     details.append(list);
     panel.append(details);
   } else panel.append(make('p', 'weekly-small', 'Inga registrerade analysändringar.'));
   return panel;
 }

 function edition(week) {
   const shell = make('div', 'weekly-main week-layout');
   const feed = make('div', 'week-feed');
   const records = week.events || [];
   const meta = make('div', 'week-feed-heading');
   const range = dateString(week.start) + ' – ' + dateString(week.end);
   meta.append(make('h3', '', range),
     make('span', '', eventCount(records.length) + ' · ' + countNoun(records.filter(verified).length, 'källgranskad', 'källgranskade')));
   feed.append(meta);
   if (records.length) items(feed, records.slice(0, 4));
   else feed.append(make('p', 'weekly-small', 'Inga daterade händelser i de kontrollerade källorna under perioden.'));
   if (records.length > 4) {
     const more = make('details', 'weekly-more');
     more.append(make('summary', '', 'Visa ytterligare ' + eventCount(records.length - 4)));
     items(more, records.slice(4));
     feed.append(more);
   }
   const side = make('aside', 'week-context');
   side.setAttribute('aria-label', 'Handelsveckan och analysen');
   side.append(quotePanel(currentChange()), analysisPanel(week));
   shell.append(feed, side);
   if (week.omitted_events) shell.append(make('p', 'weekly-foot', week.omitted_events + ' rubriker utelämnades i underlaget.'));
   if (week.source_errors?.length) shell.append(make('p', 'weekly-foot', 'Ofullständig källkontroll. ' + week.source_errors.join(' · ')));
   return shell;
 }
 fetch('./data/weekly_news.json',{cache:'no-store'})
 .then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();})
 .then(d=>{
  const weeks=(Array.isArray(d.weeks)?d.weeks:[]).slice().sort((a,b)=>String(b.id).localeCompare(String(a.id)));
  if(!weeks.length)throw new Error('Ingen nyhetshistorik finns ännu');
  const stockholmDay=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  const cutoff=new Date(stockholmDay+'T12:00:00Z');cutoff.setUTCDate(cutoff.getUTCDate()-6);
  const startDay=cutoff.toISOString().slice(0,10);
  const all=new Map();
  for(const w of weeks)for(const e of (w.events||[])){
   if(!e.date)continue;
   const key=e.date+'|'+(e.url||e.title);
   if(!all.has(key))all.set(key,e);
  }
  const sorted=[...all.values()].sort((a,b)=>String(b.date).localeCompare(String(a.date)));
  const recent=sorted.filter(e=>e.date>=startDay&&e.date<=stockholmDay);
  const older=sorted.filter(e=>e.date<startDay);
  const latest=weeks[0];
  const rolling={...latest,week:null,start:startDay,end:stockholmDay,events:recent,intro:'Nyheter publicerade under de senaste sju kalenderdagarna.'};
  current.replaceChildren(edition(rolling));
  status.textContent='Kontrollerat '+stamp(d.updated_at);
  const months=new Map();
  for(const e of older){const key=e.date.slice(0,7);if(!months.has(key))months.set(key,[]);months.get(key).push(e)}
  history.replaceChildren();
  const monthNames=['januari','februari','mars','april','maj','juni','juli','augusti','september','oktober','november','december'];
  for(const [key,events] of [...months].sort((a,b)=>b[0].localeCompare(a[0]))){
   const group=make('details','weekly-past');
   const [year,month]=key.split('-').map(Number);
   group.append(make('summary','',monthNames[month-1]+' '+year+' · '+eventCount(events.length)));
   const content=make('div','weekly-main');
   items(content,events);
   group.append(content);history.append(group);
  }
  if(!months.size) history.append(make('p','weekly-small','Inga tidigare månader i arkivet.'));
  document.getElementById('weekly-history-count').textContent='('+countNoun(months.size,'månad','månader')+')';
 })
 .catch(e=>{
  status.textContent='Kunde inte läsa veckans nyheter.';
  history.replaceChildren(make('p','weekly-small','Nyhetsarkivet kunde inte hämtas.'));
  current.replaceChildren(make('p','weekly-small','Se nyhetsflödet längre ned på sidan och GitHub Actions för källkontroll.'));
 });
})();
