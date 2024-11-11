import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt
from PIL import Image

st.set_page_config(page_title="Family Mart Sentiment Analysis", layout="wide")

# Load logo on top of sidebar
logo_path = "Untitled design (16).png"
logo = Image.open(logo_path)
st.sidebar.image(logo, width=200)

# File path and data loading function
file_path = r"C:\Users\user\OneDrive\Documents\YEAR 3\SEPT SEM\FYP 2\GS_Categorization & remove unmeaningful.xlsx"

@st.cache_data
def load_data():
    dataframes = pd.read_excel(file_path, sheet_name=None)
    df_list = []
    for sheet_name, df in dataframes.items():
        df['Source'] = sheet_name
        df_list.append(df)
    data = pd.concat(df_list, ignore_index=True)
    if 'Review_Date' in data.columns:
        data['Review_Date'] = pd.to_datetime(data['Review_Date'], errors='coerce')
    return data

# Load data and add Sentiment Score
data = load_data()
sentiment_map = {'POS': 1, 'NEU': 0.5, 'NEG': 0}
data['Sentiment Score'] = data['Sentiment'].map(sentiment_map).fillna(0)  # map sentiments to scores

# Sidebar filters (define before using them)
st.sidebar.header("📊 Analysis Controls")

# Ensure each widget has a unique key
selected_date_range = st.sidebar.date_input("Select Date Range", (data['Review_Date'].min(), data['Review_Date'].max()), key="date_range_1")
selected_source = st.sidebar.multiselect("Reviews Channels", data["Source"].unique(), default=data["Source"].unique(), key="source_1")
selected_sentiment = st.sidebar.multiselect("Sentiment Categories", data["Sentiment"].unique(), default=data["Sentiment"].unique(), key="sentiment_1")

# Filter data based on selections
filtered_data = data[(data["Source"].isin(selected_source)) & (data["Sentiment"].isin(selected_sentiment))]
selected_date_range = pd.to_datetime(selected_date_range)
if 'Review_Date' in filtered_data.columns:
    filtered_data = filtered_data[(filtered_data['Review_Date'] >= selected_date_range[0]) & (filtered_data['Review_Date'] <= selected_date_range[1])]

# Dashboard title and description
st.title("🏪 Family Mart: Customer Sentiment Intelligence Dashboard")
st.markdown("""
    This dashboard provides actionable insights from customer feedback analysis to drive business improvements.
    Use the filters in the sidebar to explore specific aspects of customer sentiment.
""")  # <-- Fixed missing triple-quote here

# Main Page: Key Metrics Summary
st.markdown("## 🔑 Key Metrics Summary")
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics
total_reviews = len(filtered_data)
average_sentiment_score = filtered_data['Sentiment Score'].mean().round(2)
positive_count = len(filtered_data[filtered_data['Sentiment'] == 'POS'])
neutral_count = len(filtered_data[filtered_data['Sentiment'] == 'NEU'])
negative_count = len(filtered_data[filtered_data['Sentiment'] == 'NEG'])

# Display metrics in columns
col1.metric("Total Reviews", total_reviews)
col2.metric("Average Sentiment Score", average_sentiment_score)
col3.metric("🥰 Positive Sentiment", positive_count)
col4.metric("😐 Neutral Sentiment", neutral_count)
col5.metric("😡 Negative Sentiment", negative_count)

# Continue with data sample display and other analysis sections as before
st.write("Loaded data sample:")

# Filter data by sources
google_play_data = data[data["Source"] == "Google Play"]
indeed_data = data[data["Source"] == "Indeed"]
pissed_consumer_data = data[data["Source"] == "Pissed Consumer"]

# Display three tables in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Google Play Data")
    st.dataframe(google_play_data[['Review_Date', 'Source', 'Aspect', 'Sentiment Expression', 'Sentiment']].head(100), height=300)

with col2:
    st.subheader("Indeed Data")
    st.dataframe(indeed_data[['Review_Date', 'Source', 'Aspect', 'Sentiment Expression', 'Sentiment']].head(100), height=300)

with col3:
    st.subheader("Pissed Consumer Data")
    st.dataframe(pissed_consumer_data[['Review_Date', 'Source', 'Aspect', 'Sentiment Expression', 'Sentiment']].head(100), height=300)

# Custom CSS for centering and enlarging headers
st.markdown("""
    <style>
    .centered-title {
        font-size: 2em;
        font-weight: bold;
        text-align: center;
        color: #2A2A2A;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

# Create tabs for different analysis sections
tab1, tab2, tab3 = st.tabs(["📈 Trend Analysis", "🎯 Aspect Analysis", "🔍 Detailed Insights"])

# Compute additional metrics
if 'Sentiment Score' not in data.columns:
    # Assuming sentiment scores are assigned as POS = 1, NEU = 0, NEG = -1
    sentiment_map = {'POS': 1, 'NEU': 0, 'NEG': -1}
    data['Sentiment Score'] = data['Sentiment'].map(sentiment_map)

# Trend Analysis Tab
with tab1:
    st.markdown("""
    <style>
        .centered-title {
            text-align: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
    </style>
    <div class="centered-title">📈 Trend Analysis</div>
""", unsafe_allow_html=True)
    if 'Review_Date' in filtered_data.columns:
        timeline_data = (
            filtered_data.groupby([filtered_data['Review_Date'].dt.to_period('M'), 'Sentiment'])
            .size().reset_index(name='Count')
        )
        timeline_data['Review_Date'] = timeline_data['Review_Date'].dt.to_timestamp()
        alt_chart = alt.Chart(timeline_data).mark_line(point=True).encode(
            x=alt.X('Review_Date:T', title='Date'),
            y=alt.Y('Count:Q', title='Number of Reviews'),
            color='Sentiment:N',
            tooltip=['Review_Date:T', 'Sentiment:N', 'Count:Q']
        ).properties(width=700, height=400).interactive()
        st.altair_chart(alt_chart, use_container_width=True)

    # Key Insights Summary
    st.markdown("---")
    st.markdown("""
    <h3 style="text-align: center;">📌 Key Insights Summary</h2>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🌟 POS - Improving Areas")
        positive_aspects = filtered_data[filtered_data['Sentiment'] == 'POS']['Aspect'].value_counts().nlargest(3)
        for aspect, count in positive_aspects.items():
            st.markdown(f"- **{aspect}**: {count} positive mentions")

    with col2:
        st.write("### ⚠️ NEG - Areas Needing Attention")
        negative_aspects = filtered_data[filtered_data['Sentiment'] == 'NEG']['Aspect'].value_counts().nlargest(3)
    
        for aspect, count in negative_aspects.items():
            st.markdown(f"- **{aspect}**: {count} negative mentions")

    st.markdown("---")
    st.markdown("""
    <h3 style="text-align: center;">☁️ WordCloud</h2>
""", unsafe_allow_html=True)
    # Word Cloud of Aspect
    text = ' '.join(filtered_data['Aspect'].dropna().astype(str))
    if text:  # Check if there is any text to display
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
    else:
        st.write("No data available for word cloud.")

# Aspect Analysis Tab
with tab2:
    st.markdown('<div class="centered-title">🎯 Aspect Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        top_aspects = filtered_data["Aspect"].value_counts().nlargest(10).index
        aspect_data = filtered_data[filtered_data["Aspect"].isin(top_aspects)]
        aspect_sentiment = aspect_data.groupby(["Aspect", "Sentiment"]).size().reset_index(name="Count")
        fig_aspects = px.bar(
            aspect_sentiment, x="Aspect", y="Count", color="Sentiment", title="Top 10 Most Discussed Aspects", barmode="group"
        )
        fig_aspects.update_layout(height=400)
        st.plotly_chart(fig_aspects, use_container_width=True)
    with col2:
        sentiment_by_source = filtered_data.groupby(["Source", "Sentiment"]).size().reset_index(name="Count")
        fig_dist = px.sunburst(
            sentiment_by_source, path=['Source', 'Sentiment'], values='Count', title="Sentiment Distribution by Reviews Channel"
        )
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)

# Advanced Search and Filtering
    search_col1, search_col2 = st.columns(2)
    with search_col1:
        search_aspect = st.text_input("🔍 Search for specific aspects or keywords")
    with search_col2:
        min_mentions = st.slider("Minimum mentions", 1, 100, 5)
    
    if search_aspect:
        search_results = filtered_data[
            filtered_data["Aspect"].str.contains(search_aspect, case=False, na=False)
        ]
        st.write(f"Found {len(search_results)} mentions of '{search_aspect}'")
        
        # Show sentiment distribution for searched aspect
        search_sentiment = search_results["Sentiment"].value_counts()
        fig_search = px.pie(
            values=search_sentiment.values,
            names=search_sentiment.index,
            title=f"Sentiment Distribution for '{search_aspect}'"
        )
        st.plotly_chart(fig_search)
        
        # Show actual reviews
        st.dataframe(
            search_results[['Review_Date', 'Source', 'Aspect', 'Sentiment', 'Sentiment Expression']],
            hide_index=True
        )

# Detailed Insights Tab
with tab3:
    st.markdown('<div class="centered-title">🔍 Detailed Insights</div>', unsafe_allow_html=True)

    sentiment_options = ["All", "POS", "NEU", "NEG"]
    selected_sentiment = st.radio("Select Sentiment", sentiment_options, index=0)
    st.subheader("Sentiment Distribution")
    sentiment_counts = filtered_data["Sentiment"].value_counts()
    colors = {'POS': 'lightcoral', 'NEU': 'lightblue', 'NEG': 'lightslategray'}
    fig = go.Figure(go.Pie(
        labels=sentiment_counts.index, values=sentiment_counts.values,
        marker=dict(colors=[colors[sentiment] if sentiment == selected_sentiment else 'silver' for sentiment in sentiment_counts.index]),
        hole=0.3
    ))
    fig.update_layout(title_text="Sentiment Distribution for Selected Aspect", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    if selected_sentiment != "All":
        filtered_data = filtered_data[filtered_data["Sentiment"] == selected_sentiment]
    st.dataframe(filtered_data[['Review_Date', 'Source', 'Aspect', 'Sentiment', 'Sentiment Expression']], hide_index=True)

# Add export functionality
if st.button("📥 Export Analysis Report", key="export_button"):
    st.download_button(
        label="Download Data",
        data=filtered_data.to_csv().encode('utf-8'),
        file_name='familymart_sentiment_analysis.csv',
        mime='text/csv',
        key="download_button"
    )
