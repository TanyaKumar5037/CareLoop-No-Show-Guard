# CareLoop Clinics — No-Show Guard

**End-to-end data science capstone:** raw appointment data → trusted booking table → SQL business analysis → no-show risk model → AI-assisted follow-up review.

> **Project-name note:** the detailed pasted assignment brief calls the project **CareLoop Clinics**. An older AI-generated session summary uses **CareClick Clinics**. This repository follows the detailed brief. The detailed brief is treated as the primary specification where older summary notes differ.

## Four-part project summary

- **Part 1 — Data foundations:** 1,020 raw appointment rows were read; 988 passed type conversion and 32 were rejected. The pandas cleaning path retains 990 rows, including 218 no-shows, and exports 16 columns.
- **Part 2 — SQL and business intelligence:** the overall no-show rate is **22.0%** (218/990); the highest rate among clinics with at least 95 bookings is Hadapsar at **27.3%**, while Gomti Nagar is **33.3%** on only 90 bookings.
- **Part 3 — Machine learning:** Logistic Regression was selected using training-only 5-fold ROC-AUC (**0.774**) and a **0.35** threshold; the held-out test result is ROC-AUC **0.789**, recall **0.571**, with 49 appointments flagged.
- **Part 4 — Generative AI:** the first 10 call-centre notes are prepared for structured analysis; **9 nonblank notes** require Gemini calls and N004 is blank and skipped. Run `04_genai.ipynb` to replace the pending scaffold with validated model outputs and produce the final merged recommendations.

## Business question

Which appointments are most likely to be missed, why do patients miss them, and what should CareLoop do first?

CareLoop operates eight outpatient clinics in six Indian cities. Missed visits leave doctor capacity unused. The pipeline is designed to identify where and when no-shows cluster, flag bookings on the evening before their appointment, and convert call-centre notes into consistent reasons and front-desk actions.

## Repository structure

```text
CareLoop_No_Show_Guard/
├── data/
│   ├── appointments.csv
│   ├── clinics.csv
│   └── followup_notes.csv
├── 01_ingest_clean.ipynb
├── 02_queries.sql
├── part2_validation.py
├── 03_model.ipynb
├── 04_genai.ipynb
├── appointments_clean.csv
├── clinics_enriched.csv
├── rejected_rows.json
├── load_data.sql
├── test_risk_scores.csv
├── all_appointment_risk_scores.csv
├── notes_analysed.csv
├── clinic_no_show_summary_filtered.csv
├── clinic_no_show_summary_all.csv
├── lead_time_summary.csv
├── monthly_no_show_trend.csv
├── requirements.txt
└── .gitignore
```

The `outputs/` folder contains copies of generated outputs. The root-level copies make the requested submission files easy to find.

## How to run

### 1. Google Colab — Part 1

1. Open `01_ingest_clean.ipynb` in Google Colab.
2. Upload the three files from `data/` when prompted. Keep the names `appointments.csv`, `clinics.csv`, and `followup_notes.csv`.
3. Run all cells from top to bottom.
4. Download the generated `outputs/` files and replace the repository's existing copies.

Expected Part 1 checks:
- CSV `DictReader`: 1,020 rows; 988 accepted; 32 rejected.
- Pandas path: 20 exact duplicate rows removed; 990 rows remain after date/status filtering.
- Five impossible ages are converted to missing; age median = 48; distance median = 8.25.
- Distance values capped: 26; fee values capped: 3.
- No-shows: 218; lead days: 1–45; 296 bookings have lead time above 14 days.
- Final appointments file: 990 rows × 16 columns, unique appointment IDs, no missing values.

**Weather API note:** `clinics_enriched.csv` currently has blank `temp_c` values because the execution environment used to assemble this starter repository could not reach Open-Meteo. The notebook contains the required live API call, timeout, one retry, and `None` fallback. Run Task 1.5 in Colab to populate live values. Do not invent temperatures.

### 2. MySQL Workbench — Part 2

1. Open `02_queries.sql` and run the database/table creation section first.
2. Run `load_data.sql` to insert the 8 clinics followed by the 990 appointments.
3. Run the verification and analysis queries in `02_queries.sql`.
4. Run `python part2_validation.py` from the repository root to reproduce the clinic, lead-time and monthly summaries in Python and cross-check the SQL results.
4. Run the duplicate-key test separately; it is expected to fail because `A0001` already exists.
5. If MySQL installation fails, the assignment permits SQLiteOnline. Skip `CREATE DATABASE` and `USE`; SQLite's duplicate-key wording differs.

Key verified findings:
- **Clinic rate, at least 95 appointments:** Hadapsar 27.3% (39/143); Malviya Nagar 26.8% (38/142); Kothrud 22.5% (36/160); Vijay Nagar 20.8% (21/101); Edappally 16.2% (23/142); Vaishali Nagar 13.8% (18/130).
- **All clinics:** Gomti Nagar has the highest raw rate at 33.3% (30/90), but falls below the 95-booking reporting threshold. This is why the `HAVING` condition matters.
- **Lead time:** 1–7 days = 16.2%; 8–14 = 17.4%; 15–30 = 30.0%; 31+ = 60.5%.
- **Monthly rate:** January 24.8%; February 20.5%; March 20.4%; April 20.9%; May 23.7%; June 21.2%.
- **Overall rate:** 22.02%.

### 3. Google Colab — Part 3

1. Run `03_model.ipynb` after Part 1.
2. It reads `outputs/appointments_clean.csv`.
3. The test set is used only for reporting. Cross-validation, GridSearchCV and threshold selection use training data only.
4. The notebook writes `outputs/test_risk_scores.csv` (198 held-out rows) and `outputs/all_appointment_risk_scores.csv` (all 990 appointments, using out-of-fold probabilities for training rows and held-out probabilities for test rows).

Reference run with the supplied data:
- Feature matrix: 11 columns; train = 792; test = 198; test no-shows = 49.
- Test-set majority baseline: 149/198 = 0.7525.
- Logistic Regression at the default 0.5 threshold: accuracy 0.788, precision 0.630, recall 0.347, F1 0.447, ROC-AUC 0.789.
- Training 5-fold ROC-AUC: Logistic Regression 0.774; depth-3 tree 0.678; random forest 0.747; tuned forest 0.767.
- Out-of-fold training threshold 0.35: precision 0.513, recall 0.467, F1 0.489, 154 flagged.
- Final held-out test at 0.35: precision 0.571, recall 0.571, ROC-AUC 0.789, 49 flagged.

**Interpretation:** in the fitted scaled Logistic Regression model, the `reminder_sent` coefficient is about -0.581. `exp(coef)` is about 0.560 per one standard deviation; the No→Yes change is `exp(coef / scale)` ≈ 0.309. This is an observational association, not evidence that reminders cause a 69% reduction.

### 4. Google Colab — Part 4

1. Create a free API key in Google AI Studio.
2. Open `04_genai.ipynb` in Colab and run it after Parts 1 and 3.
3. Enter the key only when prompted. Never put it in a code cell, notebook output, `.env` file or GitHub.
4. If the configured Flash model is unavailable in your AI Studio account, change `MODEL_NAME` to a currently available Flash model.
5. The notebook uses `gemini-3.8-flash`, JSON response schema, and Pydantic validation. It retries transient 429/503 service errors with exponential backoff. It skips blank N004 without an API call, preserves raw responses, tests invalid replies, compares V1 and CRAFT prompts on N007/N009, and writes `outputs/notes_analysed.csv`.
6. The final merge uses `all_appointment_risk_scores.csv` so note appointments can be joined to out-of-fold/test risk scores. Retain `final_recommendations.csv`.
7. If Google AI Studio returns repeated 503 errors, do not invent Gemini results or expose your API key. Keep the generated error status/raw error in the output, document the temporary service limitation, and submit the rest of the reproducible pipeline. Retry Part 4 later if the service recovers.

The checked-in `notes_analysed.csv` is a clearly marked `pending_api` scaffold for the nine nonblank notes. No Gemini response has been fabricated. It is **not a completed Part 4 result** until successful Gemini calls produce validated outputs.

## Final business recommendation

The 22.0% overall no-show rate represents 218 missed appointments in the cleaned six-month dataset. Booking far ahead is a strong operational signal: the no-show rate rises from 16.2% for 1–7 day lead times to 60.5% for 31+ days. The model selected by training-only cross-validation is Logistic Regression (ROC-AUC 0.774), with a 0.35 threshold that raises test recall to 0.571 and flags 49 of 198 test bookings. CareLoop should use the risk list to prioritize evening-before calls, with particular attention to long-lead bookings, and use the validated note categories to tailor reminders, transport support, fee clarification, empathetic rescheduling and alternate work-friendly slots. The final action threshold should be calibrated to the front desk's actual call capacity and the value of an unused doctor slot. The first 10 notes are a small illustration, not a clinic-wide estimate; their actual root-cause distribution must be filled from the Gemini run.

## Limitations

1. Only the first 10 notes are analysed because of the free-tier/API exercise; they cannot represent clinic-wide reasons.
2. Cleaning medians, quartiles and outlier fences were calculated on all 990 rows before the train/test split, so test data had a small indirect influence on preprocessing.
3. The same patient may appear in both train and test.
4. The split is random rather than a past-to-future validation.
5. The threshold depends on the front desk's evening call capacity.
6. Clinic-level percentages have different sample sizes; small clinics can show unstable rates.
7. The data are observational; associations are not causes.

## Requirements

Install the Python packages in `requirements.txt` in Colab if needed. MySQL Workbench requires a local MySQL 8 server; SQLiteOnline is the permitted fallback.

## Submission checklist

- [ ] Run Part 1 and replace the weather/cleaning outputs with fresh outputs.
- [ ] Run Part 2 in MySQL Workbench or SQLiteOnline and verify 8 clinics, 990 appointments and 218 no-shows.
- [ ] Run Part 3 and replace `test_risk_scores.csv`.
- [ ] Run Part 4 with a free Gemini API key and replace the pending notes scaffold (currently blocked by intermittent Gemini 503 service errors in this run).
- [ ] Confirm no API key appears anywhere in notebook cells or outputs.
- [ ] Create a **public** GitHub repository and upload the complete folder.
- [ ] Submit only the public repository URL.
