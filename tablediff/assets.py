from __future__ import annotations

REPORT_CSS = """
:root{
    --sapBackgroundColor:#f5f6f7;
    --sapShellColor:#354a5f;
    --sapShell_TextColor:#fff;
    --sapPageHeader_Background:#fff;
    --sapObjectHeader_Background:#fff;
    --sapGroup_ContentBackground:#fff;
    --sapList_HeaderBackground:#f7f7f7;
    --sapList_BorderColor:#d9d9d9;
    --sapList_TableGroupHeaderBackground:#f2f2f2;
    --sapTextColor:#1d2d3e;
    --sapContent_LabelColor:#556b82;
    --sapLinkColor:#0a6ed1;
    --sapButton_BorderColor:#0a6ed1;
    --sapButton_TextColor:#0a6ed1;
    --sapButton_Hover_Background:#ebf5fe;
    --sapHighlightColor:#0854a0;
    --sapInformationBackground:#e5f2ff;
    --sapSuccessBackground:#f1fdf6;
    --sapSuccessBorderColor:#188918;
    --sapWarningBackground:#fff8d6;
    --sapWarningBorderColor:#e76500;
    --sapErrorBackground:#ffb8b8;
    --sapErrorBorderColor:#bb0000;
    --sapContent_Shadow0:0 0 0 1px rgba(0,0,0,.08),0 2px 8px rgba(0,0,0,.08);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
    margin:0;
    background:var(--sapBackgroundColor);
    color:var(--sapTextColor);
    font-family:"72","72full",Arial,Helvetica,sans-serif;
    font-size:14px;
    line-height:1.4;
}
a{color:var(--sapLinkColor);text-decoration:none}
a:hover{text-decoration:underline}
.ui5-shellbar{
    position:sticky;
    top:0;
    z-index:10;
    display:flex;
    align-items:center;
    min-height:48px;
    padding:0 24px;
    background:var(--sapShellColor);
    color:var(--sapShell_TextColor);
    box-shadow:0 2px 4px rgba(0,0,0,.18);
}
.ui5-product-switch{font-size:18px;margin-right:12px}
.ui5-shell-title{font-size:16px;font-weight:700}
.ui5-shell-subtitle{margin-left:12px;color:#d3dce6;font-size:13px}
.ui5-page{max-width:1440px;margin:0 auto;padding:24px}
.ui5-object-page-header{
    background:var(--sapObjectHeader_Background);
    border-bottom:1px solid var(--sapList_BorderColor);
    box-shadow:var(--sapContent_Shadow0);
    padding:20px 24px;
}
h1{margin:0;color:var(--sapTextColor);font-size:26px;font-weight:400;letter-spacing:0}
.ui5-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap}
.ui5-subtitle{margin:6px 0 0;color:var(--sapContent_LabelColor);font-size:14px}
.ui5-kpis{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}
.ui5-kpi{
    min-width:132px;
    padding:10px 12px;
    background:#f7f7f7;
    border:1px solid var(--sapList_BorderColor);
    border-radius:4px;
}
.ui5-kpi-value{display:block;font-size:22px;font-weight:700;color:var(--sapHighlightColor)}
.ui5-kpi-label{display:block;margin-top:2px;color:var(--sapContent_LabelColor);font-size:12px}
.ui5-section{margin-top:16px}
.ui5-panel{
    background:var(--sapGroup_ContentBackground);
    border:1px solid var(--sapList_BorderColor);
    border-radius:4px;
    box-shadow:0 1px 2px rgba(0,0,0,.04);
}
.ui5-panel-header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    min-height:44px;
    padding:0 16px;
    background:var(--sapList_HeaderBackground);
    border-bottom:1px solid var(--sapList_BorderColor);
}
.ui5-panel-title{font-size:16px;font-weight:700}
.ui5-toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:12px 16px}
.ui5-button{
    min-height:32px;
    border:1px solid var(--sapButton_BorderColor);
    border-radius:4px;
    background:#fff;
    color:var(--sapButton_TextColor);
    padding:6px 12px;
    font:inherit;
    font-weight:700;
    cursor:pointer;
}
.ui5-button:hover{background:var(--sapButton_Hover_Background)}
.ui5-button:focus-visible,.ui5-input:focus-visible{outline:2px solid var(--sapHighlightColor);outline-offset:1px}
.ui5-button-icon{padding:5px 10px}
.ui5-input{
    min-height:32px;
    width:min(420px,100%);
    border:1px solid #89919a;
    border-radius:4px;
    background:#fff;
    color:var(--sapTextColor);
    padding:6px 10px;
    font:inherit;
}
.ui5-meta-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;padding:16px}
.ui5-label{color:var(--sapContent_LabelColor);font-size:12px}
.ui5-token-list{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.ui5-token{
    display:inline-flex;
    align-items:center;
    min-height:26px;
    max-width:100%;
    border:1px solid #b3d4f5;
    border-radius:4px;
    background:var(--sapInformationBackground);
    color:#174a7c;
    padding:3px 8px;
    overflow-wrap:anywhere;
}
.toc-details{overflow:hidden}
.toc-details>summary,.codeplug-table>summary{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    min-height:44px;
    padding:0 16px;
    background:var(--sapList_HeaderBackground);
    border-bottom:1px solid var(--sapList_BorderColor);
    cursor:pointer;
    font-weight:700;
    list-style:none;
}
.toc-details>summary::-webkit-details-marker,.codeplug-table>summary::-webkit-details-marker{display:none}
.toc-details>summary::before,.codeplug-table>summary::before{content:"\\25B8";color:var(--sapContent_LabelColor);margin-right:2px}
.toc-details[open]>summary::before,.codeplug-table[open]>summary::before{content:"\\25BE"}
.summary-title{flex:1;min-width:0;overflow-wrap:anywhere}
.summary-metrics{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.summary-label{
    display:inline-flex;
    align-items:center;
    min-height:24px;
    border-radius:4px;
    padding:2px 8px;
    font-size:12px;
    font-weight:700;
    white-space:nowrap;
    cursor:pointer;
    font-family:inherit;
}
.summary-label-same{background:var(--sapSuccessBackground);border:1px solid var(--sapSuccessBorderColor);color:#107e3e}
.summary-label-different{background:var(--sapWarningBackground);border:1px solid var(--sapWarningBorderColor);color:#8a4100}
.summary-label-missing{background:#ffcaca;border:1px solid var(--sapErrorBorderColor);color:#8f0000}
.summary-label-active{box-shadow:0 0 0 2px var(--sapHighlightColor)}
.top-link{
    flex:0 0 auto;
    border:1px solid transparent;
    border-radius:4px;
    padding:5px 8px;
    font-size:12px;
    font-weight:700;
}
.top-link:hover{background:var(--sapButton_Hover_Background);text-decoration:none}
.toc-search{display:flex;gap:8px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--sapList_BorderColor)}
.toc{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:0;margin:0;padding:0;list-style:none}
.toc li{border-bottom:1px solid var(--sapList_BorderColor)}
.toc a{display:block;padding:10px 16px;overflow-wrap:anywhere}
.toc a:hover{background:#f0f7ff;text-decoration:none}
.toc-empty{display:none;margin:0;padding:14px 16px;color:var(--sapContent_LabelColor)}
.codeplug-table{margin-top:12px;overflow:hidden}
.table-wrap{overflow:auto;background:#fff}
table{width:100%;border-collapse:collapse;background:#fff;table-layout:auto}
th,td{
    border-bottom:1px solid var(--sapList_BorderColor);
    border-right:1px solid var(--sapList_BorderColor);
    padding:8px 10px;
    text-align:left;
    vertical-align:top;
    overflow-wrap:anywhere;
}
th:last-child,td:last-child{border-right:0}
th{
    background:var(--sapList_TableGroupHeaderBackground);
    color:var(--sapContent_LabelColor);
    font-weight:700;
}
td:first-child{font-weight:700;background:#fafafa}
.same{background:var(--sapSuccessBackground);box-shadow:inset 4px 0 0 var(--sapSuccessBorderColor)}
.different{background:var(--sapWarningBackground);box-shadow:inset 4px 0 0 var(--sapWarningBorderColor)}
.missing{background:var(--sapErrorBackground);box-shadow:inset 4px 0 0 var(--sapErrorBorderColor)}
.empty{color:var(--sapContent_LabelColor)}
@media (max-width:700px){
    .ui5-shellbar{padding:0 16px}
    .ui5-shell-subtitle{display:none}
    .ui5-page{padding:12px}
    .ui5-object-page-header{padding:16px}
    h1{font-size:22px}
    .ui5-toolbar,.toc-search{align-items:stretch}
    .ui5-button,.ui5-input{width:100%}
    .summary-metrics{width:100%;order:3}
}
"""


REPORT_JS = """
function setAllDetails(open){
    document.querySelectorAll('details.codeplug-table').forEach(function(item){item.open=open;});
}
function openAndJump(id){
    var item=document.getElementById(id);
    if(item){item.open=true;item.scrollIntoView({behavior:'smooth',block:'start'});}
}
function filterToc(){
    var term=document.getElementById('toc-search').value.toLowerCase();
    var shown=0;
    document.querySelectorAll('#toc-list li').forEach(function(item){
        var match=item.textContent.toLowerCase().indexOf(term)!==-1;
        item.style.display=match?'':'none';
        if(match){shown++;}
    });
    document.getElementById('toc-empty').style.display=shown?'none':'block';
}
function clearTocSearch(){
    document.getElementById('toc-search').value='';
    filterToc();
    document.getElementById('toc-search').focus();
}
function filterTable(id,status,trigger){
    var table=document.getElementById(id);
    if(!table){return;}
    var nextStatus=status;
    if(trigger&&trigger.classList.contains('summary-label-active')){nextStatus='all';}
    table.open=true;
    table.querySelectorAll('tbody tr').forEach(function(row){
        row.style.display=nextStatus==='all'||row.dataset.status===nextStatus?'':'none';
    });
    table.querySelectorAll('.summary-label').forEach(function(label){
        label.classList.toggle('summary-label-active', nextStatus!=='all'&&label.dataset.status===nextStatus);
    });
}
document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('[data-action="open-all"]').forEach(function(button){
        button.addEventListener('click', function(){setAllDetails(true);});
    });
    document.querySelectorAll('[data-action="close-all"]').forEach(function(button){
        button.addEventListener('click', function(){setAllDetails(false);});
    });
    document.querySelectorAll('[data-action="clear-toc-search"]').forEach(function(button){
        button.addEventListener('click', clearTocSearch);
    });
    var tocSearch=document.getElementById('toc-search');
    if(tocSearch){tocSearch.addEventListener('input', filterToc);}
    document.querySelectorAll('[data-jump]').forEach(function(link){
        link.addEventListener('click', function(event){
            event.preventDefault();
            openAndJump(link.dataset.jump);
        });
    });
    document.querySelectorAll('.summary-label').forEach(function(button){
        button.addEventListener('click', function(event){
            event.stopPropagation();
            filterTable(button.dataset.tableId, button.dataset.status, button);
        });
    });
    document.querySelectorAll('.top-link').forEach(function(link){
        link.addEventListener('click', function(event){event.stopPropagation();});
    });
});
"""


GUI_COLORS = {
    "background": "#f5f6f7",
    "shell": "#354a5f",
    "shell_text": "#ffffff",
    "panel": "#ffffff",
    "panel_header": "#f7f7f7",
    "border": "#d9d9d9",
    "text": "#1d2d3e",
    "label": "#556b82",
    "link": "#0a6ed1",
    "button_hover": "#ebf5fe",
}
