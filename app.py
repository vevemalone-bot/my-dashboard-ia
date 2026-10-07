import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import psycopg2  # Substitua pelo conector do seu banco de dados
import time

# 1. Configurações Iniciais da Página
st.set_page_config(layout="wide", page_title="Dashboard Real-Time com IA")
st.title("🔄 Dashboard de Alta Performance com IA Integrada")

# Inicializa o cliente da IA usando os segredos seguros do Streamlit
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2. Função para Conectar e Buscar Dados do Banco de Dados
# O recurso 'ttl=1' diz ao Streamlit para limpar o cache a cada 1 segundo, buscando dados novos
@st.cache_data(ttl=1)
def buscar_dados_do_banco():
    try:
        # Puxa as credenciais de acesso salvas nos Secrets do Streamlit
        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"]
        )
        # Exemplo de Query: Puxa as últimas vendas registradas no sistema
        query = "SELECT mes, vendas, lucro FROM tabela_vendas ORDER BY id DESC LIMIT 100;"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        # Caso o banco falhe, avisa na tela de forma amigável
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return pd.DataFrame()

# 3. Executa a busca dos dados atuais
df_atual = buscar_dados_do_banco()

# Se o banco estiver vazio ou falhar, o app não quebra
if not df_atual.empty:
    
    # 4. Criação do Layout em Colunas
    col1, col2 = st.columns([2, 1])  # Coluna 1 é mais larga para os gráficos

    with col1:
        st.subheader("📈 Monitoramento em Tempo Real")
        
        # Cria o gráfico interativo com os dados mais recentes do banco
        fig = px.line(df_atual, x='mes', y='vendas', title="Volume de Vendas Atualizado")
        st.plotly_chart(fig, use_container_width=True)
        
        # Mostra a hora da última atualização na tela
        st.caption(f"Última sincronização com o banco de dados: {time.strftime('%H:%M:%S')}")

    with col2:
        st.subheader("💬 Assistente de IA de Dados")
        
        # Mantém o histórico do chat ativo
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Estou conectado ao seu banco de dados. Pode me perguntar sobre as métricas mais recentes!"}]
            
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
            
        # Caixa de chat para o usuário digitar
        if prompt := st.chat_input("Ex: Qual foi a última oscilação importante no lucro?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            # Converte os dados mais recentes em texto para a IA analisar
            contexto_dados = df_atual.to_string(index=False)
            
            resposta_ia = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Você é um analista de dados sênior conectado ao banco de dados da empresa em tempo real. Responda com base nestes dados exatos que acabaram de entrar:\n{contexto_dados}"},
                    *st.session_state.messages
                ]
            )
            
            resposta = resposta_ia.choices.message.content
            st.session_state.messages.append({"role": "assistant", "content": resposta})
            st.chat_message("assistant").write(resposta)

# 5. O Mecanismo de Loop: Força o app a recarregar a cada 1 segundo
time.sleep(1)
st.rerun()
