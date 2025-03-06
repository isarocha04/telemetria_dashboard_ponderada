import streamlit as st
import pandas as pd
import plotly.express as px
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

if not SUPABASE_URL or not SUPABASE_API_KEY:
    st.error("As variáveis SUPABASE_URL e SUPABASE_API_KEY não foram definidas no arquivo .env.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def load_logs_data(start_date=None, end_date=None):
    query = supabase.table("logs").select("*")
    if start_date and end_date:
        query = query.filter("created_at", "gte", str(start_date)).filter("created_at", "lte", str(end_date))
    response = query.execute()
    data = response.data
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def load_bronze_data(start_date=None, end_date=None):
    query = supabase.table("bronze").select("*")
    if start_date and end_date:
        query = query.filter("created_at", "gte", str(start_date)).filter("created_at", "lte", str(end_date))
    response = query.execute()
    data = response.data
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def parse_json_column(df, json_col="json"):
    def try_parse(text):
        try:
            return json.loads(text)
        except:
            return {}
    df["json_parsed"] = df[json_col].apply(try_parse)
    df["status_json"] = df["json_parsed"].apply(lambda x: x.get("STATUS"))
    df["loc_json"] = df["json_parsed"].apply(lambda x: x.get("LOC"))
    df["capture_time_json"] = df["json_parsed"].apply(lambda x: x.get("CAPTURE_TIME"))
    return df

st.set_page_config(page_title="Dashboard de Telemetria", layout="wide")

st.title("Dashboard de Telemetria do Data Lake")
st.write("""
Este dashboard apresenta métricas de uso e saúde do sistema, extraídas das tabelas **logs** e **bronze** (Data Lake) do Supabase.
""")

st.sidebar.header("Filtros de Data")
start_date_default = datetime.date(datetime.date.today().year, 1, 1)
end_date_default = datetime.date.today()
start_date = st.sidebar.date_input("Data Inicial", value=start_date_default)
end_date = st.sidebar.date_input("Data Final", value=end_date_default)

st.sidebar.write("---")
section = st.sidebar.radio("Selecione a Seção", ["Logs", "Bronze"])

if section == "Logs":
    st.subheader("Análise de Logs")
    df_logs = load_logs_data(start_date, end_date)
    if df_logs.empty:
        st.warning("Nenhum log encontrado no período selecionado.")
    else:
        if "created_at" in df_logs.columns:
            df_logs["created_at"] = pd.to_datetime(df_logs["created_at"])
        st.write("#### Amostra de Dados")
        st.dataframe(df_logs.head(10))
        total_logs = len(df_logs)
        st.metric("Total de Logs no Período", total_logs)
        if "created_at" in df_logs.columns:
            logs_time = df_logs.set_index("created_at").resample("T")["id"].count().reset_index()
            logs_time.columns = ["datetime", "count"]
            if not logs_time.empty:
                fig_time = px.line(
                    logs_time,
                    x="datetime",
                    y="count",
                    title="Evolução de Logs ao Longo do Tempo (por Minuto)"
                )
                fig_time.update_layout(xaxis=dict(tickformat='%d/%m %H:%M'))
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.write("Nenhum log encontrado após o agrupamento por minuto.")
        if "status" in df_logs.columns:
            status_count = df_logs.groupby("status")["id"].count().reset_index()
            status_count.columns = ["status", "count"]
            fig_status = px.bar(status_count, x="status", y="count", title="Logs por Status")
            st.plotly_chart(fig_status, use_container_width=True)
            if "level_type" in df_logs.columns:
                error_logs = len(df_logs[df_logs["level_type"] == "ERROR"])
            else:
                error_logs = len(df_logs[df_logs["status"] == "ERROR"])
            error_rate = (error_logs / total_logs) * 100 if total_logs > 0 else 0
            st.metric("Taxa de Erros", f"{error_rate:.2f}%")
        if "service" in df_logs.columns and "status" in df_logs.columns:
            service_status_count = df_logs.groupby(["service", "status"])["id"].count().reset_index()
            service_status_count.columns = ["service", "status", "count"]
            fig_service = px.bar(
                service_status_count,
                x="service",
                y="count",
                color="status",
                barmode="group",
                title="Logs por Serviço e Status"
            )
            st.plotly_chart(fig_service, use_container_width=True)
        if "level_type" in df_logs.columns:
            st.write("### Logs por Level Type")
            level_type_count = df_logs.groupby("level_type")["id"].count().reset_index()
            level_type_count.columns = ["level_type", "count"]
            fig_level_type = px.bar(
                level_type_count,
                x="level_type",
                y="count",
                title="Distribuição de Logs por Level Type"
            )
            st.plotly_chart(fig_level_type, use_container_width=True)
        if "service" in df_logs.columns:
            st.write("### Logs por Serviço")
            service_count = df_logs.groupby("service")["id"].count().reset_index()
            service_count.columns = ["service", "count"]
            fig_service_only = px.bar(
                service_count,
                x="service",
                y="count",
                title="Distribuição de Logs por Serviço"
            )
            st.plotly_chart(fig_service_only, use_container_width=True)

elif section == "Bronze":
    st.subheader("Análise da Tabela Bronze (Data Lake)")
    df_bronze = load_bronze_data(start_date, end_date)
    if df_bronze.empty:
        st.warning("Nenhum registro encontrado em 'bronze' no período selecionado.")
    else:
        date_col = None
        if "timestamp" in df_bronze.columns:
            df_bronze["timestamp"] = pd.to_datetime(df_bronze["timestamp"])
            date_col = "timestamp"
        elif "created_at" in df_bronze.columns:
            df_bronze["created_at"] = pd.to_datetime(df_bronze["created_at"])
            date_col = "created_at"
        st.write("#### Amostra de Dados (Brutos)")
        st.dataframe(df_bronze.head(10))
        if "json" in df_bronze.columns:
            df_bronze = parse_json_column(df_bronze, "json")
            st.write("#### Dados Após Parse do JSON")
            st.dataframe(df_bronze[["id", "status_json", "loc_json", "capture_time_json"]].head(10))
            status_count_bronze = df_bronze.groupby("status_json")["id"].count().reset_index()
            status_count_bronze.columns = ["status_json", "count"]
            fig_bronze_status = px.bar(
                status_count_bronze, 
                x="status_json", 
                y="count", 
                title="Registros em Bronze por STATUS (via JSON)"
            )
            st.plotly_chart(fig_bronze_status, use_container_width=True)
        if date_col:
            bronze_time = df_bronze.set_index(date_col).resample("T")["id"].count().reset_index()
            bronze_time.columns = ["datetime", "count"]
            if not bronze_time.empty:
                fig_bronze_time = px.line(
                    bronze_time,
                    x="datetime",
                    y="count",
                    title="Registros no Data Lake ao Longo do Tempo (por Minuto)"
                )
                fig_bronze_time.update_layout(xaxis=dict(tickformat='%d/%m %H:%M'))
                st.plotly_chart(fig_bronze_time, use_container_width=True)
            else:
                st.write("Nenhum registro encontrado após o agrupamento de datas.")
