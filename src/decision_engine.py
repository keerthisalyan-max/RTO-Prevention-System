
import json
import re
import joblib
import pandas as pd
import numpy as np

# Load trained ML model
model = joblib.load("models/rto_model.pkl")

# Load business rules
with open("config.json", "r") as file:
    config = json.load(file)


def get_pincode_prefix(pincode):
    """Extract first three digits of the pincode."""

    if pd.isna(pincode):
        return np.nan

    digits = re.sub(r"\D", "", str(pincode))

    if len(digits) < 3:
        return np.nan

    return digits[:3]


def validate_address(address):
    """
    Basic rule-based address validation.
    LLM-based language understanding can be added separately.
    """

    address = str(address).strip().lower()

    suspicious_values = [
        "asdf",
        "test",
        "xyz",
        "call me",
        ".",
        "unknown"
    ]

    if not address:
        return False, "Address is missing."

    if address in suspicious_values or len(address) <= 3:
        return False, "Address appears incomplete or suspicious."

    if len(address) <= 15:
        return True, "Address is very short; verify delivery details."

    return True, "Address passed basic validation."


def decide_order(order):

    # 1. Prepare input features
    order_datetime = pd.to_datetime(
        order["order_datetime"],
        dayfirst=True,
        errors="coerce"
    )

    if pd.isna(order_datetime):
        raise ValueError("Invalid order date/time.")

    address = str(order.get("address", "") or "")

    address_length = len(address.strip())

    address_valid, address_reason = validate_address(address)

    # 2. Create input in the same format as training data
    input_data = pd.DataFrame([{
        "city": order.get("city"),
        "state": order.get("state"),
        "pincode_prefix": get_pincode_prefix(
            order.get("pincode")
        ),
        "order_value": float(order["order_value"]),
        "num_items": int(order["num_items"]),
        "customer_prior_orders": int(
            order["customer_prior_orders"]
        ),
        "customer_prior_rto": int(
            order["customer_prior_rto"]
        ),
        "utm_source": order.get("utm_source"),
        "courier": order.get("courier"),
        "order_month": order_datetime.month,
        "order_hour": order_datetime.hour,
        "order_dayofweek": order_datetime.day_of_week,
        "address_length": address_length,
        "address_very_short": int(address_length <= 15)
    }])

    # 3. Predict RTO probability
    rto_probability = model.predict_proba(
        input_data
    )[0][1]

    risk_percentage = round(rto_probability * 100, 2)

    # 4. Generate understandable warning reasons
    reasons = [
        f"Model estimated RTO risk: {risk_percentage}%."
    ]

    if int(order["customer_prior_rto"]) >= 1:
        reasons.append(
            "Customer has previous RTO history."
        )

    if int(order["customer_prior_rto"]) >= 2:
        reasons.append(
            "Customer has multiple previous RTOs."
        )

    if address_length <= 15:
        reasons.append(address_reason)

    if not address_valid:
        reasons.append(
            "Manual address verification is recommended."
        )


    
    # 5. Apply editable business thresholds
    if risk_percentage < config["ship_threshold"]:

        action = "Ship as-is"

    elif risk_percentage < config["prepaid_threshold"]:

        action = "Nudge to prepaid"

    elif risk_percentage < config["hold_threshold"]:

        action = "Ship after confirmation"

    else:

        action = "Hold / Cancel (Manual Review)"


    # 6. Return decision
    return {
        "order_id": order.get("order_id", "NEW_ORDER"),
        "rto_probability": risk_percentage,
        "action": action,
        "reasons": reasons,
        "prepaid_discount": config["prepaid_discount"],
        "address_valid": address_valid
    }


# Test the decision engine
if __name__ == "__main__":

    sample_order = {
        "order_id": "TEST1001",
        "order_datetime": "31-10-2026 10:30",
        "customer_name": "Rahul Sharma",
        "address": "House 21, MG Road, Near SBI Bank",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        "order_value": 649,
        "num_items": 2,
        "customer_prior_orders": 0,
        "customer_prior_rto": 0,
        "utm_source": "meta_ads",
        "courier": "Delhivery"
    }

    result = decide_order(sample_order)

    print("\n========== ORDER DECISION ==========")

    print("Order ID:", result["order_id"])
    print("RTO Risk:", result["rto_probability"], "%")
    print("Action:", result["action"])

    print("\nReasons:")

    for reason in result["reasons"]:
        print("-", reason)

    print("\nPrepaid Discount: ₹", result["prepaid_discount"])

    print("====================================")
