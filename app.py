import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# URL of the published Google Sheet in CSV format
sheet_url = 'https://omansomsco-my.sharepoint.com/:x:/g/personal/data_analyst1_somsco_com/EfxAba6oBHdNoHuRfhNZShMB7f2sd3_jWGEezSPAHPIy3g?e=oYo5nG'

@st.cache_data(ttl=60)
def load_data():
    # Load the data into a DataFrame
    df = pd.read_csv(sheet_url)

    # Convert date columns to datetime
    df['Expected Start'] = pd.to_datetime(df['Expected Start'], format='%d-%b-%Y', errors='coerce')
    df['Expected End'] = pd.to_datetime(df['Expected End'], format='%d-%b-%Y', errors='coerce')
    df['Actual Start'] = pd.to_datetime(df['Actual Start'], format='%d-%b-%Y', errors='coerce')
    df['Actual End'] = pd.to_datetime(df['Actual End'], errors='coerce')

    # Update Actual End dates
    today = pd.Timestamp.now().normalize()
    df['Actual End'] = df['Actual End'].fillna(today)
    df.loc[df['Actual End'] > today, 'Actual End'] = today

    return df

df = load_data()

# Filter data to include only rows with non-null Expected Start, Expected End, and Actual Start
df_filtered = df.dropna(subset=['Expected Start', 'Expected End'])
df_filtered = df_filtered[~df_filtered['Actual Start'].isna()]

# Create traces for expected and actual timelines
fig = go.Figure()

# Plot Expected timelines and Actual timelines
for i, row in df_filtered.iterrows():
    if pd.notna(row['Expected Start']) and pd.notna(row['Expected End']):
        fig.add_trace(go.Scatter(
            x=[row['Expected Start'], row['Expected End']],
            y=[row['job_code'], row['job_code']],
            mode='lines+markers',
            line=dict(color='orange', width=15),
            name='Expected',
            hoverinfo='text',
            text=f"Expected: {row['Expected Start'].strftime('%b %d')} to {row['Expected End'].strftime('%b %d')}",
        ))

    if pd.notna(row['Actual Start']):
        fig.add_trace(go.Scatter(
            x=[row['Actual Start'], row['Actual End']],
            y=[row['job_code'], row['job_code']],
            mode='lines+markers',
            line=dict(color='red', width=5),
            name='Actual',
            hoverinfo='text',
            text=f"Actual: {row['Actual Start'].strftime('%b %d')} to {row['Actual End'].strftime('%b %d')}",
        ))

# Add annotations for Expected and Actual dates
for i, row in df_filtered.iterrows():
    if pd.notna(row['Expected Start']):
        fig.add_annotation(
            x=row['Expected Start'],
            y=row['job_code'],
            text=f"{row['Expected Start'].strftime('%b %d')}",
            showarrow=False,
            xshift=-10,
            yshift=10,
            textangle=90,
            font=dict(size=7)
        )
    if pd.notna(row['Expected End']):
        fig.add_annotation(
            x=row['Expected End'],
            y=row['job_code'],
            text=f"{row['Expected End'].strftime('%b %d')}",
            showarrow=False,
            xshift=10,
            yshift=10,
            textangle=90,
            font=dict(size=8)
        )
    if pd.notna(row['Actual Start']):
        fig.add_annotation(
            x=row['Actual Start'],
            y=row['job_code'],
            text=f"{row['Actual Start'].strftime('%b %d')}",
            showarrow=False,
            xshift=-10,
            yshift=-20,
            textangle=90,
            font=dict(size=7)
        )
    if pd.notna(row['Actual End']):
        fig.add_annotation(
            x=row['Actual End'],
            y=row['job_code'],
            text=f"{row['Actual End'].strftime('%b %d')}",
            showarrow=False,
            xshift=10,
            yshift=-20,
            textangle=90,
            font=dict(size=7)
        )

# Update layout
fig.update_layout(
    title='Gantt Chart: Expected vs Actual Dates',
    xaxis_title='Date',
    yaxis_title='Job Code',
    xaxis=dict(type='date', tickformat='%b %Y'),
    xaxis_range=[df['Expected Start'].min(), df['Expected End'].max()],
    showlegend=False,
    legend=dict(yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=400 + len(df_filtered) * 20,  # Dynamic height based on the number of tasks
    margin=dict(l=0, r=0, t=40, b=0)
)

# Streamlit app
st.title('Gantt Chart: Expected vs Actual Dates')
st.plotly_chart(fig)
