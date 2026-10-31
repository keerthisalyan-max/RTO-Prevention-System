# AI Usage Log – RTO Prevention System

**Project:** RTO Prevention System  
**Author:** Keerthi   
**Date:** 31 October 2026

## 1. How AI Was Used

AI assistance was used during development to:

- Understand the assignment requirements and break the work into manageable tasks.
- Assist with Python code structure and debugging.
- Understand Random Forest predictions and model evaluation.
- Develop configurable order-decision rules.
- Build and troubleshoot the Streamlit dashboard.
- Design the mock WhatsApp conversation workflow.
- Review financial assumptions and prepare project documentation.

All generated code and recommendations were reviewed and tested before being included in the project.

## 2. AI Suggestions That Were Reviewed and Corrected

### Example 1: Incorrect Decision Threshold Mapping

**Initial issue:** An earlier suggested decision mapping placed WhatsApp confirmation and prepaid nudges in the wrong risk ranges.

**Correction:** The decision rules were revised to use the agreed thresholds:

- Below 20%: Ship as-is.
- 20%–49.99%: Nudge to prepaid.
- 50%–69.99%: WhatsApp confirmation.
- 70% and above: Hold for manual review.

The same rules were applied to both the decision engine and dashboard.

### Example 2: Incorrect Financial Assumption

**Initial issue:** An early financial explanation used ₹649 as the average order value.

**Correction:** The dataset was reviewed, and its actual average order value was approximately ₹920 overall. September's average was approximately ₹878.40. The financial calculations and business memo were updated to distinguish these values from the ₹649 test order.

### Example 3: Mixing Different Model Results

**Initial issue:** An earlier report combined September simulation results from a separate points-based scorecard with the Random Forest implementation.

**Correction:** The project was kept consistent with the Random Forest model. The September dataset was processed using the trained model and the same 20%, 50% and 70% thresholds used by the dashboard.

## 3. Human Verification and Testing

The following checks were performed:

- Dataset cleaning and analysis outputs were compared with the source data.
- The trained Random Forest model was tested using a sample order.
- The decision engine was checked against the configured thresholds.
- WhatsApp YES, NO, invalid response and prepaid simulation flows were tested.
- Dashboard calculations and decision categories were checked using historical sample orders.
- Configuration errors in the dashboard were corrected and the application was rerun.

## 4. Responsible AI Usage

AI was used as a development assistant, not as the final decision-maker.

Model predictions are treated as estimates. High-risk orders require manual review, and the system does not automatically cancel orders.

Financial calculations are presented as estimates based on stated assumptions rather than guaranteed savings.

## Conclusion

AI assistance improved development speed and helped identify implementation issues. However, generated suggestions were reviewed, corrected where necessary, and validated through actual code execution and testing.