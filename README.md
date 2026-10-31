# RTO Prevention System

An ML-powered Return-to-Origin (RTO) Prevention System designed for a Direct-to-Consumer (D2C) e-commerce store. It predicts the likelihood of Cash-on-Delivery (COD) orders being returned and recommends suitable actions to reduce potential RTO losses.

## Project Overview

The system uses a Random Forest machine-learning model to estimate RTO risk and a configurable decision engine to classify orders into four categories:

- Ship as-is
- Nudge to prepaid
- Ship after WhatsApp confirmation
- Hold for manual review

It also includes a mock WhatsApp communication workflow and a Streamlit founder dashboard to visualize order decisions and estimated financial impact.

## Key Features

### 1. RTO Risk Prediction
- Uses historical order data to train a Random Forest model.
- Predicts the probability of an order becoming an RTO.
- Considers customer history, order value, location, courier and address-related features.

### 2. Decision Engine
Uses configurable risk thresholds stored in `config.json`.

| Predicted Risk | Recommended Action |
|---|---|
| Below 20% | Ship as-is |
| 20%–49.99% | Nudge to prepaid |
| 50%–69.99% | WhatsApp confirmation |
| 70% and above | Hold for manual review |

High-risk orders are not automatically cancelled.

### 3. WhatsApp Simulator
- Simulates customer confirmation messages.
- Supports YES, NO and invalid responses.
- Simulates a 24-hour no-response scenario.
- Provides a prepaid payment-link simulation with a ₹20 discount.
- Does not send real WhatsApp messages or process actual payments.

### 4. Founder Dashboard
Built using Streamlit.

Displays:
- Daily order counts by decision category.
- Estimated RTO savings and financial impact.
- Historical delivered and RTO outcomes.
- Decision distribution chart.
- Order-level risk and decision log.
- Adjustable prepaid conversion assumption.

Dashboard results are based on historical sample data and model predictions, not live Shopify orders.

## Technology Stack

- Python
- Pandas and NumPy
- Scikit-learn
- Random Forest Classifier
- Joblib
- Streamlit
- JSON
- CSV

## Project Structure

```text
RTO_Prevention_System/
│
├── data/
│   ├── orders_sample.csv
│   └── cleaned_orders.csv
│
├── docs/
│   └── RTO_Prevention_Business_Memo.pdf
│
├── models/
│   └── rto_model.pkl
│
├── src/
│   ├── data_analysis.py
│   ├── train_model.py
│   ├── decision_engine.py
│   ├── whatsapp_simulator.py
│   └── dashboard.py
│
├── config.json
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd RTO_Prevention_System
```

### 2. Install dependencies

```bash
pip install pandas numpy scikit-learn joblib streamlit
```

### 3. Run the data analysis

```bash
python src/data_analysis.py
```

### 4. Train the machine-learning model

```bash
python src/train_model.py
```

The trained model is saved in the `models` folder.

### 5. Run the decision engine

```bash
python src/decision_engine.py
```

### 6. Launch the WhatsApp simulator

```bash
python -m streamlit run src/whatsapp_simulator.py
```

### 7. Launch the founder dashboard

Open a separate terminal and run:

```bash
python -m streamlit run src/dashboard.py
```

## Configuration

The decision thresholds and business settings can be modified in `config.json`.

```json
{
    "ship_threshold": 20,
    "prepaid_threshold": 50,
    "hold_threshold": 70,
    "prepaid_discount": 20,
    "confirmation_timeout_hours": 24,
    "auto_cancel_high_risk": false
}
```

## Business Assumptions

- Estimated RTO cost: ₹169.40 per order.
- Gross margin: 62%.
- Assumed COD RTO rate: 28%.
- Assumed prepaid RTO rate: 4%.
- Prepaid discount: ₹20.
- Assumed prepaid conversion rate: 30%.

These values are configurable business assumptions used for financial estimation.

## Model Performance

The Random Forest model achieved approximately:

- Accuracy: 73.87%
- ROC-AUC: 0.696

Model predictions are intended to support operational decisions, not replace manual verification. Performance should be monitored as new order data becomes available.

## Limitations

- Uses historical sample data rather than live Shopify integration.
- WhatsApp communication is simulated, not connected to the actual WhatsApp Business API.
- Prepaid payments are simulated, not processed through a payment gateway.
- Financial savings are estimates based on assumptions and predicted risks.
- High-risk orders require manual review.

## Future Enhancements

- Integrate Shopify order webhooks.
- Connect the WhatsApp Business API.
- Integrate a real payment gateway.
- Store customer confirmation and delivery outcomes.
- Improve model performance using continuously updated order data.
- Add automated monitoring and operational alerts.

## Author

**Keerthi**