import streamlit as st
import json
import uuid
from datetime import datetime
from pathlib import Path
from html import escape

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

if "visita" not in st.session_state:
    st.session_state.visita = new_state()

st.title("🏫 Visita Técnica | Infraestrutura Educacional")
st.caption("MVP flexível: preencha as seções em qualquer ordem, salve parcialmente e gere relatório.")

with st.sidebar:
    st.header("Navegação")
    page = st.radio("Escolha uma seção", ["Dados da Visita", "Perguntas da Gestão", "Matriz de Observação", "Priorização", "Síntese Executiva", "Registro Fotográfico", "Exportar / Carregar"], label_visibility="collapsed")
    st.divider()
    st.write(f"ID da visita: `{st.session_state.visita['id']}`")
    if st.button("Salvar agora", use_container_width=True):
        save_state()
    if st.button("Nova visita", use_container_width=True):
        st.session_state.visita = new_state()
        st.rerun()

v = st.session_state.visita

if page == "Dados da Visita":
    st.subheader("Dados da visita")
    fields = ["Unidade visitada", "Município", "Data e horário", "Analista responsável", "Gestor(a) local que acompanhou", "Segmentos atendidos / nº aproximado de estudantes"]
    for field in fields:
        v["dados_visita"][field] = st.text_input(field, value=v["dados_visita"].get(field, ""))

elif page == "Perguntas da Gestão":
    st.subheader("Perguntas iniciais para a gestão")
    for q in PERGUNTAS_GESTAO:
        v["perguntas_gestao"][q] = st.text_area(q, value=v["perguntas_gestao"].get(q, ""), height=90)

elif page == "Matriz de Observação":
    st.subheader("Matriz de observação geral da infraestrutura")
    filtro = st.selectbox("Filtrar por dimensão", ["Todas"] + sorted(set(d for d, _ in OBSERVACAO_ITENS)))
    for idx, (dim, item) in enumerate(OBSERVACAO_ITENS):
        if filtro != "Todas" and dim != filtro:
            continue
        key = str(idx)
        atual = v["observacoes"].get(key, {"dimensao": dim, "item": item, "nota": 3, "classificacao": "", "evidencias": ""})
        with st.expander(f"{dim} — {item[:80]}", expanded=False):
            c1, c2 = st.columns([1, 2])
            with c1:
                atual["nota"] = st.slider("Nota", 1, 5, int(atual.get("nota", 3)), key=f"nota_{key}")
                atual["classificacao"] = st.selectbox("Classificação", [""] + CLASSIFICACOES, index=([""] + CLASSIFICACOES).index(atual.get("classificacao", "")) if atual.get("classificacao", "") in ([""] + CLASSIFICACOES) else 0, key=f"class_{key}")
            with c2:
                atual["evidencias"] = st.text_area("Evidências / observações", value=atual.get("evidencias", ""), key=f"ev_{key}")
            v["observacoes"][key] = atual

elif page == "Priorização":
    st.subheader("Ficha de priorização das pequenas adequações")
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
    st.subheader("Síntese executiva e plano de ação pós-visita")
    fields = ["Síntese da visita", "Prioridade 1", "Prioridade 2", "Prioridade 3", "Demandas para manutenção/engenharia", "Ações possíveis em até 30 dias", "Responsável pelo retorno à unidade"]
    for field in fields:
        v["sintese"][field] = st.text_area(field, value=v["sintese"].get(field, ""), height=80)

elif page == "Registro Fotográfico":
    st.subheader("Registro fotográfico orientado")
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
    st.subheader("Exportar, carregar ou continuar visita")
    if st.button("Gerar relatório HTML"):
        save_state()
        html = render_report(v)
        out = REPORT_DIR / f"relatorio_visita_{v['id']}.html"
        out.write_text(html, encoding="utf-8")
        st.success("Relatório gerado.")
        st.download_button("Baixar relatório HTML", data=html, file_name=out.name, mime="text/html")
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
