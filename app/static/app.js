'use strict';
const $ = id => document.getElementById(id);
const schemas = {vendas:['data','produto','categoria','quantidade','preço unitário'],despesas:['data','descrição','categoria','valor']};
let kind = 'vendas', file = null, result = null, busy = false, aiReady = false, provider = null, mapping = null, sheet = '', inspecting = false, selectionVersion = 0;
const money = n => new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(n);
const integer = n => new Intl.NumberFormat('pt-BR').format(n);
const date = s => s ? s.split('-').reverse().join('/') : 'Sem registros válidos';
const escape = v => String(v ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function status(text, type='success') { $('status').hidden=false; $('status').className='status '+type; $('status').textContent=text; }
function controls() {
  for (const id of ['sales','expenses','demo','drop','remove','export']) $(id).disabled=busy;
  $('analyze').disabled=busy||inspecting||!file||!mapping;
  $('explain').disabled=busy||!result||!result.validos||!aiReady||!$('consent').checked;
  $('consent').disabled=busy||!aiReady;
}
function reset() { result=null; $('results').hidden=true; $('ai-text').textContent=''; $('ai-text').className='ai-text'; $('consent').checked=false; }
function mode(next) {
  if(busy) return;
  kind=next; file=null; mapping=null; selectionVersion++; $('mapping-panel').hidden=true; reset(); $('file').value=''; $('selection').hidden=true; $('status').hidden=true;
  $('sales').classList.toggle('active',kind==='vendas'); $('expenses').classList.toggle('active',kind==='despesas');
  $('sales').setAttribute('aria-pressed',kind==='vendas'); $('expenses').setAttribute('aria-pressed',kind==='despesas');
  $('example').href='/api/example?tipo='+kind;
  $('columns').innerHTML=schemas[kind].map(s=>'<span>'+s+'</span>').join(''); controls();
}
async function select(selected) {
  if(busy) return;
  reset(); file=null; mapping=null; sheet=''; selectionVersion++; $('mapping-panel').hidden=true; $('selection').hidden=true;
  if(!selected) {controls(); return;}
  if(!/\.(xlsx|csv)$/i.test(selected.name)) {status('Escolha uma planilha XLSX ou CSV.','error');controls();return;}
  if(!selected.size||selected.size>5*1024*1024) {status('O arquivo deve ter conteúdo e no máximo 5 MB.','error');controls();return;}
  file=selected; $('filename').textContent=selected.name; $('selection').hidden=false; $('status').hidden=true; controls(); await inspectColumns();
}
async function request(action) {
  const response=await fetch('/api/'+action+'?'+new URLSearchParams({tipo:kind,nome:file.name,aba:sheet,...(mapping?{mapa:JSON.stringify(mapping)}:{})}),{
    method:'POST',body:file,headers:{'Content-Type':'application/octet-stream',...(action==='explain'?{'X-Loja-Consent':'sim'}:{})}
  });
  if(!response.ok) {let data;try{data=await response.json();}catch{throw new Error('O servidor não respondeu. Confira se o sistema está aberto e tente novamente.');}throw new Error(data.erro||'Não foi possível concluir.');}
  return action==='export'?response.blob():response.json();
}
function table(id, headers, rows) {
  $(id).innerHTML=rows.length?'<table><thead><tr>'+headers.map(h=>'<th scope="col">'+escape(h)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(c=>'<td>'+escape(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table>':'<p class="muted">Nenhum registro nesta seção.</p>';
}
function monthlyChart(rows) {
  if(!rows.length){$('monthly').innerHTML='<p class="muted">Corrija os registros para visualizar o gráfico.</p>';return;}
  const width=Math.max(440, rows.length*65+70), height=200, left=65, baseline=165, max=Math.max(...rows.map(r=>r.total),1), step=(width-left-15)/rows.length;
  let svg=`<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Valores mensais em reais">`;
  for(let i=0;i<=3;i++){const y=baseline-i*45;svg+=`<line x1="${left}" x2="${width}" y1="${y}" y2="${y}" stroke="#293a30"/><text x="${left-8}" y="${y+3}" text-anchor="end">${escape(new Intl.NumberFormat('pt-BR',{notation:'compact',maximumFractionDigits:1}).format(max*i/3))}</text>`;}
  rows.forEach((r,i)=>{const h=r.total/max*135,x=left+i*step+step*.2;svg+=`<rect x="${x}" y="${baseline-h}" width="${step*.6}" height="${h}" rx="4" fill="#95efb4"><title>${escape(r.mes)}: ${escape(money(r.total))}</title></rect><text x="${x+step*.3}" y="188" text-anchor="middle">${escape(r.mes.slice(5)+'/'+r.mes.slice(2,4))}</text>`;});
  $('monthly').innerHTML=svg+'</svg>';
}
function render(r) {
  const sales=kind==='vendas';
  $('results').hidden=false; $('period').textContent=r.validos?date(r.inicio)+' a '+date(r.fim)+' · '+integer(r.recebidos)+' registros recebidos':'Nenhum registro pôde ser incluído nos indicadores.';
  const warnings=[...r.avisos];
  if(r.invalidos)warnings.push(`${integer(r.invalidos)} de ${integer(r.recebidos)} registros ficaram fora dos indicadores. A análise é parcial. Confira os problemas abaixo e corrija a planilha.`);
  if(r.duplicados)warnings.push(`${integer(r.duplicados)} possíveis duplicados foram mantidos nos cálculos. Confirme se são operações distintas.`);
  $('warnings').innerHTML=warnings.map(w=>'<div class="warning">'+escape(w)+'</div>').join('');
  if(r.problemas.length) $('warnings').insertAdjacentHTML('beforeend','<a class="secondary review-link" href="#review">Ver erros da planilha ↓</a><p class="muted">A lista mostra a linha do arquivo, a coluna e o que precisa ser corrigido.</p>');
  const cards=[
    [sales?'Faturamento':'Total gasto',r.validos?money(r.total):'Indisponível','Somente registros válidos'],
    [sales?'Quantidade vendida':'Categorias',r.validos?integer(sales?r.quantidade:r.ranking.length):'—',sales?'Unidades informadas':'Com registros válidos'],
    ['Registros incluídos',integer(r.validos),`De ${integer(r.recebidos)} recebidos`],
    ['Registros para revisar',integer(r.invalidos+r.duplicados),`${integer(r.invalidos)} inválidos · ${integer(r.duplicados)} duplicados`]
  ];
  $('metrics').innerHTML=cards.map(c=>`<article class="metric"><label>${escape(c[0])}</label><strong>${escape(c[1])}</strong><small>${escape(c[2])}</small></article>`).join('');
  monthlyChart(r.mensal);
  table('monthly-table',['Mês','Total'],r.mensal.map(x=>[x.mes,money(x.total)]));
  $('ranking-title').textContent=sales?'Participação por produto':'Gastos por categoria';
  $('ranking').innerHTML=r.ranking.length?r.ranking.slice(0,5).map(x=>`<div class="rank-row"><div class="rank-label"><span>${escape(x.nome)}</span><strong>${escape(money(x.total))} · ${escape(x.participacao.toLocaleString('pt-BR'))}%</strong></div><svg class="rank-bar" width="100%" height="7" aria-hidden="true"><rect width="100%" height="7" rx="3" fill="#26352c"/><rect width="${x.participacao}%" height="7" rx="3" fill="#95efb4"/></svg></div>`).join(''):'<p class="muted">Sem registros válidos.</p>';
  table('ranking-table',[sales?'Produto':'Categoria','Total','Participação'],r.ranking.map(x=>[x.nome,money(x.total),x.participacao.toLocaleString('pt-BR')+'%']));
  $('largest-title').textContent=sales?'Maiores vendas informadas':'Maiores despesas';
  table('largest',['Data',sales?'Produto':'Descrição','Valor'],r.maiores.map(x=>[date(x.data),x.descricao,money(x.total)]));
  $('issue-count').textContent=integer(r.problemas.length)+' apontamentos';
  table('issues',['Linha','Campo','Situação','O que conferir'],r.problemas.map(x=>[x.linha,x.campo,x.nivel==='erro'?'Fora dos indicadores':'Mantido nos cálculos',x.mensagem]));
  if(!r.problemas.length)$('issues').innerHTML='<p class="muted">Nenhum problema encontrado na validação.</p>';
  $('ai-preview').textContent=JSON.stringify(r.previa_ia,null,2);
  $('ai-status').textContent=aiReady?'A IA pode explicar estes resultados após sua autorização. Os números exibidos são calculados pelo sistema.':'A IA ainda não está configurada. Os indicadores e o relatório já estão disponíveis. Nenhuma explicação por IA foi gerada.';
  $('ai-tag').textContent=aiReady?'Disponível com autorização':'Não configurada';
  $('ai-disclosure-title').textContent=provider==='Gemini'?'Veja o que será enviado ao Google Gemini':'Veja os indicadores que a IA receberá';
  $('ai-disclosure').textContent=provider==='Gemini'?'Esses indicadores serão enviados ao Google Gemini. No nível gratuito, o provedor pode utilizar os dados para aprimorar seus produtos. Evite dados confidenciais. Se o limite gratuito acabar, a explicação ficará indisponível. Não há troca automática para uma API paga.':provider==='Ollama local'?'O Ollama receberá esses indicadores somente no seu computador. Nenhuma informação é enviada para serviços externos.':'A IA é opcional: Gemini com projeto no nível gratuito ou Ollama instalado localmente. Nenhuma consulta de IA será realizada sem configuração e autorização.';
  $('consent-label').textContent=provider==='Gemini'?'Autorizo o envio destes indicadores ao Google Gemini para gerar a explicação.':'Autorizo o uso destes indicadores pela IA local para gerar a explicação.';
  controls();
}
async function analyze() {
  if(!file||busy)return;
  busy=true;controls();status('Conferindo sua planilha e calculando os resultados…','loading');
  try {result=await request('analyze');render(result);status(result.validos?'Análise concluída. Confira os resultados e os avisos abaixo.':'A planilha foi lida, mas todos os registros precisam de correção.',result.validos?'success':'error');$('results').scrollIntoView({behavior:'smooth',block:'start'});}
  catch(e){reset();status(e.message,'error');}
  finally{busy=false;controls();}
}
$('sales').addEventListener('click',()=>mode('vendas'));$('expenses').addEventListener('click',()=>mode('despesas'));
$('drop').addEventListener('click',()=>$('file').click());$('file').addEventListener('change',e=>select(e.target.files[0]));
$('remove').addEventListener('click',()=>{select(null);$('file').value='';});$('analyze').addEventListener('click',analyze);
for(const event of ['dragenter','dragover'])$('drop').addEventListener(event,e=>{e.preventDefault();if(!busy)$('drop').classList.add('drag');});
for(const event of ['dragleave','drop'])$('drop').addEventListener(event,e=>{e.preventDefault();$('drop').classList.remove('drag');});
$('drop').addEventListener('drop',e=>{if(e.dataTransfer.files.length!==1){status('Envie uma planilha de cada vez.','error');return;}select(e.dataTransfer.files[0]);});
// Prevent a dropped file outside the target from navigating away.
window.addEventListener('dragover',e=>e.preventDefault());window.addEventListener('drop',e=>e.preventDefault());
$('demo').addEventListener('click',async()=>{
  if(busy)return;busy=true;controls();status('Preparando os dados fictícios…','loading');
  try{const response=await fetch('/api/example?tipo='+kind);if(!response.ok)throw new Error('Não foi possível carregar o exemplo.');const blob=await response.blob();busy=false;await select(new File([blob],'exemplo_'+kind+'.xlsx',{type:blob.type}));if(mapping)await analyze();}
  catch(e){busy=false;status(e.message,'error');controls();}
});
$('export').addEventListener('click',async()=>{
  if(!result||busy)return;busy=true;controls();status('Preparando sua planilha com resultados e conferência…','loading');
  try{const blob=await request('export'),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='relatorio_'+kind+'.xlsx';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('Relatório pronto. O download inclui dados originais, tratados, indicadores e problemas.');}
  catch(e){status(e.message,'error');}finally{busy=false;controls();}
});
$('consent').addEventListener('change',controls);
$('explain').addEventListener('click',async()=>{
  if(busy||!aiReady||!$('consent').checked)return;busy=true;controls();$('ai-text').className='ai-text';$('ai-text').textContent='A IA está preparando a explicação…';
  try{const data=await request('explain');$('ai-text').textContent=data.texto;$('ai-tag').textContent='Gerado por IA · '+data.origem;}
  catch(e){$('ai-text').className='ai-text error';$('ai-text').textContent=e.message+' Nenhuma explicação por IA foi gerada.';}
  finally{busy=false;controls();}
});
mode('vendas');
fetch('/api/status').then(r=>{if(!r.ok)throw new Error();return r.json();}).then(r=>{aiReady=r.ia_configurada;provider=r.provedor;if(result)render(result);controls();}).catch(()=>status('Não foi possível conectar ao sistema. Abra o servidor local e recarregue a página.','error'));

const fieldLabels = {data:'Data', produto:'Produto', categoria:'Categoria', quantidade:'Quantidade', preco_unitario:'Preço unitário', descricao:'Descrição', valor:'Valor da despesa'};
function updateMapping() {
  const selects = [...$('mapping-fields').querySelectorAll('select')];
  const values = selects.map(el=>el.value);
  mapping = values.every(Boolean) && new Set(values).size===values.length ? Object.fromEntries(selects.map(el=>[el.dataset.field, el.value])) : null;
  controls();
}
async function inspectColumns() {
  const version = ++selectionVersion;
  inspecting=true; mapping=null; controls(); status('Lendo as abas e colunas da planilha…','loading');
  try {
    const data=await request('inspect');
    if(version!==selectionVersion)return;
    sheet=data.aba;
    $('sheet-label').hidden=data.abas.length<2;
    $('sheet-select').innerHTML=data.abas.map(name=>`<option value="${escape(name)}" ${name===sheet?'selected':''}>${escape(name)}</option>`).join('');
    $('mapping-fields').innerHTML=data.campos.map(field=>`<label>${escape(fieldLabels[field])}<select data-field="${escape(field)}"><option value="">Escolha a coluna</option>${data.colunas.map(col=>`<option value="${escape(col.chave)}" ${data.sugestoes[field]===col.chave?'selected':''}>${escape(col.nome)}</option>`).join('')}</select></label>`).join('');
    $('mapping-panel').hidden=false;
    for(const el of $('mapping-fields').querySelectorAll('select'))el.addEventListener('change',updateMapping);
    $('status').hidden=true;
    updateMapping();
  } catch(e) { if(version===selectionVersion) status(e.message,'error'); }
  finally {if(version===selectionVersion){inspecting=false; controls();}}
}
$('sheet-select').addEventListener('change',async e=>{sheet=e.target.value;reset();await inspectColumns();});
