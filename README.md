#  Dashboard de Telemetria do Data Lake e Data Warehouse

##  Visão Geral
Este projeto consiste na criação de um **Dashboard de Telemetria** para monitoramento de um **Data Lake** e um **Data Warehouse** utilizando **Streamlit** e **Supabase**. O objetivo é fornecer insights sobre o uso dos dados e a performance do sistema, garantindo que as informações sejam apresentadas de forma clara e eficaz.

##  Objetivos do Dashboard
- **Monitorar logs** do Data Warehouse para identificar padrões de uso e falhas.
- **Analisar os dados brutos** armazenados no Data Lake.
- **Exibir métricas relevantes**, como volume de registros, taxa de erro, distribuição por serviço e nível de severidade.
- **Permitir filtros temporais** para refinar a análise dentro de um intervalo de tempo selecionado pelo usuário.

##  Tecnologias Utilizadas
- **Streamlit**: Framework para criação do dashboard.
- **Supabase**: Plataforma de banco de dados (PostgreSQL) utilizada para armazenar os dados.
- **Plotly**: Biblioteca para visualização de dados.
- **Pandas**: Manipulação e análise dos dados.
- **Python dotenv**: Gerenciamento de variáveis de ambiente.


```

##  Configuração e Execução
### 1️ Configurar as Credenciais do Supabase
Crie um arquivo `.env` na raiz do projeto e adicione:
```
SUPABASE_URL="https://seu-supabase-url.supabase.co"
SUPABASE_API_KEY="sua-chave-api"
```

### 2 Instalar Dependências
Execute o comando abaixo para instalar as bibliotecas necessárias:
```
pip install -r requirements.txt
```

### 3️ Executar o Dashboard
```
streamlit run app.py
```
```
##  Métricas Monitoradas
O dashboard é dividido em duas seções: **Logs** e **Bronze (Data Lake)**.

###  Análise de Logs (Data Warehouse)
1. **Evolução de logs ao longo do tempo** (por minuto)
2. **Quantidade total de logs** no período selecionado
3. **Distribuição de logs por status** (SUCCESS, ERROR, etc.)
4. **Taxa de erro** (percentual de logs com status "ERROR")
5. **Logs por serviço e status** (identificação de falhas por serviço)
6. **Logs por nível de severidade (level_type)**
7. **Distribuição de logs por serviço**

###  Análise de Dados Brutos (Data Lake)
1. **Evolução do volume de registros** ao longo do tempo (por minuto)
2. **Distribuição dos registros por status (JSON)**
3. **Distribuição dos registros por localização (JSON)**
4. **Análise do campo "CAPTURE_TIME"** para verificar padrões

 **Padrões identificados:**
- A maioria dos logs foi gerada em um curto período de tempo, o que indica que os dados foram inseridos em lote.
- Os registros do Data Lake apresentam diferentes status e localizações, permitindo identificar padrões de captura dos dados.

 **Pontos de atenção:**
- A alta concentração de erros em determinados serviços pode indicar falhas sistêmicas.
- A distribuição dos logs por nível de severidade pode ser usada para priorizar ações corretivas.
- A visualização do volume de dados no Data Lake ajuda a prever necessidade de armazenamento.


Este dashboard fornece uma visão detalhada da telemetria do sistema, auxiliando na identificação de falhas e melhorias na governança dos dados. A implementação permite monitoramento contínuo e suporte à tomada de decisões baseadas em dados.

