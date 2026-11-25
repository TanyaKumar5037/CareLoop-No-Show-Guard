"""Reproduce the Part 2 clinic counts and lead-time/month summaries."""
import pandas as pd

appointments = pd.read_csv("appointments_clean.csv")
clinics = pd.read_csv("data/clinics.csv")

clinic_summary = (
    appointments.groupby("clinic_id")
    .agg(appointments=("appointment_id", "count"), no_shows=("no_show", "sum"))
    .reset_index()
    .merge(clinics[["clinic_id", "clinic_name", "city"]], on="clinic_id", how="left")
)
clinic_summary["no_show_pct"] = (100 * clinic_summary["no_shows"] / clinic_summary["appointments"]).round(1)
print("Clinic summary (compare with SQL Task 2.2):")
print(clinic_summary.sort_values("no_show_pct", ascending=False).to_string(index=False))

assert len(appointments) == 990
assert int(appointments["no_show"].sum()) == 218
assert int(clinic_summary["appointments"].sum()) == 990
assert int(clinic_summary["no_shows"].sum()) == 218

lead_summary = (
    appointments.assign(
        lead_band=pd.cut(
            appointments["lead_days"], bins=[0, 7, 14, 30, float("inf")],
            labels=["1-7", "8-14", "15-30", "31+"]
        )
    )
    .groupby("lead_band", observed=False)
    .agg(appointments=("appointment_id", "count"), no_shows=("no_show", "sum"))
    .reset_index()
)
lead_summary["no_show_pct"] = (100 * lead_summary["no_shows"] / lead_summary["appointments"]).round(1)
print("\\nLead-time summary (compare with SQL Task 2.3):")
print(lead_summary.to_string(index=False))

monthly = appointments.assign(month=appointments["appt_date"].str[:7]).groupby("month").agg(
    appointments=("appointment_id", "count"), no_shows=("no_show", "sum")
).reset_index()
monthly["no_show_pct"] = (100 * monthly["no_shows"] / monthly["appointments"]).round(1)
monthly["change_pp"] = monthly["no_show_pct"].diff().round(1)
print("\\nMonthly summary (compare with SQL Task 2.4):")
print(monthly.to_string(index=False))
