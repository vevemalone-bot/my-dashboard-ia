import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# 1. Configuração da Página e da IA
st.set_page_config(layout="wide", page_title="Dashboard Inteligente")
st.title("📊 Dashboard Interativo com IA Integrada")

# Insira sua chave da OpenAI aqui (ou use st.secrets para produção)
client = OpenAI(api_key="SUA_CHAVE_API_AQUI")

# 2. Base de Dados Simulação (Pode ser carregada de um CSV/Excel)
data = {
    'Mês': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho'],
    'Vendas': [45000, 52000, 49000, 61000, 58000, 71000],
    'Lucro': [12000, 15000, 11000, 19000, 17000, 24000]
}
df = pd.DataFrame(data)

# 3. Divisão do Layout em duas colunas (Gráficos vs Chat da IA)
col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("📈 Indicadores e Métricas")
    # Filtro Interativo
    metricas = st.multiselect("Selecione as Métricas:", ['Vendas', 'Lucro'], default=['Vendas', 'Lucro'])
    
    # Gráfico Interativo Plotly
    fig = px.line(df, x='Mês', y=metricas, title="Desempenho Semestral", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💬 Converse com seus Dados")
    
    # Inicializa o histórico do chat na tela
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Olá! Pergunte-me qualquer coisa sobre o desempenho das vendas."}]
        
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    # Input do Usuário
    if prompt := st.chat_input("Ex: Qual foi o mês com maior lucro?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Engenharia de Prompt: Passamos o contexto dos dados para a IA responder com precisão
        contexto_dados = df.to_string(index=False)
        resposta_ia = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Você é um analista de dados de negócios. Responda de forma curta e objetiva com base nestes dados atuais:\n{contexto_dados}"},
                *st.session_state.messages
            ]
        )
        
        resposta = resposta_ia.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(resposta)
