# 🌾 Holdr - Grain Post-Harvest Decision Engine

## Description of the Project
**Holdr** (formerly AgroIntel) is an AI-powered post-harvest management and grain telemetry platform. It is engineered to provide actionable storage, inventory monitoring, and sales-timing recommendations for grain farmers and commodity aggregators. This specific module (`rule_engine.py`) serves as the core decision-making backend, evaluating real-time telemetry, storage conditions, and market parameters against agronomic thresholds to automate intelligent post-harvest decision support.

---

## Problem Statement
Grain farmers and commodity aggregators frequently face steep financial losses post-harvest due to improper storage conditions, moisture-induced spoilage, and mistimed sales decisions driven by lack of market intelligence. Manual monitoring of grain silos and fluctuating market dynamics is error-prone and often leads to delayed interventions. The core problem addressed by this component is how to automate the evaluation of incoming telemetry (such as moisture levels, temperature, and storage duration) and business rules to instantly flag spoilage risks and determine optimal holding or selling windows.

---

## The Tools Used
The module is built using clean, high-performance Python programming standards:
* **Programming Language:** Python 3.x
* **Core Logic & Architecture:** Object-Oriented Programming (OOP), modular conditional evaluation frameworks
* **Data Processing:** Standard Python data structures and datetime manipulation libraries
* **Version Control & Environment:** Git, GitHub

---

## The Methodology
The rule engine executes a deterministic, rule-based evaluation pipeline designed for speed and reliability:
1. **Telemetry Ingestion:** Receiving real-time or batch sensor data points covering critical storage parameters (e.g., grain moisture content, ambient temperature, relative humidity, and storage duration).
2. **Threshold Rule Definition:** Establishing domain-specific agronomic and commercial thresholds (e.g., critical moisture ceilings for maize or beans to prevent mold growth and mycotoxin development).
3. **Condition Evaluation & State Assessment:** Processing input parameters through a cascading set of evaluation rules to classify current storage health (e.g., *Safe*, *Warning*, or *Critical Spoilage Risk*).
4. **Actionable Recommendation Generation:** Translating evaluation outputs into structured recommendations (such as immediate aeration, drying, or strategic market release based on holding duration and price trends).

---

## The Results
* Successfully implemented a robust, programmatic rule engine that automates complex post-harvest safety checks and inventory evaluations.
* Eliminated latency in risk detection by instantly flagging unsafe storage parameters before physical grain degradation occurs.
* Provided a modular, extensible backend architecture that can be seamlessly integrated into broader FastAPI backends, web dashboards, or offline RAG/AI assistants.

---

## 🚀 Getting Started

To run or integrate this module locally:
```bash
# Clone the repository
git clone [https://github.com/Placidus-Ali/Holdr.git](https://github.com/Placidus-Ali/Holdr.git)

# Navigate to the project directory
cd Holdr

# Run or import the rule engine script
python rule_engine.py
```

## Here is the App
https://holdr-aipostharvestmanagementplatform.streamlit.app/
