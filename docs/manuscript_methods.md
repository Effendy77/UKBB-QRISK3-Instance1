QRISK3 Risk Calculation

Ten-year cardiovascular risk was calculated using the QRISK3 algorithm based on baseline (Instance 1) UK Biobank data. All predictor variables were derived from the Assessment Centre visit corresponding to the time of retinal imaging acquisition. Variables included age, sex, ethnicity, Townsend deprivation index, smoking category, diabetes status, treated hypertension, systolic blood pressure and variability, total cholesterol-to-HDL ratio, body mass index, family history of cardiovascular disease, atrial fibrillation, chronic kidney disease, rheumatoid arthritis, systemic lupus erythematosus, severe mental illness, steroid use, and erectile dysfunction in men.

Missing data were handled using multiple imputation by chained equations (m=5), applying predictive mean matching for continuous variables and logistic regression for binary variables. QRISK3 risk was computed using sex-specific equations in R, generating continuous 10-year ASCVD probability estimates.

Participants with prevalent cardiovascular disease at baseline were excluded to ensure proper risk estimation.