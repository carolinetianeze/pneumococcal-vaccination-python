# Assessing Socioeconomic Barriers to Pneumococcal Vaccination in Brazil

This project conducts a comprehensive statistical analysis of the factors influencing the 10-valent Pneumococcal Conjugate Vaccine (PCV-10) coverage across 5,500+ Brazilian municipalities. Utilizing a large-scale real-world dataset, we examine the impact of municipal development on baseline immunization uptake and map adherence friction by calculating the clinical **Booster Dropout Rate**.

## Key Research Findings

### 1. The Socioeconomic Divide (Pearson Correlation)
The Municipal Human Development Index (HDI) is confirmed as a significant macro-environmental factor dictating primary immunization success.
* **Positive Correlation:** Higher municipal development directly correlates with superior baseline vaccine coverage ($p < 0.001$), reflecting structural health access disparities.
* **Density Insights:** Bivariate density evaluation indicates a high concentration of municipalities clustering below the national target, highlighting systemic vulnerabilities across lower-income strata.

### 2. The Adherence Gap: Primary Series vs. Booster
Tracking patient persistence between the initial infant schedule (2 and 4 months) and the 12-month booster shot ($ref1$) reveals a critical drop in coverage.
* **Booster Decline:** While initial infant access is established, patient retention decreases significantly by the 12-month mark.
* **Regional Friction:** High dropout rates are heavily concentrated in specific macro-regions, pinpointing where longitudinal follow-up care and active patient tracking break down.

### 3. Structural Paradoxes: Identifying "Vaccine Deserts"
By mapping socioeconomic indices against statistical anomalies, the model isolates structural public health failures.
* **Vaccine Deserts:** A significant cluster of municipalities with an HDI above the national median exhibits critically low vaccination rates (Z-Score $< -2.0$).
* **Epidemiological Significance:** Since these regions possess adequate economic infrastructure, this statistical divergence strongly points toward behavioral **vaccine hesitancy** or localized urban logistical bottlenecks rather than financial scarcity.

## Model Performance & Reliability
To ensure the scientific validity of the geographic and demographic comparisons, we performed data normalization and statistical evaluations across the pipeline:

| Test / Metric | Status / Application | Interpretation |
| :--- | :--- | :--- |
| **Pearson Correlation ($r$)** | Quantified ($p < 0.001$) | Validates the linear link between structural wealth and primary vaccine distribution. |
| **Z-Score Anomaly Vector** | Threshold set at $\pm 2.0$ | Reliably separates standard coverage fluctuations from true systemic outliers. |
| **Data Normalization** | Upper-bound clipped at 100% | Resolves DATASUS population estimation anomalies to prevent mathematical inflation. |
| **Temporal Consistency** | Longitudinal tracking ($\ge 2019$) | Ensures findings are robust against annual seasonal variance or pandemic anomalies. |

## Feature Engineering & Methodology
* **Immunization Retention (Dropout Rate):** Programmatic patient dropout was engineered using the following epidemiological formula:
$$Dropout \, Rate = \frac{(\text{Primary Coverage} - \text{Booster Coverage})}{\text{Primary Coverage}} \times 100$$
* **Socioeconomic Alignment:** String-based municipal index scores were cleaned, parsed into standard floating-point metrics, and merged using synchronized 7-digit IBGE municipal codes to match administrative registries seamlessly.
* **Outlier Classification Matrix:** Municipalities were grouped into `Standard`, `High Performer`, and `Vaccine Desert` categories using combined median development thresholds and coverage Z-scores.

## Project Structure
* `pni_pneumo_analysis.py`: Main execution pipeline (Cloud data fetching, data cleaning, Z-score modeling, and statistical exports).
* **Figures/**:
    * `regional_boxplot.png`: Static macro-regional boxplots demonstrating spatial vaccination inequality.
    * `heatmap.html`: Interactive bivariate density map charting the intersection of HDI and coverage.
    * `states_map.html`: Dynamic state-level choropleth mapping utilizing live GeoJSON vector integration.
    * `dropout_rate_analysis.html`: Interactive ordinary least squares (OLS) regression line modeling patient attrition.
    * `statistical_outliers_analysis.html`: High-contrast scatter plot isolating critical "Vaccine Deserts".

## Public Health Implications
This data pipeline transitions raw administrative claims into actionable **Real-World Evidence (RWE)**. Proving that high development does not universally guarantee high immunization highlights that public health strategies must adapt. While less-developed regions require infrastructural support, affluent "Vaccine Deserts" demand tailored communication campaigns to combat behavioral vaccine hesitancy and safeguard community immunity.

---
**Developed by Caroline** – *Pharmacoepidemiologist & RWE Analytics Consultant*