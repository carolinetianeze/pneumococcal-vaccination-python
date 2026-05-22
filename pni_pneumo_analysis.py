#%% Installation of required libraries
# pip install pandas basedosdados google-cloud-bigquery kagglehub openpyxl scipy plotly matplotlib seaborn statsmodels

#%% Import of required libraries
import os
import ssl
import json
from urllib.request import urlopen
import pandas as pd
import numpy as np
import basedosdados as bd
import kagglehub
from scipy.stats import pearsonr
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import statsmodels

#%% *** 1. Configuration ***
# Replace with your Google Cloud Project ID for BigQuery billing
PROJECT_ID = "MY_PROJECT_ID"

# Create output directory for figures
os.makedirs("Figures", exist_ok=True)

#%% *** 2. Data Ingestion (Google BigQuery & Kaggle Hub) ***

print("Extracting PNI immunization data from BigQuery...")
query = """
        SELECT ano, \
               sigla_uf, \
               id_municipio, \
               doses_pneumococica, \
               cobertura_pneumococica, \
               doses_pneumococica_ref1, \
               cobertura_pneumococica_ref1
        FROM `basedosdados.br_ms_imunizacoes.municipio`
        WHERE ano >= 2019 \
        """

# Extracting data directly into a Pandas DataFrame
df = bd.read_sql(query, billing_project_id=PROJECT_ID, reauth=True)
print("Vaccination Data Sample Loaded Successfully:")
print(df.head())

print("\nDownloading socioeconomic dataset from Kaggle...")
path = kagglehub.dataset_download("gabrielrs3/economy-and-population-of-cities-in-brazil-ibge")

# Identify the downloaded file in the target path
files = os.listdir(path)
file_path = os.path.join(path, files[0])

# Load socioeconomic indicators from IBGE
df_hdi = pd.read_excel(file_path)
print("HDI Data Sample Loaded Successfully:")
print(df_hdi.head())

#%% *** 3. Data Wrangling & Preprocessing ***
print("\nPreprocessing and merging datasets...")
# Convert city code columns to numeric for seamless joining
df['id_municipio'] = pd.to_numeric(df['id_municipio'], errors='coerce')
df_hdi['IBGECode'] = pd.to_numeric(df_hdi['IBGECode'], errors='coerce')

# Merge dataframes using standard IBGE keys
df_final = pd.merge(df, df_hdi, left_on='id_municipio', right_on='IBGECode', how='inner')

# Normalize the IDHM field (convert string commas to standard dots)
df_final['IDHM'] = df_final['IDHM'].astype(str).str.replace(',', '.')
df_final['IDHM'] = pd.to_numeric(df_final['IDHM'], errors='coerce')

# Clean mapping coordinates
df_final['Latitude'] = pd.to_numeric(df_final['Latitude'].astype(str).str.replace(',', '.'), errors='coerce')
df_final['Longitude'] = pd.to_numeric(df_final['Longitude'].astype(str).str.replace(',', '.'), errors='coerce')

# Cap vaccine coverages at 100% to handle population estimation anomalies
df_final['cobertura_pneumococica'] = df_final['cobertura_pneumococica'].clip(upper=100)
df_final['cobertura_pneumococica_ref1'] = df_final['cobertura_pneumococica_ref1'].clip(upper=100)

# Drop missing values across target analytical variables
df_clean = df_final.dropna(subset=['IDHM', 'cobertura_pneumococica', 'cobertura_pneumococica_ref1']).copy()

#%% *** 4. Core Statistical Analysis ***
print("\nExecuting statistical evaluations...")
corr, p_value = pearsonr(df_clean['IDHM'], df_clean['cobertura_pneumococica'])
print(f"--> Pearson Correlation Coefficient (HDI vs. PCV Primary Coverage): {corr:.2f}")
print(f"--> P-Value: {p_value:.4e}")

# Generating 2D Density Heatmap
fig_density = px.density_heatmap(
    df_clean,
    x="IDHM",
    y="cobertura_pneumococica",
    nbinsx=30, nbinsy=30,
    color_continuous_scale="Viridis",
    title="Heatmap: HDI vs. Vaccine Coverage Density",
    labels={'cobertura_pneumococica': 'Coverage (%)', 'IDHM': 'Municipal HDI'}
)
fig_density.update_yaxes(range=[0, 110])
fig_density.write_html("Figures/heatmap.html")

#%% *** 5. Longitudinal Retention (Dropout Rate Tracking) ***
print("Calculating immunization adherence and dropouts...")
# Drop-out rate logic formula: ((Initial Dose - Booster) / Initial Dose) * 100
df_clean['dropout_rate'] = (
                                   (df_clean['cobertura_pneumococica'] - df_clean['cobertura_pneumococica_ref1']) /
                                   df_clean['cobertura_pneumococica'].replace(0, np.nan)
                           ) * 100

# Scatter plot for Dropouts with OLS Regression line
fig_dropout = px.scatter(
    df_clean,
    x="IDHM",
    y="dropout_rate",
    color="RegiaoBrasil",
    trendline="ols",
    hover_name="LocalCidade",
    hover_data=["sigla_uf", "cobertura_pneumococica"],
    title="Impact of Socioeconomic Development (HDI) on Vaccine Dropout Rates",
    labels={"IDHM": "Municipal HDI", "dropout_rate": "Dropout Rate (%)", "RegiaoBrasil": "Region"},
    template="plotly_white"
)
fig_dropout.update_yaxes(range=[-20, 100])
fig_dropout.write_html("Figures/dropout_rate_analysis.html")

#%% *** 6. Z-Score Driven Anomaly Detection ("Vaccine Deserts") ***
print("Executing Z-Score outlier detection for 'Vaccine Deserts'...")
df_clean['coverage_zscore'] = stats.zscore(df_clean['cobertura_pneumococica'])
hdi_median = df_clean['IDHM'].median()

# Initialize labels
df_clean['analysis_status'] = 'Standard'

# Set flags: Z-Score < -2 (Severely low coverage) but HDI > median (Highly developed city)
critical_mask = (df_clean['coverage_zscore'] < -2) & (df_clean['IDHM'] > hdi_median)
performer_mask = (df_clean['coverage_zscore'] > 2)

df_clean.loc[critical_mask, 'analysis_status'] = 'Vaccine Desert (Critical)'
df_clean.loc[performer_mask, 'analysis_status'] = 'High Performer'

# Scatter plot highlighting Vaccine Deserts
fig_outliers = px.scatter(
    df_clean,
    x="IDHM",
    y="cobertura_pneumococica",
    color="analysis_status",
    hover_name="LocalCidade",
    hover_data=["sigla_uf", "coverage_zscore"],
    color_discrete_map={
        'Standard': 'rgba(211, 211, 211, 0.4)',
        'Vaccine Desert (Critical)': 'crimson',
        'High Performer': 'seagreen'
    },
    title="Outlier Detection: Identification of 'Vaccine Deserts' in Brazil",
    labels={'cobertura_pneumococica': 'Coverage (%)', 'IDHM': 'Municipal HDI'},
    template="plotly_white"
)
fig_outliers.add_hline(y=95, line_dash="dash", line_color="blue", annotation_text="National Target (95%)")
fig_outliers.write_html("Figures/statistical_outliers_analysis.html")

#%% *** 7. Macro-Regional & Geospatial Visualizations ***
print("Plotting macro-regional coverage distributions...")
plt.figure(figsize=(12, 6))
sns.set_theme(style="whitegrid")
sns.boxplot(data=df_clean, x='RegiaoBrasil', y='cobertura_pneumococica', palette='Set3')
plt.axhline(95, color='red', linestyle='--', label='PNI Target (95%)')
plt.title('Distribution of Pneumococcal Coverage by Brazilian Region', fontsize=14)
plt.xlabel('Region', fontsize=12)
plt.ylabel('Coverage (%)', fontsize=12)
plt.ylim(0, 110)
plt.legend()
plt.tight_layout()
plt.savefig("Figures/regional_boxplot.png", dpi=300)
plt.close()

print("Generating state choropleth map...")
# Dynamic State-Level Choropleth Map via GeoJSON
context = ssl._create_unverified_context()
geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

try:
    with urlopen(geojson_url, context=context) as response:
        brazil_geojson = json.load(response)

    df_recent = df_clean[df_clean['ano'] == df_clean['ano'].max()].copy()
    df_state = df_recent.groupby('sigla_uf')['cobertura_pneumococica'].mean().reset_index()

    fig_map = px.choropleth(
        df_state,
        geojson=brazil_geojson,
        locations='sigla_uf',
        featureidkey="properties.sigla",
        color='cobertura_pneumococica',
        color_continuous_scale="Viridis",
        scope="south america",
        title=f"Average Pneumococcal Coverage by State ({int(df_clean['ano'].max())})",
        labels={'cobertura_pneumococica': 'Mean Coverage (%)'}
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.write_html("Figures/states_map.html")
except Exception as e:
    print(f"Choropleth mapping bypassed/failed due to network connection: {e}")

print("\nPipeline execution completed successfully! All artifacts saved inside 'Figures/'.")