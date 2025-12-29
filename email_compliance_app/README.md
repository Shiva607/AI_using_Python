# **AI-Driven Email Compliance Monitoring System**

## **1. Use Case Overview & Business Problem**

### **Overview**

The AI-driven Email Compliance Monitoring System is an advanced tool designed for banks and financial institutions to automatically scan and analyze emails exchanged between employees and external parties. This system leverages artificial intelligence to identify potential compliance violations, categorize risks, and prioritize alerts for efficient review.

### **Business Problem**

Financial institutions are required by regulatory bodies (such as SEC, SEBI, or FINRA) to monitor communications for non-compliant activities, including insider trading, bribery, or unethical behavior.

**Key challenges include:**

- **High False Positives:** Traditional rule-based systems flag too many innocuous emails, overwhelming compliance teams.
- **Manual Review Effort:** Reviewing thousands of emails daily is time-consuming and prone to human error.
- **Lack of Alert Prioritization:** Without risk-based scoring, critical violations may be buried among low-priority alerts, delaying response and increasing regulatory risks.

The system addresses these by automating detection and focusing on employee–external emails, where most compliance risks occur.

---

## **2. Objectives of the AI Solution**

The primary goals of the AI solution are to enhance compliance monitoring efficiency and accuracy:

- **Reduce False Positives:** Use contextual AI analysis to distinguish benign communications from true risks, minimizing unnecessary reviews.
- **Improve Productivity:** Automate initial screening, allowing compliance officers to focus on high-risk cases.
- **Enable Risk-Based Prioritization:** Assign severity scores and priorities to alerts, ensuring critical issues are addressed first.

Overall, the solution aims to strengthen regulatory compliance while optimizing operational resources.

---

## **3. Scope of Compliance Categories**

The system focuses on key compliance risks commonly encountered in financial communications.

**Supported categories include:**

- **Secrecy:** Indications of withholding or concealing sensitive information (e.g., "don't tell compliance" or cover-ups).
- **Market Manipulation / Misconduct:** Signals of insider trading, coordinated behavior, or price distortion (e.g., "position trades before announcement").
- **Market Bribery:** References to kickbacks, inducements, or favors (e.g., "gift in return for information").
- **Change in Communication Channels:** Attempts to switch to off-record discussions (e.g., "let's discuss offline" or "call me instead").
- **Complaints:** Expressions of dissatisfaction or escalation threats (e.g., "poor execution" or "escalate to regulator").
- **Employee Ethics:** Violations of internal policies or ethical standards (e.g., "bypass approval" or "against rules").

The system can detect one or more categories per email and combines them for comprehensive risk assessment.

---

## **4. What the AI System Does**

The AI system performs end-to-end processing of emails to detect and prioritize compliance risks:

- **Automatically Flag Potentially Non-Compliant Emails:** Scans incoming emails for risk indicators using AI context understanding.
- **Assign One or More Non-Compliance Categories:** Categorizes violations based on content using predefined risk tiers.
- **Identify Reasons and Exact Source Lines Triggering Violations:** Highlights specific phrases or sentences that triggered the flag.
- **Prioritize Alerts Using a Predefined Criticality Matrix:** Applies a weighted scoring formula to assign priorities (Critical, High, Medium, Low).

This workflow ensures actionable insights without manual intervention.

---

## **5. High-Level Architecture (LLM-Based)**

The system is built on a large language model (LLM) foundation, emphasizing efficiency and scalability without traditional machine learning training.

### **Key Components**

- **Email Ingestion:** Loads emails from Excel files or integrates with email APIs for batch processing.
- **Preprocessing:** Cleans text by removing noise (URLs, emails, phone numbers, greetings, signatures).
- **LLM Analysis:** Uses GPT-based LLM to detect categories, estimate confidence, and assess language risk.
- **Categorization:** Matches content to predefined compliance categories.
- **Prioritization:** Applies weighted scoring formula for risk level assignment.
- **Memory Management:** Uses Streamlit session state to cache processed results and prevent re-analysis.
- **Reviewer Dashboard:** Streamlit-based UI for visualization, filtering, and exporting reports.

### **Architecture Flow**

```
Email Source (Excel/API)
        ↓
Ingestion Layer
        ↓
Preprocessing (Noise Removal)
        ↓
LLM Analysis (Category Detection, Confidence, Language Risk)
        ↓
Categorization & Scoring (Weighted Formula)
        ↓
Prioritization (Critical/High/Medium/Low)
        ↓
Memory Caching (Session State)
        ↓
Reviewer Dashboard (Streamlit UI)
        ↓
Export (Excel)
```

**Explanation:** Emails are ingested and cleaned. The LLM analyzes risks. Categories and scores are calculated, prioritized, cached in memory, and visualized in the dashboard. This LLM-centric design ensures adaptability, performance, and cost efficiency.

---

## **6. Business Benefits**

- **Faster Investigations:** Review time reduced from days to hours.
- **Reduced Manual Effort:** 70–80% fewer false positives.
- **Better Regulatory Compliance:** Early risk detection minimizes fines and reputational damage.
- **Operational Efficiency:** Scalable processing with cost control via token usage tracking and memory caching.

---

## **7. Used Libraries and Their Purpose**

| Library          | Purpose                                                                 |
| ---------------- | ----------------------------------------------------------------------- |
| streamlit        | Builds the interactive web-based dashboard UI and manages session state |
| pandas           | Handles data processing, Excel reading, and DataFrame operations        |
| plotly.express   | Creates interactive charts for visualization                            |
| io.BytesIO       | Manages in-memory file buffers for Excel downloads                      |
| streamlit_extras | Adds UI utility functions                                               |
| openai           | Interfaces with the LLM for analysis and scoring                        |
| dotenv           | Loads environment variables from `.env`                                 |
| pydantic         | Defines and validates data models                                       |
| re               | Performs regex-based text cleaning                                      |
| typing           | Provides type hints                                                     |

---

## **8. Architecture Diagram and Explanation**

```
+--------------------+
| Email Source       |
| (Excel/API)        |
+--------------------+
          |
          v
+--------------------+
| Ingestion Layer    |
+--------------------+
          |
          v
+--------------------+
| Preprocessing      |
| (Remove Junk)      |
+--------------------+
          |
          v
+--------------------+
| LLM Analysis       |
| (GPT for Categories|
| Confidence, Risk)  |
+--------------------+
          |
          v
+--------------------+
| Categorization     |
| & Scoring (Formula)|
+--------------------+
          |
          v
+--------------------+
| Prioritization     |
| (Critical-High-Low)|
+--------------------+
          |
          v
+--------------------+
| Memory Caching     |
| (Session State)    |
+--------------------+
          |
          v
+--------------------+
| Reviewer Dashboard |
| (Streamlit UI)     |
+--------------------+
          |
          v
+--------------------+
| Export (Excel)     |
+--------------------+
```

**Explanation:** Modular, LLM-centric design focused on intelligent analysis without ML training.

---

## **9. Folder Structure**

```
email_compliance_app/
├── app.py
├── llm/
│   └── gpt_classifier.py
├── models/
│   ├── email_schema.py
│   └── llm_schema.py
├── preprocessing/
│   ├── cleaner.py
│   └── rules.py
```

---

## **10. Weighted Scoring Model**

**Formula**

```
Score = 100 × (0.60 × normalized_category
             + 0.30 × model_confidence
             + 0.10 × language_risk)
```

### **Category Severity Mapping**

| Category                         | Severity (0–5) |
| -------------------------------- | -------------- |
| Secrecy                          | 5              |
| Market Manipulation / Misconduct | 4              |
| Market Bribery                   | 4              |
| Change in Communication          | 3              |
| Complaints                       | 2              |
| Employee Ethics                  | 1              |

### **Priority Mapping**

| Priority | Score Range |
| -------- | ----------- |
| Critical | ≥ 80        |
| High     | 65 – 79     |
| Medium   | 45 – 64     |
| Low      | < 45        |

**Example:**
Market Bribery (4) + Change in Communication (3) → High Priority (Score = 69)

---

## **11. Flow Diagram**

```
Start
  ↓
Upload Excel
  ↓
Ingestion
  ↓
Preprocessing
  ↓
LLM Analysis
  ↓
Weighted Score Calculation
  ↓
Priority Assignment
  ↓
Cache Results
  ↓
Dashboard Display
  ↓
Export Excel
  ↓
End
```

**Explanation:** Sequential, optimized flow with memory caching to avoid redundant LLM calls.

---
