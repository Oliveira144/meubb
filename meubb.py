import streamlit as st
import time

# Configuração da página
st.set_page_config(page_title="Sistema de Análise Preditiva - Cassino", layout="wide")

# Inicialização do estado
if 'history' not in st.session_state:
    st.session_state.history = []

if 'analysis' not in st.session_state:
    st.session_state.analysis = {
        'patterns': [],
        'riskLevel': 'low',
        'manipulation': 'none',
        'prediction': None,
        'confidence': 0,
        'recommendation': 'watch'
    }

# Função para adicionar resultado
def add_result(result):
    st.session_state.history.append({'result': result, 'timestamp': time.time()})
    analyze_data()

# Reset do histórico
def reset_history():
    st.session_state.history = []
    st.session_state.analysis = {
        'patterns': [],
        'riskLevel': 'low',
        'manipulation': 'none',
        'prediction': None,
        'confidence': 0,
        'recommendation': 'watch'
    }

# Funções de Análise
def analyze_data():
    data = st.session_state.history
    if len(data) < 3:
        return

    recent = data[-27:]  # últimas 3 linhas (27 resultados)
    patterns = detect_patterns(recent)
    riskLevel = assess_risk(recent)
    manipulation = detect_manipulation(recent)
    prediction = make_prediction(recent, patterns)

    st.session_state.analysis = {
        'patterns': patterns,
        'riskLevel': riskLevel,
        'manipulation': manipulation,
        'prediction': prediction['color'],
        'confidence': prediction['confidence'],
        'recommendation': get_recommendation(riskLevel, manipulation, patterns)
    }

def detect_patterns(data):
    patterns = []
    results = [d['result'] for d in data]

    # Streak
    current_streak = 1
    current_color = results[-1]
    for i in range(len(results)-2, -1, -1):
        if results[i] == current_color:
            current_streak += 1
        else:
            break

    if current_streak >= 2:
        patterns.append({
            'type': 'streak',
            'color': current_color,
            'length': current_streak,
            'description': f"{current_streak}x {get_color_name(current_color)} seguidas"
        })

    # Alternância
    alternating = True
    if len(results) >= 4:
        for i in range(-1, -4, -1):
            if i-1 >= -len(results) and results[i] == results[i-1]:
                alternating = False
                break
        if alternating:
            patterns.append({'type': 'alternating', 'description': 'Padrão alternado detectado'})

    # 2x2
    if len(results) >= 4:
        last4 = results[-4:]
        if last4[0] == last4[1] and last4[2] == last4[3] and last4[0] != last4[2]:
            patterns.append({'type': '2x2', 'description': 'Padrão 2x2 detectado'})

    return patterns

def assess_risk(data):
    results = [d['result'] for d in data]
    risk_score = 0

    # Streaks
    max_streak = 1
    current_streak = 1
    current_color = results[0]
    for i in range(1, len(results)):
        if results[i] == current_color:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
            current_color = results[i]

    if max_streak >= 5: risk_score += 40
    elif max_streak >= 4: risk_score += 25
    elif max_streak >= 3: risk_score += 10

    empate_streak = 0
    for r in reversed(results):
        if r == 'E': empate_streak += 1
        else: break
    if empate_streak >= 2: risk_score += 30

    if risk_score >= 50: return 'high'
    if risk_score >= 25: return 'medium'
    return 'low'

def detect_manipulation(data):
    results = [d['result'] for d in data]
    manipulation_score = 0

    empate_count = results.count('E')
    if empate_count / len(results) > 0.25: manipulation_score += 30

    if len(results) >= 6:
        recent6 = results[-6:]
        p1, p2 = recent6[:3], recent6[3:]
        if len(set(p1)) == 1 and len(set(p2)) == 1 and p1[0] != p2[0]:
            manipulation_score += 25

    if manipulation_score >= 40: return 'high'
    if manipulation_score >= 20: return 'medium'
    return 'low'

def make_prediction(data, patterns):
    results = [d['result'] for d in data]
    last_result = results[-1]
    prediction = {'color': None, 'confidence': 0}

    streak = next((p for p in patterns if p['type'] == 'streak'), None)
    if streak:
        if streak['length'] >= 3:
            other_colors = ['C', 'V']
            other_colors.remove(streak['color'])
            prediction['color'] = other_colors[0]
            prediction['confidence'] = min(85, 50 + streak['length'] * 8)
        else:
            prediction['color'] = streak['color']
            prediction['confidence'] = 65
    else:
        prediction['color'] = 'C' if last_result == 'V' else 'V'
        prediction['confidence'] = 55

    return prediction

def get_recommendation(risk, manipulation, patterns):
    if risk == 'high' or manipulation == 'high': return 'avoid'
    if patterns and risk == 'low': return 'bet'
    return 'watch'

def get_color_name(color):
    return {'C': 'Vermelho', 'V': 'Azul', 'E': 'Empate'}.get(color, '')

# Layout Streamlit
st.title("🎰 Sistema de Análise Preditiva - Cassino")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Inserir Resultados")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("🔴 Vermelho (C)", on_click=add_result, args=('C',))
    with c2:
        st.button("🔵 Azul (V)", on_click=add_result, args=('V',))
    with c3:
        st.button("🟡 Empate (E)", on_click=add_result, args=('E',))

    st.button("🔄 Resetar Histórico", on_click=reset_history)

    st.subheader("📊 Histórico (Mais recente à esquerda)")
    if st.session_state.history:
        max_results = 90
        recent_history = st.session_state.history[-max_results:][::-1]

        for i in range(0, len(recent_history), 9):
            row = recent_history[i:i+9]
            cols = st.columns(9)
            for idx, result in enumerate(row):
                color = result['result']
                bg = "#ff4d4d" if color == 'C' else "#4d79ff" if color == 'V' else "#ffeb3b"
                text_color = "black" if color == 'E' else "white"
                cols[idx].markdown(f"<div style='background:{bg};color:{text_color};text-align:center;padding:10px;border-radius:8px;font-weight:bold'>{color}</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum resultado inserido ainda.")

with col2:
    st.subheader("📈 Análise")
    analysis = st.session_state.analysis

    st.write("**Risco:**", analysis['riskLevel'])
    st.write("**Manipulação:**", analysis['manipulation'])

    st.write("**Previsão:**", analysis['prediction'] if analysis['prediction'] else "Aguardando...")
    st.write("**Confiança:**", f"{analysis['confidence']}%")
    st.write("**Recomendação:**", analysis['recommendation'])

    if analysis['patterns']:
        st.write("### Padrões Detectados:")
        for p in analysis['patterns']:
            st.write(f"- {p['description']}")
