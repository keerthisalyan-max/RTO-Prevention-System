
import streamlit as st
import time

st.set_page_config(
    page_title="WhatsApp Simulator",
    page_icon="💬",
    layout="centered"
)

st.title("💬 WhatsApp Order Communication")
st.caption("Mock WhatsApp API – RTO Prevention System")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "status" not in st.session_state:
    st.session_state.status = "Waiting for customer"

if "flow_started" not in st.session_state:
    st.session_state.flow_started = False

if "flow_type" not in st.session_state:
    st.session_state.flow_type = ""

if "payment_pending" not in st.session_state:
    st.session_state.payment_pending = False

# Order details
st.subheader("Order Details")

order_id = st.text_input("Order ID", "TEST1001")
customer = st.text_input("Customer Name", "Rahul")
order_value = st.number_input(
    "Order Value (₹)",
    min_value=1,
    value=649
)

action = st.selectbox(
    "Select Decision Engine Action",
    [
        "Ship after confirmation",
        "Nudge to prepaid",
        "Ship as-is",
        "Hold / Cancel"
    ]
)

language = st.selectbox(
    "Message Language",
    ["English", "Hinglish"]
)

discount = 20

# Start WhatsApp flow
if st.button("Start WhatsApp Flow", type="primary"):

    st.session_state.messages = []
    st.session_state.payment_pending = False
    st.session_state.flow_started = True

    if action == "Ship after confirmation":

        st.session_state.flow_type = "confirmation"
        st.session_state.status = "Waiting for confirmation"

        if language == "English":
            message = (
                f"Hi {customer}! Thank you for ordering from us. "
                f"Your order {order_id} worth ₹{order_value} is ready. "
                "Please reply YES to confirm delivery or NO to cancel."
            )
        else:
            message = (
                f"Hi {customer}! Aapke order {order_id} ki value "
                f"₹{order_value} hai. Delivery confirm karne ke liye "
                "YES reply karein, cancel karne ke liye NO reply karein."
            )

    elif action == "Nudge to prepaid":

        st.session_state.flow_type = "prepaid"
        st.session_state.status = "Waiting for prepaid response"

        if language == "English":
            message = (
                f"Hi {customer}! Pay online for order {order_id} "
                f"and get ₹{discount} OFF. "
                f"Original price: ₹{order_value}. "
                f"Prepaid price: ₹{order_value - discount}. "
                "Reply YES to receive a payment link."
            )
        else:
            message = (
                f"Hi {customer}! Order {order_id} par online payment "
                f"karne par ₹{discount} OFF milega. "
                f"New price ₹{order_value - discount}. "
                "Payment link ke liye YES reply karein."
            )

    elif action == "Ship as-is":

        st.session_state.flow_type = "none"
        st.session_state.status = "Approved for shipping"
        message = "Order approved. No confirmation required."

    else:

        st.session_state.flow_type = "none"
        st.session_state.status = "Held for manual review"
        message = "Order placed on hold for manual review."

    st.session_state.messages.append({
        "sender": "Business",
        "message": message
    })


# Display conversation
if st.session_state.flow_started:

    st.divider()
    st.subheader("WhatsApp Conversation")

    for item in st.session_state.messages:

        if item["sender"] == "Business":
            st.info("🏪 Business: " + item["message"])
        else:
            st.success("👤 Customer: " + item["message"])

    st.write("Current Status:", st.session_state.status)

    # Customer response
    if st.session_state.flow_type in [
        "confirmation", "prepaid"
    ] and not st.session_state.payment_pending:

        response = st.text_input(
            "Enter Customer Response",
            placeholder="Type YES, NO or anything else",
            key="customer_reply"
        )

        if st.button("Send Customer Reply"):

            reply = response.strip().upper()

            if not reply:
                st.warning("Please enter a response.")
            else:

                st.session_state.messages.append({
                    "sender": "Customer",
                    "message": response
                })

                if reply in ["YES", "Y"]:

                    if st.session_state.flow_type == "confirmation":

                        st.session_state.status = "Confirmed – Ready to ship"

                        reply_message = (
                            "Thank you! Your order is confirmed "
                            "and will be shipped shortly."
                        )

                    else:

                        st.session_state.payment_pending = True
                        st.session_state.status = "Payment link sent"

                        reply_message = (
                            f"Thank you! Mock payment link generated "
                            f"for ₹{order_value - discount}. "
                            "Please complete your payment."
                        )

                elif reply in ["NO", "N"]:

                    if st.session_state.flow_type == "confirmation":

                        st.session_state.status = "Cancelled by customer"

                        reply_message = (
                            "Your order has been cancelled as requested."
                        )

                    else:

                        st.session_state.status = (
                            "Prepaid declined – Confirmation required"
                        )

                        reply_message = (
                            "No problem! Would you still like the order "
                            "on Cash on Delivery? Reply YES to confirm "
                            "or NO to cancel."
                        )

                        st.session_state.flow_type = "confirmation"

                else:

                    st.session_state.status = "Waiting for valid response"

                    reply_message = (
                        "Sorry, we couldn't understand your response. "
                        "Please reply YES or NO."
                    )

                st.session_state.messages.append({
                    "sender": "Business",
                    "message": reply_message
                })

                st.rerun()

    # Simulate payment
    if st.session_state.payment_pending:

        if st.button("Simulate Successful Payment"):

            st.session_state.payment_pending = False
            st.session_state.status = "Prepaid – Approved for shipping"

            st.session_state.messages.append({
                "sender": "Business",
                "message": "Payment received successfully! Your order is approved for shipping."
            })

            st.rerun()

    # Simulate 24-hour timeout
    if st.session_state.flow_type in [
        "confirmation", "prepaid"
    ] and st.session_state.status not in [
        "Confirmed – Ready to ship",
        "Cancelled by customer",
        "Prepaid – Approved for shipping",
        "Payment link sent",
        "Held after timeout"
    ]:

        if st.button("Simulate 24-Hour Timeout"):

            st.session_state.status = "Held after timeout"

            st.session_state.messages.append({
                "sender": "Business",
                "message": (
                    "We did not receive your response within 24 hours. "
                    "Your order has been placed on hold for manual review."
                )
            })

            st.rerun()

    # Reset
    if st.button("Reset Simulator"):

        st.session_state.messages = []
        st.session_state.status = "Waiting for customer"
        st.session_state.flow_started = False
        st.session_state.flow_type = ""
        st.session_state.payment_pending = False

        st.rerun()
