
# import json
# from pathlib import Path
# from datetime import date

# import joblib
# import numpy as np
# import pandas as pd
# import streamlit as st


# # -----------------------------
# # PAGE CONFIGURATION
# # -----------------------------
# st.set_page_config(
#     page_title="RTO Prevention Dashboard",
#     page_icon="📊",
#     layout="wide"
# )

# st.title("📊 RTO Prevention System")
# st.caption("Founder Dashboard | Historical Sample Data Simulation")

# ROOT = Path(__file__).resolve().parent.parent

# MODEL_PATH = ROOT / "models" / "rto_model.pkl"
# DATA_PATH = ROOT / "data" / "cleaned_orders.csv"
# CONFIG_PATH = ROOT / "config.json"


# # -----------------------------
# # BUSINESS ASSUMPTIONS
# # -----------------------------
# RTO_COST = 169.40
# GROSS_PROFIT_PER_ORDER = 649 * 0.62

# COD_RTO_RATE = 0.28
# PREPAID_RTO_RATE = 0.04
# PREPAID_DISCOUNT = 20


# # -----------------------------
# # LOAD MODEL AND DATA
# # -----------------------------
# @st.cache_resource
# def load_model():
#     return joblib.load(MODEL_PATH)


# @st.cache_data
# def load_data():
#     return pd.read_csv(DATA_PATH)


# model = load_model()
# df = load_data()

# with open(CONFIG_PATH, "r") as file:
#     config = json.load(file)


# # -----------------------------
# # PREPARE MODEL FEATURES
# # -----------------------------
# df["order_datetime"] = pd.to_datetime(
#     df["order_datetime"],
#     dayfirst=True,
#     errors="coerce"
# )

# df["order_month"] = df["order_datetime"].dt.month
# df["order_hour"] = df["order_datetime"].dt.hour
# df["order_dayofweek"] = df["order_datetime"].dt.dayofweek

# df["address"] = df["address"].fillna("").astype(str)
# df["address_length"] = df["address"].str.len()
# df["address_very_short"] = (
#     df["address_length"] <= 15
# ).astype(int)

# df["pincode_prefix"] = (
#     df["pincode"]
#     .fillna("")
#     .astype(str)
#     .str.extract(r"(\d{3})", expand=False)
# )

# feature_columns = [
#     "city",
#     "state",
#     "pincode_prefix",
#     "order_value",
#     "num_items",
#     "customer_prior_orders",
#     "customer_prior_rto",
#     "utm_source",
#     "courier",
#     "order_month",
#     "order_hour",
#     "order_dayofweek",
#     "address_length",
#     "address_very_short"
# ]

# # Ensure all expected model columns exist
# for column in feature_columns:
#     if column not in df.columns:
#         df[column] = np.nan

# X = df[feature_columns].copy()

# df["rto_risk"] = model.predict_proba(X)[:, 1] * 100


# # -----------------------------
# # ASSIGN DECISION CATEGORIES
# # -----------------------------
# ship_threshold = config["ship_threshold"]
# prepaid_threshold = config["prepaid_threshold"]
# hold_threshold = config["hold_threshold"]


# def assign_action(risk):
#     if risk < ship_threshold:
#         return "Ship as-is"
#     elif risk < confirm_threshold:
#         return "Ship after confirmation"
#     elif risk < prepaid_threshold:
#         return "Nudge to prepaid"
#     else:
#         return "Hold / Cancel"


# df["decision"] = df["rto_risk"].apply(assign_action)


# # -----------------------------
# # SIDEBAR DATE FILTER
# # -----------------------------
# st.sidebar.header("Dashboard Filters")

# valid_dates = df["order_datetime"].dropna()

# if valid_dates.empty:
#     st.error("No valid order dates found in the dataset.")
#     st.stop()

# min_date = valid_dates.min().date()
# max_date = valid_dates.max().date()

# selected_date = st.sidebar.date_input(
#     "Select sample date",
#     value=max_date,
#     min_value=min_date,
#     max_value=max_date
# )

# daily_df = df[
#     df["order_datetime"].dt.date == selected_date
# ].copy()

# st.subheader(f"Order Summary – {selected_date}")

# if daily_df.empty:
#     st.warning("No orders are available for this date.")
#     st.stop()

# st.info(
#     "Demo dashboard: figures are calculated from the historical "
#     "sample dataset and model predictions. They are not live Shopify "
#     "orders or verified actual savings."
# )


# # -----------------------------
# # ORDER COUNTS
# # -----------------------------
# total_orders = len(daily_df)

# ship_count = (
#     daily_df["decision"] == "Ship as-is"
# ).sum()

# confirm_count = (
#     daily_df["decision"] == "Ship after confirmation"
# ).sum()

# prepaid_count = (
#     daily_df["decision"] == "Nudge to prepaid"
# ).sum()

# hold_count = (
#     daily_df["decision"] == "Hold / Cancel"
# ).sum()


# # -----------------------------
# # DISPLAY METRICS
# # -----------------------------
# col1, col2, col3, col4, col5 = st.columns(5)

# col1.metric("Total Orders", total_orders)
# col2.metric("Ship As-is", ship_count)
# col3.metric("Confirmation", confirm_count)
# col4.metric("Prepaid Nudge", prepaid_count)
# col5.metric("Hold / Cancel", hold_count)


# # -----------------------------
# # FINANCIAL IMPACT ESTIMATION
# # -----------------------------

# # -----------------------------
# # FINANCIAL IMPACT ESTIMATION
# # -----------------------------
# st.divider()
# st.subheader("Estimated Financial Impact")

# st.sidebar.subheader("Financial Assumptions")

# conversion_rate = st.sidebar.slider(
#     "Assumed prepaid conversion rate (%)",
#     min_value=0,
#     max_value=100,
#     value=30
# ) / 100

# # Business assumptions
# RTO_COST = 169.40
# GROSS_MARGIN = 0.62
# COD_RTO_RATE = 0.28
# PREPAID_RTO_RATE = 0.04
# PREPAID_DISCOUNT = 20

# # 1. Orders held for manual review
# held_orders = daily_df[
#     daily_df["decision"] == "Hold / Cancel"
# ].copy()

# # Expected RTOs among held orders
# expected_rtos_avoided = (
#     held_orders["rto_risk"] / 100
# ).sum()

# # Expected RTO cost avoided if held orders are not shipped
# potential_rto_savings = (
#     expected_rtos_avoided * RTO_COST
# )

# # 2. Potential genuine orders among held orders
# expected_genuine_orders = (
#     1 - held_orders["rto_risk"] / 100
# ).sum()

# # Estimate contribution at risk using actual order values
# potential_lost_contribution = (
#     (held_orders["order_value"] * GROSS_MARGIN)
#     * (1 - held_orders["rto_risk"] / 100)
# ).sum()

# # 3. Prepaid conversion estimate
# prepaid_orders = daily_df[
#     daily_df["decision"] == "Nudge to prepaid"
# ]

# expected_prepaid_conversions = (
#     len(prepaid_orders) * conversion_rate
# )

# # Expected RTO cost reduction from COD to prepaid
# prepaid_rto_cost_reduction = (
#     expected_prepaid_conversions
#     * (COD_RTO_RATE - PREPAID_RTO_RATE)
#     * RTO_COST
# )

# # Discount cost for converted orders
# discount_cost = (
#     expected_prepaid_conversions * PREPAID_DISCOUNT
# )

# prepaid_net_benefit = (
#     prepaid_rto_cost_reduction - discount_cost
# )

# # 4. Overall estimated financial impact
# net_impact = (
#     potential_rto_savings
#     + prepaid_net_benefit
#     - potential_lost_contribution
# )

# # Display financial metrics
# f1, f2, f3, f4 = st.columns(4)

# f1.metric(
#     "RTO Savings",
#     f"₹{potential_rto_savings:,.2f}"
# )

# f2.metric(
#     "Discount Cost",
#     f"₹{discount_cost:,.2f}"
# )

# f3.metric(
#     "Contribution at Risk",
#     f"₹{potential_lost_contribution:,.2f}"
# )

# f4.metric(
#     "Net Impact",
#     f"₹{net_impact:,.2f}"
# )

# st.divider()

# st.subheader("Additional Impact Estimates")

# a1, a2, a3 = st.columns(3)

# a1.metric(
#     "Expected RTOs Avoided",
#     f"{expected_rtos_avoided:.2f}"
# )

# a2.metric(
#     "Genuine Orders at Risk",
#     f"{expected_genuine_orders:.2f}"
# )

# a3.metric(
#     "Prepaid Net Benefit",
#     f"₹{prepaid_net_benefit:,.2f}"
# )

# st.caption(
#     "These are estimates, not verified savings. They assume held orders "
#     "are not shipped and use predicted RTO probabilities. Prepaid "
#     "conversion is based on the adjustable assumption. Contribution "
#     "at risk is estimated using order value and gross margin."
# )


# # -----------------------------
# # ACTUAL HISTORICAL OUTCOMES
# # -----------------------------
# st.divider()
# st.subheader("Historical Order Outcomes")

# if "final_status" in daily_df.columns:
#     outcome_counts = (
#         daily_df["final_status"]
#         .astype(str)
#         .str.upper()
#         .value_counts()
#     )

#     o1, o2, o3 = st.columns(3)

#     delivered = outcome_counts.get("DELIVERED", 0)
#     rto = outcome_counts.get("RTO", 0)

#     o1.metric("Delivered", delivered)
#     o2.metric("RTO Orders", rto)

#     actual_rto_rate = (
#         (rto / (delivered + rto)) * 100
#         if delivered + rto > 0 else 0
#     )

#     o3.metric("Historical RTO Rate", f"{actual_rto_rate:.2f}%")


# # -----------------------------
# # DECISION DISTRIBUTION
# # -----------------------------
# st.divider()
# st.subheader("Decision Distribution")

# decision_counts = (
#     daily_df["decision"]
#     .value_counts()
#     .reindex(
#         [
#             "Ship as-is",
#             "Ship after confirmation",
#             "Nudge to prepaid",
#             "Hold / Cancel"
#         ],
#         fill_value=0
#     )
# )

# st.bar_chart(decision_counts)

# # -----------------------------
# # ORDER DECISION LOG
# # -----------------------------
# st.divider()
# st.subheader("Order-Level Decision Log")

# display_columns = [
#     "order_id",
#     "city",
#     "order_value",
#     "rto_risk",
#     "decision"
# ]

# available_columns = [
#     column for column in display_columns
#     if column in daily_df.columns
# ]

# result_table = daily_df[available_columns].copy()

# result_table["rto_risk"] = (
#     result_table["rto_risk"].round(2).astype(str) + "%"
# )

# st.dataframe(
#     result_table,
#     use_container_width=True,
#     hide_index=True
# )

# st.caption(
#     "High-risk orders are marked for manual review when automatic "
#     "cancellation is disabled in the configuration."
# )



import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="RTO Prevention Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RTO Prevention System")
st.caption("Founder Dashboard | Historical Sample Data Simulation")

ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = ROOT / "models" / "rto_model.pkl"
DATA_PATH = ROOT / "data" / "cleaned_orders.csv"
CONFIG_PATH = ROOT / "config.json"


# -----------------------------
# BUSINESS ASSUMPTIONS
# -----------------------------
RTO_COST = 169.40
GROSS_MARGIN = 0.62
COD_RTO_RATE = 0.28
PREPAID_RTO_RATE = 0.04
PREPAID_DISCOUNT = 20

HOLD_ACTION = "Hold / Cancel (Manual Review)"


# -----------------------------
# LOAD MODEL AND DATA
# -----------------------------
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


model = load_model()
df = load_data()

with open(CONFIG_PATH, "r") as file:
    config = json.load(file)


# -----------------------------
# PREPARE MODEL FEATURES
# -----------------------------
df["order_datetime"] = pd.to_datetime(
    df["order_datetime"],
    dayfirst=True,
    errors="coerce"
)

df["order_month"] = df["order_datetime"].dt.month
df["order_hour"] = df["order_datetime"].dt.hour
df["order_dayofweek"] = df["order_datetime"].dt.dayofweek

df["address"] = df["address"].fillna("").astype(str)
df["address_length"] = df["address"].str.len()

df["address_very_short"] = (
    df["address_length"] <= 15
).astype(int)

df["pincode_prefix"] = (
    df["pincode"]
    .fillna("")
    .astype(str)
    .str.extract(r"(\d{3})", expand=False)
)

feature_columns = [
    "city",
    "state",
    "pincode_prefix",
    "order_value",
    "num_items",
    "customer_prior_orders",
    "customer_prior_rto",
    "utm_source",
    "courier",
    "order_month",
    "order_hour",
    "order_dayofweek",
    "address_length",
    "address_very_short"
]

for column in feature_columns:
    if column not in df.columns:
        df[column] = np.nan

X = df[feature_columns].copy()

df["rto_risk"] = model.predict_proba(X)[:, 1] * 100


# -----------------------------
# ASSIGN DECISION CATEGORIES
# -----------------------------
ship_threshold = config["ship_threshold"]
prepaid_threshold = config["prepaid_threshold"]
hold_threshold = config["hold_threshold"]


def assign_action(risk):

    if risk < ship_threshold:
        return "Ship as-is"

    elif risk < prepaid_threshold:
        return "Nudge to prepaid"

    elif risk < hold_threshold:
        return "Ship after confirmation"

    else:
        return HOLD_ACTION


df["decision"] = df["rto_risk"].apply(assign_action)


# -----------------------------
# SIDEBAR DATE FILTER
# -----------------------------
st.sidebar.header("Dashboard Filters")

valid_dates = df["order_datetime"].dropna()

if valid_dates.empty:
    st.error("No valid order dates found in the dataset.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

selected_date = st.sidebar.date_input(
    "Select sample date",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

daily_df = df[
    df["order_datetime"].dt.date == selected_date
].copy()

st.subheader(f"Order Summary – {selected_date}")

if daily_df.empty:
    st.warning("No orders are available for this date.")
    st.stop()

st.info(
    "Demo dashboard: figures are calculated from historical sample "
    "data and model predictions. They are not live Shopify orders "
    "or verified actual savings."
)


# -----------------------------
# ORDER COUNTS
# -----------------------------
total_orders = len(daily_df)

ship_count = (
    daily_df["decision"] == "Ship as-is"
).sum()

prepaid_count = (
    daily_df["decision"] == "Nudge to prepaid"
).sum()

confirm_count = (
    daily_df["decision"] == "Ship after confirmation"
).sum()

hold_count = (
    daily_df["decision"] == HOLD_ACTION
).sum()


# -----------------------------
# DISPLAY ORDER METRICS
# -----------------------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Orders", total_orders)
col2.metric("Ship As-is", ship_count)
col3.metric("Prepaid Nudge", prepaid_count)
col4.metric("Confirmation", confirm_count)
col5.metric("Hold / Review", hold_count)


# -----------------------------
# FINANCIAL IMPACT ESTIMATION
# -----------------------------
st.divider()
st.subheader("Estimated Financial Impact")

st.sidebar.subheader("Financial Assumptions")

conversion_rate = st.sidebar.slider(
    "Assumed prepaid conversion rate (%)",
    min_value=0,
    max_value=100,
    value=30
) / 100


# 1. Orders held for manual review
held_orders = daily_df[
    daily_df["decision"] == HOLD_ACTION
].copy()

expected_rtos_avoided = (
    held_orders["rto_risk"] / 100
).sum()

potential_rto_savings = (
    expected_rtos_avoided * RTO_COST
)


# 2. Potential genuine orders among held orders
expected_genuine_orders = (
    1 - held_orders["rto_risk"] / 100
).sum()

potential_lost_contribution = (
    held_orders["order_value"]
    * GROSS_MARGIN
    * (1 - held_orders["rto_risk"] / 100)
).sum()


# 3. Prepaid conversion estimate
prepaid_orders = daily_df[
    daily_df["decision"] == "Nudge to prepaid"
]

expected_prepaid_conversions = (
    len(prepaid_orders) * conversion_rate
)

prepaid_rto_cost_reduction = (
    expected_prepaid_conversions
    * (COD_RTO_RATE - PREPAID_RTO_RATE)
    * RTO_COST
)

discount_cost = (
    expected_prepaid_conversions * PREPAID_DISCOUNT
)

prepaid_net_benefit = (
    prepaid_rto_cost_reduction - discount_cost
)


# 4. Overall estimated financial impact
net_impact = (
    potential_rto_savings
    + prepaid_net_benefit
    - potential_lost_contribution
)


# -----------------------------
# DISPLAY FINANCIAL METRICS
# -----------------------------
f1, f2, f3, f4 = st.columns(4)

f1.metric(
    "RTO Savings",
    f"₹{potential_rto_savings:,.2f}"
)

f2.metric(
    "Discount Cost",
    f"₹{discount_cost:,.2f}"
)

f3.metric(
    "Contribution at Risk",
    f"₹{potential_lost_contribution:,.2f}"
)

f4.metric(
    "Net Impact",
    f"₹{net_impact:,.2f}"
)


# -----------------------------
# ADDITIONAL IMPACT ESTIMATES
# -----------------------------
st.divider()
st.subheader("Additional Impact Estimates")

a1, a2, a3 = st.columns(3)

a1.metric(
    "Expected RTOs Avoided",
    f"{expected_rtos_avoided:.2f}"
)

a2.metric(
    "Genuine Orders at Risk",
    f"{expected_genuine_orders:.2f}"
)

a3.metric(
    "Prepaid Net Benefit",
    f"₹{prepaid_net_benefit:,.2f}"
)

st.caption(
    "These are estimates, not verified savings. They assume held "
    "orders are not shipped and use predicted RTO probabilities. "
    "Prepaid conversion is based on the adjustable assumption. "
    "Contribution at risk is estimated using order value and "
    "gross margin."
)


# -----------------------------
# ACTUAL HISTORICAL OUTCOMES
# -----------------------------
st.divider()
st.subheader("Historical Order Outcomes")

if "final_status" in daily_df.columns:

    outcome_counts = (
        daily_df["final_status"]
        .astype(str)
        .str.upper()
        .value_counts()
    )

    delivered = outcome_counts.get("DELIVERED", 0)
    rto = outcome_counts.get("RTO", 0)

    o1, o2, o3 = st.columns(3)

    o1.metric("Delivered", delivered)
    o2.metric("RTO Orders", rto)

    actual_rto_rate = (
        (rto / (delivered + rto)) * 100
        if delivered + rto > 0 else 0
    )

    o3.metric(
        "Historical RTO Rate",
        f"{actual_rto_rate:.2f}%"
    )


# -----------------------------
# DECISION DISTRIBUTION
# -----------------------------
st.divider()
st.subheader("Decision Distribution")

decision_counts = (
    daily_df["decision"]
    .value_counts()
    .reindex(
        [
            "Ship as-is",
            "Nudge to prepaid",
            "Ship after confirmation",
            HOLD_ACTION
        ],
        fill_value=0
    )
)

st.bar_chart(decision_counts)


# -----------------------------
# ORDER-LEVEL DECISION LOG
# -----------------------------
st.divider()
st.subheader("Order-Level Decision Log")

display_columns = [
    "order_id",
    "city",
    "order_value",
    "rto_risk",
    "decision"
]

available_columns = [
    column for column in display_columns
    if column in daily_df.columns
]

result_table = daily_df[available_columns].copy()

result_table["rto_risk"] = (
    result_table["rto_risk"].round(2).astype(str) + "%"
)

st.dataframe(
    result_table,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "High-risk orders are flagged for manual review. "
    "Automatic cancellation is disabled in the configuration."
)
