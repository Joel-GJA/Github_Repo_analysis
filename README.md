# Github_Repo_analysis
This looks like a complete and well-structured Streamlit application for analyzing GitHub repository data\! Here is a README file for the `github_repo_analysis.py` project, along with key learning points about the tools used.

-----

# 🐙 GitHub Repository Popularity & Trends Analyzer

This Streamlit application fetches and analyzes trending GitHub repositories based on a user-defined search query. It provides summary statistics and various visualizations to explore language popularity, creation trends, and log-transformed popularity metrics over time.

## ✨ Features

  * **GitHub API Integration:** Fetches repository data using the GitHub Search API.
  * **Data Analysis:** Utilizes **Pandas** for efficient data processing and calculates summary statistics.
  * **Popularity Normalization:** Employs **NumPy's** log transformation ($\log_{10}(1+x)$) to normalize highly skewed popularity metrics (stars and forks).
  * **Interactive UI:** Built with **Streamlit** for a simple and interactive user experience.
  * **Visualizations:** Generates plots using **Matplotlib** to show:
      * Top languages by total stars and forks.
      * Repository creation trend over the years.
      * Log-transformed popularity (stars and forks) over the creation date.

## ⚙️ Setup and Installation

### Prerequisites

  * Python 3.7+
  * A **GitHub Personal Access Token (PAT)**.

### Steps

1.  **Clone the repository:**

    git clone <repository_url>
    cd github-repo-analyzer

2.  **Install dependencies:**

    pip install -r requirements.txt
    # Assuming you have a requirements.txt with:
    # streamlit
    # pandas
    # numpy
    # requests
    # python-dotenv
    # matplotlib

3.  **Create an environment file:**
    Create a file named `.env` in the root directory and add your GitHub Personal Access Token:

    # .env
    GITHUB_TOKEN="YOUR_PERSONAL_ACCESS_TOKEN_HERE"
    
    *Note: The token is used for authorization to increase the API rate limit.*

4.  **Run the application:**

    streamlit run github_repo_analysis.py

    The application will open in your web browser.

## 🚀 Usage

1.  **Enter Search Query:** Specify your search criteria (e.g., `language:JavaScript`, `topic:machine-learning`).
2.  **Configure Fetch:** Select the number of repos to fetch, the sorting criteria (`stars`, `forks`, `updated`), and the order (`desc`, `asc`).
3.  **Click "Analyze Data":** The app will fetch the data, perform the analysis, and display statistics and plots.

## 📚 Learning Points

The development of this application highlights several key concepts and best practices in data science and API interaction:

### 1\. GitHub API Interaction

  * **Authentication:** The use of a `GITHUB_TOKEN` stored in an environment variable (`.env` file) and passed in the request header via the `Authorization` field is the standard and secure way to interact with the GitHub API. This token significantly **increases your rate limit** compared to unauthenticated requests.
  * **Search API:** The core functionality relies on the `/search/repositories` endpoint. This allows for complex querying (e.g., filtering by language, topic, stars) directly in the URL query parameters (`q={query}&sort={sort}`).
  * **Handling Errors:** The `search_repos` function includes explicit error checking for a `response.status_code` of 200, providing helpful messages about potential issues like incorrect tokens or hitting the **API rate limit**.

### 2\. NumPy for Transformation

  * **Log Transformation for Skewed Data:** The popularity metrics like "stars" and "forks" on GitHub are often heavily **right-skewed** (a few repos have millions, most have very few).
  * **Normalization:** The code uses `np.log10(1 + x)` to apply a **log base 10 transformation**.
      * **The Log:** It pulls in the extremely high values, making the distribution closer to normal and more suitable for averaging and comparison, allowing for normalized popularity metrics.
      * **The $+1$:** Adding 1 to the count (`1 + x`) is crucial because $\log(0)$ is undefined. Since a repository can have 0 stars or forks, adding 1 ensures the log is calculated for all data points, with $0$ stars/forks mapping to $\log(1)=0$.

### 3\. Pandas for Data Wrangling

  * **Data Structuring:** The `analyze_repos` function efficiently converts the list of dictionaries returned by the API into a structured **Pandas DataFrame**, which is the foundation for all subsequent analysis and plotting.
  * **Feature Engineering:** It dynamically adds new, derived columns like `'log_stars'`, `'log_forks'`, and `'year'` (`df['created_at'].dt.year`) for enhanced analysis without modifying the original data.
  * **Grouped Analysis:** Functions like `plot_language_trends` utilize the powerful `groupby()` and `agg()` methods to quickly calculate the sum of stars/forks for each programming language, making the visualization data generation concise.

### 4\. Streamlit for Dashboarding

  * **Simplified UI:** Streamlit makes creating an interactive web application trivial. The code uses functions like `st.title()`, `st.text_input()`, `st.selectbox()`, and `st.button()` to build the UI with minimal effort.
  * **Displaying Metrics:** The `st.metric()` function is excellent for displaying key performance indicators (KPIs) and summary statistics in an organized layout.
  * **Visualization Integration:** Streamlit seamlessly integrates with Matplotlib, using `st.pyplot(fig)` to display the generated charts.