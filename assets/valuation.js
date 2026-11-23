function drawValuations(valuations,openInfo){
 const today=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm'}).format(new Date());
 const names=[...new Set(valuations.map(p=>p.who))];
 const latest=names.map(who=>valuations.filter(p=>p.who===who).sort((a,b)=>b.date.localeCompare(a.date))[0]);
 const svg=document.getElementById('valuation-chart');const ns='http://www.w3.org/2000/svg';
 const el=(tag,atts,parent=svg)=>{const node=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(atts))node.setAttribute(k,v);parent.append(node);return node};
 const left=65,right=1047,top=35,bottom=313;
 const to=Date.parse(today),from=Math.min(...valuations.map(p=>Date.parse(p.date)))-14*86400000;
 const peak=Math.max(...valuations.map(p=>p.value)),step=10**Math.floor(Math.log10(peak))/2;
 const max=Math.ceil(peak/step)*step;
 const x=d=>left+(Date.parse(d)-from)/(to-from)*(right-left);
 const y=v=>bottom-v/max*(bottom-top);
 for(let v=0;v<=max;v+=max/5){el('line',{x1:left,x2:right,y1:y(v),y2:y(v),stroke:'#334657','stroke-dasharray':'5 8'});const t=el('text',{x:52,y:y(v)+4,fill:'#b1c1d0','font-size':12,'text-anchor':'end'});t.textContent=v.toLocaleString('sv-SE',{maximumFractionDigits:2});}
 for(let i=0;i<=4;i++){const date=new Date(from+(to-from)*i/4).toISOString().slice(0,10);const label=i===4?'I dag · '+today:new Date(date).toLocaleDateString('sv-SE',{month:'short',year:'numeric',timeZone:'UTC'});const t=el('text',{x:x(date),y:344,fill:'#b1c1d0','font-size':12,'text-anchor':'middle'});t.textContent=label;}
 const typecolor={Edison:'#5cc8fb',Redeye:'#9fe2b0',BioVal:'#ffba79',ABG:'#5cc8fb'};
 for(const who of names){
  const points=valuations.filter(v=>v.who===who).sort((a,b)=>a.date.localeCompare(b.date));
  el('path',{d:[...points,{date:today,value:points[points.length-1].value}].map((p,i)=>(i?'L':'M')+x(p.date).toFixed(2)+' '+y(p.value).toFixed(2)).join(' '),fill:'none',stroke:typecolor[who],'stroke-width':'2.5','stroke-dasharray':'7 5','stroke-linecap':'round'});
  for(const p of points){
   const dot=el('circle',{cx:x(p.date),cy:y(p.value),r:7,fill:typecolor[who],class:'valuation-point',tabindex:0,role:'button','aria-label':who+' '+p.value.toFixed(2)+' kronor, '+p.date});
   const title=el('title',{},dot);title.textContent=who+' · '+p.value.toFixed(2)+' kr · '+p.date;
   const detail={date:p.date,title:who+' · '+p.value.toLocaleString('sv-SE',{minimumFractionDigits:2,maximumFractionDigits:2})+' kr/aktie',body:p.type+'. '+p.body,url:p.url};
   dot.addEventListener('click',()=>openInfo(detail,dot));dot.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openInfo(detail,dot)}});
   const label=el('text',{x:x(p.date)+(x(p.date)>right-80?-12:12),'text-anchor':x(p.date)>right-80?'end':'start',y:y(p.value)-9,fill:typecolor[who],'font-size':13,'font-weight':750});label.textContent=p.value.toLocaleString('sv-SE',{maximumFractionDigits:2})+' kr';
  }
 }
 const host=document.getElementById('valuation-highlights');for(const p of latest){
  const b=document.createElement('button');b.type='button';b.className='chart-tile';b.innerHTML='<small></small><strong></strong><small></small>';
  b.children[0].textContent=p.who+' · '+p.date;b.children[1].textContent=p.value.toLocaleString('sv-SE',{minimumFractionDigits:2,maximumFractionDigits:2})+' kr';b.children[2].textContent=p.type;
  b.addEventListener('click',()=>openInfo({date:p.date,title:p.who+' · värderingsuppdatering',body:p.body,url:p.url},b));host.append(b);
 }
}
