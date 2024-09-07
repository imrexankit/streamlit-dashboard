import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# Google Sheets URLs
project_sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSi8SH1hivNxPLDZaVQBDqMQLFcwGLVkSNzQmmsXCvZbA8cHBvsC9sPkVF9NjKKkXm93lV13cAA0wrT/pub?output=csv'
idle_time_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSim4lC_gDM7-CE35oHbF5kRMpAiLv8YRXDAZC4SYHSRq6XfS62pngKd0efrAkIvTEBlv728_JC-G5t/pub?output=csv'
Project_status = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRNe0IR8SyrCU7H6J4gRXswVJVKukw0VFivj61AYCvJH96BovUJByWNKP95-kSiEV-rR1wc-F9NMYUF/pub?output=csv'

# Caching the data loading for efficiency
@st.cache_data(ttl=60)
def load_data(url):
    return pd.read_csv(url)

# Sidebar
st.sidebar.title("Select a Data Source")
data_source = st.sidebar.radio("Choose a sheet", ("Projects", "Idle Manpower"))

# # Filters section
# st.sidebar.subheader("Filters")
# year_filter = st.sidebar.selectbox("Year", [2022, 2023, 2024])  # Example filter for years
# month_filter = st.sidebar.selectbox("Month", ["January", "February", "March"])  # Example filter for months
# client_filter = st.sidebar.selectbox("Client", ["Client A", "Client B", "Client C"])  # Example filter for clients
# site_filter = st.sidebar.selectbox("Site", ["Site 1", "Site 2", "Site 3"])  # Example filter for sites

# Load the appropriate data based on the selected sheet
if data_source == "Projects":
    df = load_data(project_sheet_url)
else:
    df = load_data(idle_time_url)

# Main area header and dropdown for pages
st.title("SOMS Dashboard")
page = st.selectbox("Select Page", ["Timeline Chart", "Idle Manpower", "Project Status"])


# Main content area based on dropdown selection
if page == "Timeline Chart":
    st.subheader("Timeline Chart")
    if data_source == "Projects":
        # Convert columns to datetime
        df['Expected Start'] = pd.to_datetime(df['Expected Start'], format='%d-%b-%Y', errors='coerce')
        df['Expected End'] = pd.to_datetime(df['Expected End'], format='%d-%b-%Y', errors='coerce')
        df['Actual Start'] = pd.to_datetime(df['Actual Start'], format='%d-%b-%Y', errors='coerce')
        df['Actual End'] = pd.to_datetime(df['Actual End'], errors='coerce')

        # Update Actual End dates
        today = pd.Timestamp.now().normalize()
        df['Actual End'] = df['Actual End'].fillna(today)
        df.loc[df['Actual End'] > today, 'Actual End'] = today

        # Filter data
        df_filtered = df.dropna(subset=['Expected Start', 'Expected End'])
        df_filtered = df_filtered[~df_filtered['Actual Start'].isna()]

        # Create Gantt Chart    
        fig = go.Figure()

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
                    font=dict(size=7, color='orange')
                )
            if pd.notna(row['Expected End']):
                fig.add_annotation(
                    x=row['Expected End'],
                    y=row['job_code'],
                    text=f"{row['Expected End'].strftime('%b %d')}",
                    showarrow=False,
                    xshift=10,
                    yshift=10,
                    font=dict(size=8, color='orange')
                )
            if pd.notna(row['Actual Start']):
                fig.add_annotation(
                    x=row['Actual Start'],
                    y=row['job_code'],
                    text=f"{row['Actual Start'].strftime('%b %d')}",
                    showarrow=False,
                    xshift=-10,
                    yshift=-20,
                    font=dict(size=7, color='red')
                )
            if pd.notna(row['Actual End']):
                fig.add_annotation(
                    x=row['Actual End'],
                    y=row['job_code'],
                    text=f"{row['Actual End'].strftime('%b %d')}",
                    showarrow=False,
                    xshift=10,
                    yshift=-20,
                    font=dict(size=7, color='red')
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
        st.plotly_chart(fig)
# Close the box
    

elif page == "Idle Manpower":
    st.subheader("Idle Manpower Report")

    #vertical space
    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more vertical space

    if data_source == "Idle Manpower":
        # Convert the 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Calculate Idle Manhours
        df['Idle Manhours'] = df['Days Idle'] * 9

        # Aggregate Idle Manhours by Date
        df_daily_idle = df.groupby('Date').agg({'Idle Manhours': 'sum'}).reset_index()
        average_idle_manhours = df_daily_idle['Idle Manhours'].mean()


        # Create Line Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_daily_idle['Date'],
            y=df_daily_idle['Idle Manhours'],
            mode='lines+markers+text',
            line=dict(color='royalblue', width=2),
            name='Idle Manhours',
            text=df_daily_idle['Idle Manhours'],
            textposition='top center',
            textfont=dict(size=7)
        ))

        # fig.update_traces(
        #     texttemplate='%{y:.2s}',  # Display text with 2 decimal places
        #     textposition='top left',
            
        # )

        fig.update_layout(
            title='Idle Manhours Per Day',
            xaxis_title='Date',
            yaxis_title='Total Idle Manhours',
            xaxis=dict(
                type='date', 
                tickformat='%b %d, %Y', 
                showgrid=True,
                #gridcolor='lightgray',
                #gridwidth=0.1,
                #dtick='W1',
            ),
            margin=dict(l=50, r=50, t=40, b=100),
            shapes=[                       # Add border using shape
                dict(
                    type="rect",
                    x0=0, y0=0, x1=1, y1=1,
                    line=dict(color="#FFFFFC", width=0.5),
                    xref="paper", yref="paper"
                    )
                ],
                annotations=[                  # Annotation for total manhours
        dict(
            xref="paper", yref="paper",
                    x=0.5, y=1.1,  # Position above the chart (right side)
                    text=f"Avg Idle Hours per Day: {average_idle_manhours:,.0f}",  # Format to 2 decimal places
                    showarrow=False,
                    font=dict(size=14, color="white"),
                    bordercolor="white",
                    borderwidth=0,
                    borderpad=4,
#                   bgcolor="#0e1117",
                    )
                ],

            showlegend=False,
            height=400,
        )
        
        st.plotly_chart(fig)

        #vertical space
        st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more vertical space



        # Aggregate Idle Manhours by Client
        df_client_idle = df.groupby('Client').agg({'Idle Manhours': 'sum'}).reset_index().sort_values(by='Idle Manhours', ascending=False)

        # Calculate the total idle manhours
        total_idle_manhours = df_client_idle['Idle Manhours'].sum()

        # Create Bar Chart for Idle Manhours by Client
        fig_client = go.Figure()
        fig_client.add_trace(go.Bar(
            x=df_client_idle['Client'],
            y=df_client_idle['Idle Manhours'],
            marker_color='indianred',
            text=df_client_idle['Idle Manhours'],
            textposition='auto',
        ))

        fig_client.update_layout(
            title='Total Idle Manhours by Client',
            xaxis_title='Client',
            yaxis_title='Total Idle Manhours',
            margin=dict(l=50, r=50, t=40, b=100),
            height=400,
            shapes=[                       # Add border using shape
                dict(
                    type="rect",
                    x0=0, y0=0, x1=1, y1=1,
                    line=dict(color="#FFFFFC", width=0.5),
                    xref="paper", yref="paper"
                    )
                ],
                annotations=[                  # Annotation for total manhours
        dict(
            xref="paper", yref="paper",
                    x=0.5, y=1.1,  # Position above the chart (right side)
                    text=f"Total Idle Manhours: {total_idle_manhours:,.0f}",  # Format to 2 decimal places
                    showarrow=False,
                    font=dict(size=14, color="white"),
                    bordercolor="white",
                    borderwidth=0,
                    borderpad=4,
                    #    bgcolor="white",
                    )
                ]
        )
        # st.metric(label="Total Idle Manhours", value=f"{total_idle_manhours:,.0f}")

        st.plotly_chart(fig_client)

        #vertical space
        st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more vertical space


        # Aggregate Cost of Idle time by Client
        cost_of_idle_time = df['Pay Per Day'].sum().round(2)

        df_client_cost = df.groupby('Client').agg({'Pay Per Day': 'sum'}).reset_index().sort_values(by='Pay Per Day', ascending=False)

        total_row = pd.DataFrame({'Client': ['Total'], 'Pay Per Day': [cost_of_idle_time]})
        df_client_cost = pd.concat([df_client_cost, total_row], ignore_index=True)

        #df_client_cost = df.groupby('Client').agg({'Pay Per Day': 'sum'}).reset_index().sort_values(by='Pay Per Day', ascending=False)

        # Create Waterfall Chart for Cost of Idle Time by Client
        fig_client_cost = go.Figure()
        fig_client_cost.add_trace(go.Waterfall(
            name='Cost of Idle Time',
            measure=['relative'] * (len(df_client_cost) - 1) + ['total'],
#            measure=['relative','relative', 'relative', 'relative', 'relative', 'relative', 'total'],
            x=df_client_cost['Client'],
            y=df_client_cost['Pay Per Day'],
            text=df_client_cost['Pay Per Day'],
            textposition='auto',
        ))

        fig_client_cost.update_layout(
            title='Total Cost of Idle Time by Client',
            xaxis_title='Client',
            yaxis_title='Total Cost of Idle Time',
            margin=dict(l=50, r=50, t=40, b=100),
            height=600,
            shapes=[                       # Add border using shape
                dict(
                    type="rect",
                    x0=0, y0=0, x1=1, y1=1,
                    line=dict(color="#FFFFFC", width=0.5),
                    xref="paper", yref="paper"
                    )
                ],

        )
        st.plotly_chart(fig_client_cost)

# Project Status page area 
elif page == "Project Status":
    #st.subheader("Project Status")
    df_project_status = load_data(Project_status)
    #st.write(df_project_status)

    # clean numeric columns
# Clean data in specific columns
    df_clean = df_project_status[['PO Amount', 'Profit Margin', 'Estimated Budget', 
                              'Allocated Budget to Project Team', 'Expense by Project Team', 
                              'Balance', 'Profit Trend']]

    # Replace unwanted characters and convert to numeric
    df_clean = df_clean.apply(lambda col: col.str.replace('OMR', '')
                                           .str.replace('(', '')
                                           .str.replace(')', '')
                                           .str.replace(',', '')
                                           .str.replace('O', '')  # Remove stray 'O'
                                           .str.replace('-', '')
                                           .str.replace(' ', '')
                                           .str.replace('#VALUE!', '')
                                           .replace('', np.nan)   # Replace empty strings with NaN
                                           .astype(float) if col.dtype == 'object' else col)
    df_clean.fillna(0, inplace=True)

    # Process the data with relevant columns
    df_process = df_project_status[['Job Code','Client Name', 'PO received date', 'Project Type', 'S/ONO.','SO DATE','Remark']]
    df_project_data = pd.concat([df_process,df_clean], axis=1)
    #st.write(df_project_data)

    # Calculate metrics based on the 'Remark' column
    total_jobs = df_project_data['Job Code'].count()
    completed_jobs = df_project_data[df_project_data['Remark'] == 'Completed'].shape[0]
    ongoing_jobs = df_project_data[df_project_data['Remark'] == 'Ongoing'].shape[0]

    # Display metrics in cards
    st.subheader("Project Status Overview")
    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more vertical space


    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Total Jobs", value=total_jobs)

    with col2:
        st.metric(label="Completed Jobs", value=completed_jobs)

    with col3:
        st.metric(label="Ongoing Jobs", value=ongoing_jobs)

# Vertical space
    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more vertical space



    # Donut chart for total jobs by status (Remark)
    remark_counts = df_project_data['Remark'].value_counts()
    fig_donut = go.Figure(data=[go.Pie(
    labels=remark_counts.index,
        values=remark_counts.values,
        hole=0.4,
            textinfo='label+percent',
            marker=dict(colors=['gold', 'lightcoral', 'lightskyblue'])
        )])
    fig_donut.update_layout(title_text="Total Jobs by Status")
    st.plotly_chart(fig_donut)

# vertical space
    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more vertical space



# Stacked bar chart Client-wise with Completed and Ongoing Jobs
# Group by client and remark, then filter clients with ongoing jobs
    client_status = df_project_data.groupby(['Client Name', 'Remark']).size().unstack(fill_value=0)
    ongoing_clients = df_project_data[df_project_data['Remark'] == 'Ongoing']['Client Name'].unique()

# Filter client_status to include only those clients with ongoing jobs
    client_status_filtered = client_status.loc[ongoing_clients]

# Calculate the total number of jobs for each client
    client_status_filtered['Total Jobs'] = client_status_filtered.sum(axis=1)

# Create Stacked Bar Chart for Clients with Ongoing Jobs
    fig_client = go.Figure()

# Add bars for Completed Jobs
    fig_client.add_trace(go.Bar(
        x=client_status_filtered.index,
        y=client_status_filtered['Completed'],
        name='Completed Jobs',
        marker_color='green',  # Customize as needed
        text=client_status_filtered['Completed'],
        textposition='inside',  # Display text inside the bars
    ))

# Add bars for Ongoing Jobs
    fig_client.add_trace(go.Bar(
        x=client_status_filtered.index,
        y=client_status_filtered['Ongoing'],
        name='Ongoing Jobs',
        marker_color='#FF7F7F',  # Customize as needed
        text=client_status_filtered['Ongoing'],
        textposition='inside',  # Display text inside the bars
    ))

# Add annotations for total values
    for i, client in enumerate(client_status_filtered.index):
        total_value = client_status_filtered.loc[client, 'Total Jobs']
        y_position = total_value + 2
        fig_client.add_annotation(
            x=client,
            y=y_position,
            text=f'{total_value}',
            showarrow=False,
            # arrowhead=2,
            # ax=0,
            # ay=-50,  # Adjust position of annotation
            font=dict(size=12, color="white")
        )

    fig_client.update_layout(
        title='Completed and Ongoing Jobs by Client',
        xaxis_title='Client',
        yaxis_title='Number of Jobs',
        barmode='stack',
        xaxis=dict(tickangle=-45),  # Rotate x-axis labels if needed for readability
        height=400,
        
    )


    st.plotly_chart(fig_client)

#vertical space
    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds more vertical space

# Stacked bar chart by Project Type with Completed and Ongoing Jobs
    type_status = df_project_data.groupby(['Project Type', 'Remark']).size().unstack(fill_value=0)
    fig_type = go.Figure()
    for status in type_status.columns:
        fig_type.add_trace(go.Bar(
        x=type_status.index,
        y=type_status[status],
        name=status,
        text=type_status[status],  # Show values inside bars
        textposition='auto'
    ))
    fig_type.update_layout(
        title='Completed and Ongoing Jobs by Project Type',
        xaxis_title='Project Type',
        yaxis_title='Number of Jobs',
        barmode='stack'
    )
    st.plotly_chart(fig_type)
