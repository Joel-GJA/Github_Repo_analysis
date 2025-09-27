# github_repo_analysis.py
import os
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("Warning: GITHUB_TOKEN not found in .env file.")

headers = {"Authorization": f"token {GITHUB_TOKEN}"}


# Fetch repos based on user query
def search_repos(query, sort='stars', order='desc', per_page=20):
    """Fetches repositories from the GitHub Search API."""
    if not GITHUB_TOKEN:
        st.error("🚨 GITHUB_TOKEN is missing. Analysis cannot proceed.")
        return []
        
    url = f"https://api.github.com/search/repositories?q={query}&sort={sort}&order={order}&per_page={per_page}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['items']
    else:
        st.error(f"Failed to fetch repos. Status code: {response.status_code}")
        st.error(f"Error details: {response.json().get('message', 'Check your token and rate limit.')}")
        return []

# Analyze fetched repos
def analyze_repos(repos):
    """
    Converts the list of repository dicts into a pandas DataFrame
    and adds columns for log-transformed popularity metrics.
    """
    data = []
    for repo in repos:
        stars = repo['stargazers_count']
        forks = repo['forks_count']
        
        data.append({
            'name': repo['full_name'],
            'stars': stars,
            'forks': forks,
            'watchers': repo['watchers_count'],
            'language': repo['language'] if repo['language'] else 'Other/None',
            'created_at': datetime.strptime(repo['created_at'], "%Y-%m-%dT%H:%M:%SZ"),
            'log_stars': np.log10(1 + stars),
            'log_forks': np.log10(1 + forks)
        })
    return pd.DataFrame(data)

# --- Analysis & Plotting Functions ---

def calculate_summary_stats(df):
    """
    Calculates raw averages and log-transformed averages (for normalized analysis).
    """
    # Raw Averages
    avg_stars = df['stars'].mean().round(1)
    avg_forks = df['forks'].mean().round(1)
    avg_watchers = df['watchers'].mean().round(1)
    
    # Log Averages
    avg_log_stars = df['log_stars'].mean().round(2)
    avg_log_forks = df['log_forks'].mean().round(2)
    
    return avg_stars, avg_forks, avg_watchers, avg_log_stars, avg_log_forks


# Plot stars and forks by language
def plot_language_trends(df):
    """Generates a bar plot of total stars and forks grouped by language."""
    grouped = df[df['language'] != 'Other/None'].groupby('language').agg({'stars':'sum', 'forks':'sum'}).sort_values('stars', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10,6))
    grouped.plot(kind='bar', ax=ax, rot=45)
    ax.set_title('Top 10 Languages: Total Stars and Forks')
    ax.set_ylabel('Count')
    plt.tight_layout()
    return fig

# Plot creation trend by year
def plot_creation_trend(df):
    """Generates a line plot showing repository creation trend over years."""
    df['year'] = df['created_at'].dt.year
    trend = df.groupby('year').size()
    fig, ax = plt.subplots(figsize=(10,5.5))
    trend.plot(kind='line', marker='o', ax=ax)
    ax.set_title('Repository Creation Trend Over Years')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Repositories')
    return fig

# Plot log-transformed stars and forks over time
def plot_time_series(df):
    """Generates a scatter plot of log-transformed stars and forks against creation date."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.scatter(df['created_at'], df['log_stars'],label='Log(Stars)', alpha=0.6, s=50, color='blue')
    
    ax.scatter(df['created_at'], df['log_forks'],label='Log(Forks)', alpha=0.6, s=50, color='red', marker='x')

    ax.set_title('Log-Transformed Popularity (Stars & Forks) Over Time')
    ax.set_xlabel('Repository Creation Date')
    ax.set_ylabel(r'$\log_{10}(1 + \text{Count})$')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


# --- Streamlit UI (Simplified for 'self-made' feel) ---
st.title("GitHub Repository Popularity & Trends Analyzer ")

st.markdown("""
    *Use this tool to fetch and analyze trending repositories based on a search query.*
""")

# Input fields
query = st.text_input("1. Enter search query (e.g., language:Python):", "language:Python")

per_page = st.slider("2. Number of repositories to fetch (5-50):", 5, 50, 20)
sort = st.selectbox("3. Sort by:", ["stars", "forks", "updated"])
order = st.selectbox("4. Order:", ["desc", "asc"])

if st.button("Analyze Data"):
    if not GITHUB_TOKEN:
        st.error("Please set your GITHUB_TOKEN in the `.env` file to proceed.")
        st.stop()
        
    with st.spinner("Fetching and analyzing repositories..."):
        repos = search_repos(query, sort, order, per_page)
        
        if repos:
            df = analyze_repos(repos)
            st.success(f"Successfully analyzed {len(df)} repositories.")
            st.markdown("---")
            
            # --- Summary Statistics ---
            st.header("Summary Statistics")
            
            avg_stars, avg_forks, avg_watchers, avg_log_stars, avg_log_forks = calculate_summary_stats(df)

            st.markdown("##### Raw Averages (May be Skewed)")
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg. Stars", f"{avg_stars:.1f}")
            col2.metric("Avg. Forks", f"{avg_forks:.1f}")
            col3.metric("Avg. Watchers", f"{avg_watchers:.1f}")
            
            st.markdown("##### Log-Transformed Averages (Normalized Popularity)")
            col4, col5 = st.columns(2)
            col4.metric("Log(Stars) Mean", f"{avg_log_stars:.2f}")
            # Equivalent Stars (10^log - 1)
            col5.metric("Equivalent Stars", f"{int(10**avg_log_stars - 1):,}")

            st.markdown("---")

            # --- Raw Data ---
            st.header("Fetched Data")
            st.write(f"Showing the top {len(df)} results sorted by **{sort}**:")
            st.dataframe(df[['name', 'stars', 'forks', 'watchers', 'language', 'created_at']])

            st.markdown("---")

            # --- Visualizations ---
            st.header("Visualization Trends")
            
            col_lang, col_trend = st.columns(2)

            with col_lang:
                st.subheader("Language Popularity")
                st.caption("")
                st.caption("")
                st.pyplot(plot_language_trends(df))

            with col_trend:
                st.subheader("Repository Creation Over Time")
                st.pyplot(plot_creation_trend(df))

            st.subheader("Popularity Trends Over Time (Log Scale)")
            st.pyplot(plot_time_series(df))

        else:
            st.info("No repositories found or an error occurred during fetching.")