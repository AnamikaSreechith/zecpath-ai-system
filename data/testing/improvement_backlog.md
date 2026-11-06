# Day 17 – ATS Improvement Backlog

## Real Evaluation Findings (50-Pair Matrix)
- **Evaluations:** 50
- **Accuracy:** 76.0%
- **Precision:** 30.77%
- **Recall:** 57.14%
- **F1-Score:** 40.0%
- **Identified Mismatches:** 12 cases (9 False Positives, 3 False Negatives)

---

## 1. High-Priority Engineering Backlog Items

### Item 1: Mandatory Core Skill Hard-Gating (Fixes 6 False Positives)
- **Problem:** Front-end developers, Cyber Security freshers, and Project Managers were passed for Python, Java, and Data Analyst roles because shared secondary keywords (SQL, Git, REST APIs) inflated their aggregate score above 50%.
- **Solution:** Introduce a hard-gating rule in `ats_scoring_engine.py`: If a role specifies a mandatory core language (e.g., Java for Java Dev, Python for Python Dev), candidates missing that core language cannot exceed a score of 45% and are automatically disqualified from the `Review` status.

### Item 2: Dynamic Margin / Gray-Zone Handling (Fixes 3 False Negatives)
- **Problem:** `CAND009` scored 49.76% for Python Developer and was rejected because of a rigid 50.00% threshold.
- **Solution:** Implement a configurable "Borderline Review Band" (e.g., 48.0% - 52.0%) where borderline candidates trigger a secondary semantic keyword check rather than an immediate hard rejection.

### Item 3: Role-Specific Keyword Weight Rebalancing (Fixes 3 False Positives)
- **Problem:** Project Managers and Cyber Security candidates received disproportionate points in Data Analyst and ML Engineer roles.
- **Solution:** Increase the weight of specialized algorithms and frameworks (e.g., PyTorch, TensorFlow, Pandas, Scikit-Learn) relative to generic IT tooling (Jira, Git, Agile).