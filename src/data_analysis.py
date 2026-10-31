
import pandas as pd
import numpy as np

# 1. Load dataset
df = pd.read_csv("data/orders_sample.csv")

print("ORIGINAL DATASET SHAPE:", df.shape)

# 2. Remove exact duplicate records
df = df.drop_duplicates()

# 3. Normalize status values
df["final_status"] = (
    df["final_status"].astype(str).str.strip().str.upper()
)

# 4. Keep only completed orders
df = df[df["final_status"].isin(["DELIVERED", "RTO"])].copy()

# 5. Create target column
# 1 = RTO, 0 = Delivered
df["is_rto"] = (df["final_status"] == "RTO").astype(int)

# 6. Display basic information
print("\nCLEANED DATASET SHAPE:", df.shape)

print("\nORDER STATUS:")
print(df["final_status"].value_counts())

# 7. Calculate overall RTO rate
rto_rate = df["is_rto"].mean() * 100

print("\nOVERALL RTO RATE:", round(rto_rate, 2), "%")

# 8. Analyse customer history
print("\nRTO RATE BY PREVIOUS ORDERS:")
print(
    df.groupby("customer_prior_orders")["is_rto"]
    .agg(["count", "mean"])
)

# 9. Analyse previous RTO history
print("\nRTO RATE BY PREVIOUS RTO COUNT:")
print(
    df.groupby("customer_prior_rto")["is_rto"]
    .agg(["count", "mean"])
)

# 10. Analyse city-wise RTO
print("\nCITY-WISE RTO RATE:")
city_analysis = (
    df.groupby("city")["is_rto"]
    .agg(["count", "mean"])
)

city_analysis = city_analysis[city_analysis["count"] >= 20]
city_analysis["rto_percentage"] = (
    city_analysis["mean"] * 100
).round(2)

print(city_analysis.sort_values(
    "rto_percentage", ascending=False
))

# 11. Analyse address length
df["address_length"] = df["address"].fillna("").str.len()

df["address_category"] = pd.cut(
    df["address_length"],
    bins=[-1, 15, 30, 60, float("inf")],
    labels=["Very Short", "Short", "Medium", "Long"]
)

print("\nADDRESS-WISE RTO RATE:")
print(
    df.groupby("address_category", observed=True)["is_rto"]
    .agg(["count", "mean"])
)

# 12. Missing values
print("\nMISSING VALUES:")
print(df.isnull().sum())

# 13. Save cleaned dataset
df.to_csv("data/cleaned_orders.csv", index=False)

print("\nAnalysis completed successfully!")
print("Cleaned dataset saved.")
