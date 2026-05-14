import streamlit as st
import json
import uuid
from datetime import datetime
from pathlib import Path
from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "dados"
PHOTO_DIR = DATA_DIR / "fotos"
REPORT_DIR = DATA_DIR / "relatorios"
for p in [DATA_DIR, PHOTO_DIR, REPORT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Visita Técnica", page_icon="🏫", layout="wide")

OBSERVACAO_ITENS = [
    ("Conservação", "Salas de aula: pintura, piso, paredes, portas, janelas, quadros e mobiliário."),
    ("Conservação", "Banheiros: sanitários, torneiras, descargas, revestimentos, ventilação, odor e condições de uso."),
    ("Conservação", "Cozinha/refeitório: organização, conservação, fluxo, higienização, mobiliário e conforto dos estudantes."),
    ("Conservação", "Áreas administrativas e atendimento: organização, conservação, privacidade e acolhimento."),
    ("Risco aparente", "Estrutura: fissuras, rachaduras, deformações, piso cedendo, desplacamentos ou sinais incomuns."),
    ("Risco aparente", "Cobertura/telhado: goteiras, infiltrações, telhas soltas, mofo, manchas ou risco de desprendimento."),
    ("Risco aparente", "Instalações elétricas: fiação exposta, tomadas danificadas, sobrecarga, quadros sem proteção ou falta de pontos."),
    ("Risco aparente", "Instalações hidráulicas: vazamentos, infiltrações, baixa pressão, tubulações expostas ou falhas de abastecimento."),
    ("Segurança e circulação", "Escadas, rampas, corrimãos, pisos escorregadios/irregulares, rotas livres e acessos."),
    ("Conforto ambiental", "Iluminação natural e artificial em salas, corredores, banheiros e áreas externas."),
    ("Conforto ambiental", "Ventilação, conforto térmico, incidência de calor e possibilidade de circulação de ar."),
    ("Conforto ambiental", "Ruído interno/externo que interfere nas aulas, concentração, acolhimento ou convivência."),
    ("Infraestrutura pedagógica", "Recursos tecnológicos: computadores, projetores, telas, caixas de som, internet e equipamentos multimídia."),
    ("Infraestrutura pedagógica", "Biblioteca/sala de leitura: acesso, organização, conforto, acervo, cantos de leitura e uso pelos estudantes."),
    ("Infraestrutura pedagógica", "Ambientes de experimentação, arte, tecnologia, atendimento individualizado, acolhimento e convivência."),
    ("Mobiliário", "Carteiras, mesas, cadeiras, armários, estantes e mobiliários flexíveis: quantidade, estado e adequação ao uso."),
    ("Ambiência pedagógica", "Murais, exposição de trabalhos dos alunos, registros de projetos, comunicação visual e valorização da produção estudantil."),
    ("Ambiência pedagógica", "Uso de cores, organização visual, sensação de acolhimento, pertencimento, identidade e cuidado com os ambientes."),
    ("Limpeza e higiene", "Limpeza de salas, banheiros, corredores, pátios, refeitório, janelas, mobiliários e áreas de uso comum."),
    ("Resíduos", "Lixeiras, coleta, organização de resíduos, armazenamento e percepção de cuidado ambiental."),
    ("Paisagismo e áreas externas", "Jardins, sombra, áreas verdes, pátio, bancos, espaços de permanência, circulação externa e potencial pedagógico."),
    ("Espaços esportivos", "Quadra ou espaço esportivo: piso, cobertura, iluminação, traves/tabelas, arquibancada e segurança de uso."),
]

PERGUNTAS_GESTAO = [
    "Quais ambientes são mais utilizados pedagogicamente e quais estão subutilizados?",
    "Quais problemas de infraestrutura mais impactam a rotina de professores e estudantes?",
    "Há queixas recorrentes sobre calor, iluminação, ruído, mobiliário, internet, limpeza ou circulação?",
    "Quais ações já foram solicitadas e ainda não executadas?",
    "Há espaços de acolhimento, convivência, leitura, experimentação, arte, tecnologia ou atendimento individualizado?",
    "Quais adequações poderiam melhorar a aprendizagem já no próximo mês?",
    "Há algum risco aparente que exija isolamento, interdição ou encaminhamento técnico imediato?",
]

CATEGORIAS_FOTO = [
    "Fachada e acesso principal",
    "Salas de aula representativas por segmento",
    "Banheiros de estudantes e servidores",
    "Pátio, refeitório e áreas de convivência",
    "Biblioteca/sala de leitura",
    "Ambientes de tecnologia, arte, experimentação ou atendimento individualizado",
    "Quadra ou espaço esportivo",
    "Pontos de risco aparente",
    "Oportunidades de impacto pedagógico imediato",
]

CLASSIFICACOES = [
    "A. Pequena adequação sem obra",
    "B. Pequena adequação de baixo custo",
    "C. Pequena adequação com impacto pedagógico imediato",
    "D. Encaminhamento técnico",
]


def new_state():
    return {
        "id": str(uuid.uuid4())[:8],
        "dados_visita": {},
        "perguntas_gestao": {},
        "observacoes": {},
        "priorizacoes": [],
        "sintese": {},
        "fotos": [],
        "criado_em": datetime.now().isoformat(timespec="seconds"),
        "atualizado_em": datetime.now().isoformat(timespec="seconds"),
    }


def save_state():
    st.session_state.visita["atualizado_em"] = datetime.now().isoformat(timespec="seconds")
    path = DATA_DIR / f"visita_{st.session_state.visita['id']}.json"
    path.write_text(json.dumps(st.session_state.visita, ensure_ascii=False, indent=2), encoding="utf-8")
    st.toast("Dados salvos.")


def load_visit(path):
    st.session_state.visita = json.loads(Path(path).read_text(encoding="utf-8"))


def h(x):
    return escape(str(x or ""))


def render_report(data):
    obs_rows = "".join(
        f"<tr><td>{h(v.get('dimensao'))}</td><td>{h(v.get('item'))}</td><td>{h(v.get('nota'))}</td><td>{h(v.get('classificacao'))}</td><td>{h(v.get('evidencias'))}</td></tr>"
        for v in data.get("observacoes", {}).values()
    )
    pri_rows = "".join(
        f"<tr><td>{h(p.get('ambiente'))}</td><td>{h(p.get('problema'))}</td><td>{h(p.get('adequacao'))}</td><td>{h(p.get('classificacao'))}</td><td>{h(p.get('impacto'))}</td><td>{h(p.get('prazo'))}</td></tr>"
        for p in data.get("priorizacoes", [])
    )
    perguntas = "".join(f"<h3>{h(k)}</h3><p>{h(v)}</p>" for k, v in data.get("perguntas_gestao", {}).items() if v)
    fotos = "".join(f"<li>{h(f.get('categoria'))}: {h(f.get('arquivo'))} — {h(f.get('observacao'))}</li>" for f in data.get("fotos", []))
    dados = data.get("dados_visita", {})
    sint = data.get("sintese", {})
    return f"""
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Relatório de Visita Técnica</title>
<style>body{{font-family:Arial,sans-serif;margin:32px;line-height:1.45}} table{{border-collapse:collapse;width:100%;margin:12px 0}}td,th{{border:1px solid #999;padding:6px;vertical-align:top}} h1,h2{{color:#333}}</style></head><body>
<h1>Relatório de Visita Técnica | Infraestrutura Educacional</h1>
<h2>Dados da visita</h2>
<p><b>Unidade:</b> {h(dados.get('Unidade visitada'))}<br><b>Município:</b> {h(dados.get('Município'))}<br><b>Data e horário:</b> {h(dados.get('Data e horário'))}<br><b>Analista:</b> {h(dados.get('Analista responsável'))}<br><b>Gestor(a) local:</b> {h(dados.get('Gestor(a) local que acompanhou'))}<br><b>Segmentos / estudantes:</b> {h(dados.get('Segmentos atendidos / nº aproximado de estudantes'))}</p>
<h2>Perguntas iniciais à gestão</h2>{perguntas}
<h2>Matriz de observação</h2><table><tr><th>Dimensão</th><th>Item</th><th>Nota</th><th>Classificação</th><th>Evidências</th></tr>{obs_rows}</table>
<h2>Priorização das adequações</h2><table><tr><th>Ambiente</th><th>Problema/oportunidade</th><th>Adequação proposta</th><th>Classificação</th><th>Impacto pedagógico</th><th>Prazo/encaminhamento</th></tr>{pri_rows}</table>
<h2>Síntese executiva</h2>
<p><b>Síntese:</b> {h(sint.get('Síntese da visita'))}</p><p><b>Prioridade 1:</b> {h(sint.get('Prioridade 1'))}<br><b>Prioridade 2:</b> {h(sint.get('Prioridade 2'))}<br><b>Prioridade 3:</b> {h(sint.get('Prioridade 3'))}</p>
<p><b>Demandas para manutenção/engenharia:</b> {h(sint.get('Demandas para manutenção/engenharia'))}<br><b>Ações possíveis em até 30 dias:</b> {h(sint.get('Ações possíveis em até 30 dias'))}<br><b>Responsável pelo retorno:</b> {h(sint.get('Responsável pelo retorno à unidade'))}</p>
<h2>Registro fotográfico</h2><ul>{fotos}</ul>
<p><small>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}.</small></p>

</body></html>"""


def _safe_text(value):
    return str(value or "").replace("\n", "<br/>")


def _p(value, style):
    return Paragraph(_safe_text(value), style)


def generate_pdf(data):
    """Gera um relatório em PDF em memória para download no Streamlit."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Relatório de Visita Técnica",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, fontSize=16, leading=20, spaceAfter=12))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=12, leading=15, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontSize=7, leading=9))

    story = []
    dados = data.get("dados_visita", {})
    sint = data.get("sintese", {})

    story.append(Paragraph("Relatório de Visita Técnica", styles["TitleCenter"]))
    story.append(Paragraph("Infraestrutura Educacional", styles["Heading3"]))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph("Dados da visita", styles["Section"]))
    dados_table = [
        [_p("Unidade visitada", styles["Cell"]), _p(dados.get("Unidade visitada"), styles["Cell"])],
        [_p("Município", styles["Cell"]), _p(dados.get("Município"), styles["Cell"])],
        [_p("Data e horário", styles["Cell"]), _p(dados.get("Data e horário"), styles["Cell"])],
        [_p("Analista responsável", styles["Cell"]), _p(dados.get("Analista responsável"), styles["Cell"])],
        [_p("Gestor(a) local que acompanhou", styles["Cell"]), _p(dados.get("Gestor(a) local que acompanhou"), styles["Cell"])],
        [_p("Segmentos / estudantes", styles["Cell"]), _p(dados.get("Segmentos atendidos / nº aproximado de estudantes"), styles["Cell"])],
    ]
    t = Table(dados_table, colWidths=[5 * cm, 12 * cm], repeatRows=0)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    story.append(Paragraph("Perguntas iniciais à gestão", styles["Section"]))
    perguntas = data.get("perguntas_gestao", {})
    if any(perguntas.values()):
        for pergunta, resposta in perguntas.items():
            if resposta:
                story.append(Paragraph(f"<b>{_safe_text(pergunta)}</b>", styles["BodyText"]))
                story.append(Paragraph(_safe_text(resposta), styles["BodyText"]))
                story.append(Spacer(1, 0.15 * cm))
    else:
        story.append(Paragraph("Sem registros.", styles["BodyText"]))

    story.append(Paragraph("Matriz de observação", styles["Section"]))
    obs_data = [[_p("Dimensão", styles["Cell"]), _p("Item", styles["Cell"]), _p("Nota", styles["Cell"]), _p("Classificação", styles["Cell"]), _p("Evidências", styles["Cell"])] ]
    for item in data.get("observacoes", {}).values():
        if item.get("evidencias") or item.get("classificacao") or item.get("nota"):
            obs_data.append([
                _p(item.get("dimensao"), styles["Cell"]),
                _p(item.get("item"), styles["Cell"]),
                _p(item.get("nota"), styles["Cell"]),
                _p(item.get("classificacao"), styles["Cell"]),
                _p(item.get("evidencias"), styles["Cell"]),
            ])
    if len(obs_data) == 1:
        story.append(Paragraph("Sem registros.", styles["BodyText"]))
    else:
        t = Table(obs_data, colWidths=[2.7 * cm, 5.2 * cm, 1.1 * cm, 3.2 * cm, 4.8 * cm], repeatRows=1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        story.append(t)

    story.append(Paragraph("Priorização das adequações", styles["Section"]))
    pri_data = [[_p("Ambiente", styles["Cell"]), _p("Problema/oportunidade", styles["Cell"]), _p("Adequação proposta", styles["Cell"]), _p("Classificação", styles["Cell"]), _p("Impacto", styles["Cell"]), _p("Prazo", styles["Cell"])] ]
    for p in data.get("priorizacoes", []):
        if any(p.values()):
            pri_data.append([
                _p(p.get("ambiente"), styles["Cell"]),
                _p(p.get("problema"), styles["Cell"]),
                _p(p.get("adequacao"), styles["Cell"]),
                _p(p.get("classificacao"), styles["Cell"]),
                _p(p.get("impacto"), styles["Cell"]),
                _p(p.get("prazo"), styles["Cell"]),
            ])
    if len(pri_data) == 1:
        story.append(Paragraph("Sem registros.", styles["BodyText"]))
    else:
        t = Table(pri_data, colWidths=[2.4 * cm, 3.2 * cm, 3.2 * cm, 2.7 * cm, 3.2 * cm, 2.3 * cm], repeatRows=1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)

    story.append(Paragraph("Síntese executiva", styles["Section"]))
    for campo in ["Síntese da visita", "Prioridade 1", "Prioridade 2", "Prioridade 3", "Demandas para manutenção/engenharia", "Ações possíveis em até 30 dias", "Responsável pelo retorno à unidade"]:
        if sint.get(campo):
            story.append(Paragraph(f"<b>{campo}:</b> {_safe_text(sint.get(campo))}", styles["BodyText"]))
            story.append(Spacer(1, 0.1 * cm))

    story.append(Paragraph("Registro fotográfico", styles["Section"]))
    fotos = data.get("fotos", [])
    if not fotos:
        story.append(Paragraph("Sem fotos registradas.", styles["BodyText"]))
    else:
        for foto in fotos:
            story.append(Paragraph(f"<b>{_safe_text(foto.get('categoria'))}</b> — {_safe_text(foto.get('observacao'))}", styles["BodyText"]))
            img_path = PHOTO_DIR / str(foto.get("arquivo", ""))
            if img_path.exists():
                try:
                    story.append(Image(str(img_path), width=8 * cm, height=6 * cm, kind="proportional"))
                except Exception:
                    story.append(Paragraph(f"Arquivo: {_safe_text(foto.get('arquivo'))}", styles["Small"]))
            else:
                story.append(Paragraph(f"Arquivo: {_safe_text(foto.get('arquivo'))}", styles["Small"]))
            story.append(Spacer(1, 0.2 * cm))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}.", styles["Small"]))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


CUSTOM_CSS = """
<style>
:root {
    --primary: #243B53;
    --secondary: #486581;
    --accent: #2F80ED;
    --bg-soft: #F4F7FB;
    --card: #FFFFFF;
    --text: #1F2933;
    --muted: #6B7280;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1180px;
}

.hero {
    background: linear-gradient(135deg, #243B53 0%, #486581 58%, #2F80ED 100%);
    border-radius: 24px;
    padding: 28px 32px;
    margin-bottom: 22px;
    color: white;
    box-shadow: 0 12px 32px rgba(36, 59, 83, 0.18);
}
.hero h1 {
    margin: 0;
    font-size: 2rem;
    letter-spacing: -0.03em;
}
.hero p {
    margin-top: 8px;
    font-size: 1rem;
    opacity: 0.92;
}
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}
.badge {
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 0.85rem;
}
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    min-height: 96px;
}
.metric-card .label {
    color: #6B7280;
    font-size: 0.85rem;
    margin-bottom: 6px;
}
.metric-card .value {
    color: #111827;
    font-size: 1.45rem;
    font-weight: 700;
}
.section-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 20px;
    padding: 22px;
    margin: 8px 0 20px 0;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
}
.section-title {
    font-size: 1.35rem;
    font-weight: 750;
    color: #1F2937;
    margin-bottom: 6px;
}
.section-subtitle {
    color: #6B7280;
    margin-bottom: 16px;
}
.small-note {
    color: #6B7280;
    font-size: 0.88rem;
}
[data-testid="stSidebar"] {
    background: #F8FAFC;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #243B53;
}
.stButton>button {
    border-radius: 12px;
    min-height: 42px;
    font-weight: 650;
}
.stDownloadButton>button {
    border-radius: 12px;
    min-height: 42px;
    font-weight: 650;
}
div[data-testid="stExpander"] {
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.035);
}
</style>
"""

SECTION_ICONS = {
    "Início": "🏠",
    "Dados da Visita": "📝",
    "Perguntas da Gestão": "💬",
    "Matriz de Observação": "🔎",
    "Priorização": "🛠️",
    "Síntese Executiva": "📌",
    "Registro Fotográfico": "📷",
    "Exportar / Carregar": "📄",
}


def count_filled_values(obj):
    if isinstance(obj, dict):
        return sum(count_filled_values(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_filled_values(v) for v in obj)
    return 1 if str(obj or "").strip() else 0


def completion_stats(v):
    dados_ok = count_filled_values(v.get("dados_visita", {}))
    perguntas_ok = count_filled_values(v.get("perguntas_gestao", {}))
    obs_ok = len([x for x in v.get("observacoes", {}).values() if x.get("evidencias") or x.get("classificacao") or x.get("nota")])
    prio_ok = len([x for x in v.get("priorizacoes", []) if any(str(y or '').strip() for y in x.values())])
    sintese_ok = count_filled_values(v.get("sintese", {}))
    fotos_ok = len(v.get("fotos", []))
    total = min(100, round((dados_ok/6)*15 + (perguntas_ok/7)*15 + (obs_ok/len(OBSERVACAO_ITENS))*30 + min(prio_ok,3)/3*15 + (sintese_ok/7)*15 + min(fotos_ok,5)/5*10))
    return total, obs_ok, prio_ok, fotos_ok


def render_hero(v):
    progresso, obs_ok, prio_ok, fotos_ok = completion_stats(v)
    unidade = v.get("dados_visita", {}).get("Unidade visitada") or "Visita técnica"
    municipio = v.get("dados_visita", {}).get("Município") or "Município não informado"
    st.markdown(f"""
    <div class="hero">
        <h1>Visita Técnica | Infraestrutura Educacional</h1>
        <p>{h(unidade)} · {h(municipio)}</p>
        <div class="badge-row">
            <span class="badge">ID: {h(v.get('id'))}</span>
            <span class="badge">Progresso estimado: {progresso}%</span>
            <span class="badge">Observações: {obs_ok}</span>
            <span class="badge">Fotos: {fotos_ok}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
      <div class="label">{h(label)}</div>
      <div class="value">{h(value)}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, subtitle=""):
    st.markdown(f"""
    <div class="section-card">
      <div class="section-title">{h(title)}</div>
      <div class="section-subtitle">{h(subtitle)}</div>
    </div>
    """, unsafe_allow_html=True)

if "visita" not in st.session_state:
    st.session_state.visita = new_state()

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Visita Técnica")
    st.caption("Protótipo flexível para registro em campo")
    opcoes = ["Início", "Dados da Visita", "Perguntas da Gestão", "Matriz de Observação", "Priorização", "Síntese Executiva", "Registro Fotográfico", "Exportar / Carregar"]
    page = st.radio("Escolha uma seção", opcoes, format_func=lambda x: f"{SECTION_ICONS.get(x, '')} {x}", label_visibility="collapsed")
    st.divider()
    st.markdown(f"**ID da visita:** `{st.session_state.visita['id']}`")
    progresso, obs_ok, prio_ok, fotos_ok = completion_stats(st.session_state.visita)
    st.progress(progresso / 100, text=f"Progresso estimado: {progresso}%")
    if st.button("💾 Salvar agora", use_container_width=True):
        save_state()
    if st.button("➕ Nova visita", use_container_width=True):
        st.session_state.visita = new_state()
        st.rerun()
    st.divider()
    st.caption("Dica: salve após concluir cada seção.")

v = st.session_state.visita
render_hero(v)

if page == "Início":
    progresso, obs_ok, prio_ok, fotos_ok = completion_stats(v)
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Progresso", f"{progresso}%")
    with c2: metric_card("Itens observados", obs_ok)
    with c3: metric_card("Priorizações", prio_ok)
    with c4: metric_card("Fotos", fotos_ok)
    st.markdown("### Como usar")
    st.info("Preencha as seções na ordem que preferir. Durante a visita, use o menu lateral para alternar entre dados, observações, fotos e síntese.")
    st.markdown("### Recomendações rápidas")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""- Use **Salvar agora** após cada bloco importante.
- Gere o **PDF** antes de encerrar a visita.
- Registre fotos com observações curtas.""")
    with c2:
        st.markdown("""- Use a matriz para notas de 1 a 5.
- Registre prioridades claras.
- Use a síntese para consolidar encaminhamentos.""")

elif page == "Dados da Visita":
    section_header("Dados da visita", "Identificação da unidade, responsável e contexto da visita.")
    fields = ["Unidade visitada", "Município", "Data e horário", "Analista responsável", "Gestor(a) local que acompanhou", "Segmentos atendidos / nº aproximado de estudantes"]
    for field in fields:
        v["dados_visita"][field] = st.text_input(field, value=v["dados_visita"].get(field, ""))

elif page == "Perguntas da Gestão":
    section_header("Perguntas iniciais para a gestão", "Use este espaço para registrar percepções da equipe local.")
    for q in PERGUNTAS_GESTAO:
        v["perguntas_gestao"][q] = st.text_area(q, value=v["perguntas_gestao"].get(q, ""), height=90)

elif page == "Matriz de Observação":
    section_header("Matriz de observação geral da infraestrutura", "Avalie os ambientes por dimensão, nota, evidências e classificação da adequação.")
    filtro = st.selectbox("Filtrar por dimensão", ["Todas"] + sorted(set(d for d, _ in OBSERVACAO_ITENS)))
    for idx, (dim, item) in enumerate(OBSERVACAO_ITENS):
        if filtro != "Todas" and dim != filtro:
            continue
        key = str(idx)
        atual = v["observacoes"].get(key, {"dimensao": dim, "item": item, "nota": 3, "classificacao": "", "evidencias": ""})
        with st.expander(f"{SECTION_ICONS.get("Matriz de Observação")} {dim} — {item[:80]}", expanded=False):
            c1, c2 = st.columns([1, 2])
            with c1:
                atual["nota"] = st.slider("Nota", 1, 5, int(atual.get("nota", 3)), key=f"nota_{key}")
                atual["classificacao"] = st.selectbox("Classificação", [""] + CLASSIFICACOES, index=([""] + CLASSIFICACOES).index(atual.get("classificacao", "")) if atual.get("classificacao", "") in ([""] + CLASSIFICACOES) else 0, key=f"class_{key}")
            with c2:
                atual["evidencias"] = st.text_area("Evidências / observações", value=atual.get("evidencias", ""), key=f"ev_{key}")
            v["observacoes"][key] = atual

elif page == "Priorização":
    section_header("Priorização das pequenas adequações", "Registre os problemas ou oportunidades com maior potencial de impacto.")
    qtd = st.number_input("Quantidade de adequações a registrar", min_value=1, max_value=20, value=max(1, len(v["priorizacoes"])), step=1)
    while len(v["priorizacoes"]) < qtd:
        v["priorizacoes"].append({})
    v["priorizacoes"] = v["priorizacoes"][:qtd]
    for i, p in enumerate(v["priorizacoes"]):
        with st.expander(f"Adequação {i+1}", expanded=True):
            p["ambiente"] = st.text_input("Ambiente", value=p.get("ambiente", ""), key=f"amb_{i}")
            p["problema"] = st.text_area("Problema/oportunidade", value=p.get("problema", ""), key=f"prob_{i}")
            p["adequacao"] = st.text_area("Adequação proposta", value=p.get("adequacao", ""), key=f"adeq_{i}")
            p["classificacao"] = st.selectbox("Classificação", [""] + CLASSIFICACOES, key=f"pri_class_{i}")
            p["impacto"] = st.text_area("Impacto pedagógico esperado", value=p.get("impacto", ""), key=f"imp_{i}")
            p["prazo"] = st.text_input("Prazo/encaminhamento", value=p.get("prazo", ""), key=f"prazo_{i}")

elif page == "Síntese Executiva":
    section_header("Síntese executiva e plano de ação", "Consolide prioridades, encaminhamentos e ações possíveis em curto prazo.")
    fields = ["Síntese da visita", "Prioridade 1", "Prioridade 2", "Prioridade 3", "Demandas para manutenção/engenharia", "Ações possíveis em até 30 dias", "Responsável pelo retorno à unidade"]
    for field in fields:
        v["sintese"][field] = st.text_area(field, value=v["sintese"].get(field, ""), height=80)

elif page == "Registro Fotográfico":
    section_header("Registro fotográfico orientado", "Inclua imagens por categoria para apoiar evidências e encaminhamentos.")
    categoria = st.selectbox("Categoria da foto", CATEGORIAS_FOTO)
    obs = st.text_input("Observação sobre a foto")
    uploaded = st.file_uploader("Enviar foto", type=["png", "jpg", "jpeg"])
    if uploaded and st.button("Adicionar foto"):
        filename = f"{v['id']}_{uuid.uuid4().hex[:8]}_{uploaded.name}"
        (PHOTO_DIR / filename).write_bytes(uploaded.getbuffer())
        v["fotos"].append({"categoria": categoria, "observacao": obs, "arquivo": filename})
        save_state()
    st.write("Fotos adicionadas:")
    for foto in v["fotos"]:
        st.write(f"- {foto['categoria']} — {foto['arquivo']} — {foto.get('observacao','')}")

elif page == "Exportar / Carregar":
    section_header("Exportar, carregar ou continuar visita", "Gere o PDF, salve os dados ou retome visitas salvas nesta instalação.")
    if st.button("Gerar relatório PDF"):
        save_state()
        pdf = generate_pdf(v)
        out = REPORT_DIR / f"relatorio_visita_{v['id']}.pdf"
        out.write_bytes(pdf)
        st.success("Relatório PDF gerado.")
        st.download_button("Baixar relatório PDF", data=pdf, file_name=out.name, mime="application/pdf")
    st.divider()
    st.write("Visitas salvas nesta instalação:")
    saved = sorted(DATA_DIR.glob("visita_*.json"), reverse=True)
    if saved:
        choice = st.selectbox("Escolha uma visita para carregar", [str(p) for p in saved])
        if st.button("Carregar visita selecionada"):
            load_visit(choice)
            st.rerun()
    else:
        st.info("Ainda não há visitas salvas.")

st.divider()
st.caption("Dica: use o botão 'Salvar agora' no menu lateral após preencher cada seção.")
