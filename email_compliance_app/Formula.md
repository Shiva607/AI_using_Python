# Weighted Scoring Model (Correct & Clean Format)

This approach is based on the **weighted sum model / weighted linear combination**, commonly used in multi-criteria decision analysis.

## ✅ Weighted Scoring Formula

```
Score = 100 × (w_cat × category_score + w_conf × model_confidence + w_lang × language_risk)
```

### Conditions

```
w_cat + w_conf + w_lang = 1
```

- `category_score`, `model_confidence`, and `language_risk` must be **on the same scale (0–1)**
- The final score is scaled to **0–100**

---

## ✅ Category Severity Mapping

| Category                         | Severity (0–5) |
| -------------------------------- | -------------- |
| Secrecy                          | 5              |
| Market Manipulation / Misconduct | 4              |
| Market Bribery                   | 4              |
| Change in communication          | 3              |
| Complaints                       | 2              |
| Employee ethics                  | 1              |

---

## ✅ Weights (Must Sum to 1)

```
w_cat  = 0.60   // category severity
w_conf = 0.30   // model confidence
w_lang = 0.10   // language risk
```

```
0.60 + 0.30 + 0.10 = 1.00
```

---

## ✅ Example Scenario

### Input Data

```
Categories detected:
- Market Bribery (4)
- Change in communication (3)

Model confidence = 0.80
Language risk    = 0.30
```

---

## ✅ Combine Multiple Categories

Average severity:

```
category_score = (4 + 3) / 2 = 3.5
```

---

## ❗ Why Normalization Is Required

- `category_score` is on a **0–5 scale**
- `model_confidence` and `language_risk` are on **0–1 scale**

So we normalize category severity:

```
normalized_cat = category_score / 5
normalized_cat = 3.5 / 5 = 0.70
```

---

## ❌ Incorrect (Before Normalization)

```
Score = 100 × (0.60×3.5 + 0.30×0.80 + 0.10×0.30)
Score = 100 × (2.1 + 0.24 + 0.03)
Score = 237   ❌
```

Reason: values are on **different scales**, breaking weight meaning.

---

## ✅ Correct Calculation (After Normalization)

```
Score = 100 × (0.60×0.70 + 0.30×0.80 + 0.10×0.30)
```

Step-by-step:

```
0.60 × 0.70 = 0.42
0.30 × 0.80 = 0.24
0.10 × 0.30 = 0.03
```

```
Total = 0.69
Score = 100 × 0.69 = 69
```

---

## ✅ Priority Mapping

| Priority Level | Score Range |
| -------------- | ----------- |
| Critical       | ≥ 80        |
| High           | 65 – 79     |
| Medium         | 45 – 64     |
| Low            | < 45        |

```
Final Score = 69 → High Priority
```

---

## ✅ Summary (One Block)

```
Input:
 Categories = Market Bribery + Change in communication
 Model confidence = 0.80
 Language risk = 0.30

Normalized category score:
 (4 + 3) / 2 / 5 = 0.70

Final formula:
 Score = 100 × (0.60×0.70 + 0.30×0.80 + 0.10×0.30)
 Score = 69

Priority = High
```

---

### Q1 Why do we normalize `category_score` before applying the weighted formula?

**Answer:**
Because weighted scoring models require all inputs to be on the **same scale**. Without normalization, category severity (0–5) would dominate confidence and language risk (0–1), breaking the meaning of the weights.

---

### Q2 Why are `Market Manipulation / Misconduct and Market Bribery` both assigned a severity score of 4?

**Answer:** Both are rated 4 because they are equally “High severity” but not the absolute highest risk.

## Why both are `4` (Clear reasoning)

Severity scores are **ordinal**, not precise measurements.
They represent **risk tiers**, not mathematical truth.

A common 1–5 interpretation looks like this:

| Severity | Meaning                     |
| -------- | --------------------------- |
| 5        | Critical / existential risk |
| 4        | High risk                   |
| 3        | Medium risk                 |
| 2        | Low risk                    |
| 1        | Very low risk               |

Now map your categories:

### 1️⃣ Market Manipulation / Misconduct → **4**

- Insider trading signals
- Coordinated trading behavior
- Price distortion
- Regulatory violations (SEBI, SEC, etc.)

➡ **High regulatory & financial risk**
➡ But usually **requires corroboration** before enforcement
➡ Hence **4, not 5**

---

### 2️⃣ Market Bribery → **4**

- Kickbacks, inducements, favors
- Corruption-related risk
- Serious compliance breach

➡ **High legal & reputational risk**
➡ Often **transactional and covert**
➡ Not always immediately systemic
➡ Hence **4, not 5**

---

## Why neither is `5`

### `5` is reserved for **Secrecy**

Examples:

- Leakage of MNPI
- Attempted cover-up
- Obfuscation + evasion
- Explicit “don’t tell compliance” language

These indicate:

- **Intent**
- **Systemic breach**
- **Regulatory catastrophe**

So:

```
Secrecy = 5 (Critical)
Manipulation = 4 (High)
Bribery = 4 (High)
```

---

## Key design principle (important)

> **Severity ≠ frequency** > **Severity = potential impact if true**

Both manipulation and bribery:

- Can cause massive damage
- Are often **context-dependent**
- Usually escalated further when combined with **Secrecy**

Example:

```
Market Bribery + Secrecy → effective severity ≈ 5
```

---

## If you want finer differentiation (optional)

You _can_ separate them later:

```
Market Manipulation = 4.5
Market Bribery = 4.0
```

or apply **rule-based escalation**:

```
IF category = Market Bribery AND secrecy_flag = true
THEN category_score = 5
```

---

## One-line exam answer

> Market Manipulation/Misconduct and Market Bribery are both assigned severity 4 because they represent high-impact compliance risks with significant legal and financial consequences, but they are ranked below Secrecy, which indicates critical intent and systemic breach.

---
