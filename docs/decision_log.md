# Decision Log – RTO Prevention System

**Project:** RTO Prevention System  
**Author:** Keerthi   
**Date:** 31 October 2026

## 1. Decision-Making Approach

The system uses a Random Forest machine-learning model to estimate the probability of an order becoming a Return-to-Origin (RTO).

The predicted risk percentage is compared with configurable thresholds in `config.json` to recommend an action.

## 2. Decision Rules

| RTO Risk | Decision | Reason |
|---|---|---|
| Below 20% | Ship as-is | Low predicted RTO risk |
| 20% to below 50% | Nudge to prepaid | Encourage prepaid payment to reduce COD exposure |
| 50% to below 70% | Ship after confirmation | Verify customer intent through WhatsApp |
| 70% and above | Hold for manual review | High predicted risk requires additional verification |

Automatic cancellation is disabled. High-risk orders are flagged for human review.

## 3. Configuration

The following settings are maintained in `config.json`:

- Ship threshold: 20%
- Prepaid threshold: 50%
- Hold threshold: 70%
- Prepaid discount: ₹20
- WhatsApp confirmation timeout: 24 hours
- Automatic cancellation: Disabled

These values can be changed without modifying the main decision logic.

## 4. Example Decision

**Test Order ID:** TEST1001

| Field | Value |
|---|---|
| Order value | ₹649 |
| Customer prior orders | 0 |
| Customer prior RTOs | 0 |
| Predicted RTO risk | 30.95% |
| Recommended action | Nudge to prepaid |
| Prepaid discount | ₹20 |

**Reason:** The model estimated a 30.95% RTO risk. Since this falls within the 20%–50% range, the system recommends encouraging the customer to pay online.

## 5. WhatsApp Decision Handling

The mock WhatsApp workflow supports:

- YES: Customer confirms the order.
- NO: Customer declines the order.
- Invalid response: The system requests a valid response.
- No response: A timeout scenario is simulated after 24 hours.
- Prepaid acceptance: A simulated payment link is provided, followed by a simulated successful payment option.

This is a demonstration workflow and does not connect to the real WhatsApp Business API.

## 6. Human Review Policy

Orders with predicted RTO risk of 70% or higher are held for manual review. This avoids automatically rejecting genuine customers based only on model predictions.

Incomplete or suspicious address details may also require verification.

## 7. Important Limitations

- Model predictions are estimates, not guarantees.
- Historical patterns do not establish causation.
- Financial impact depends on business assumptions.
- Customer responses and payment outcomes are simulated in the current prototype.
- Actual performance must be monitored after integration with live order data.

## Conclusion

The decision engine combines machine-learning predictions with configurable business rules to support consistent COD order handling while retaining human oversight for high-risk orders.