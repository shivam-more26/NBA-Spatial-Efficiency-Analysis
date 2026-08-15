# NBA Spatial Efficiency & Expected Value (EV) Analytics

An automated, production-grade Python ETL pipeline and Power BI analytics framework that ingests live NBA spatial shot data, performs mathematical coordinate mapping and Expected Value modeling, and exports star-schema analytics datasets for Power BI dashboards.

---

## 🌟 Resume & Portfolio Showcase

Looking to feature this project on your **Resume**, **LinkedIn**, or **Portfolio**? 
Check out **[`RESUME_SHOWCASE.md`](file:///d:/projects/NBA%20Spatial%20Efficiency%20Analysis/RESUME_SHOWCASE.md)** for:
- 📄 **STAR Method Resume Bullet Points** (Data Analyst & Analytics Engineer tracks)
- 💼 **LinkedIn / Portfolio 1-Paragraph Pitch & One-Liners**
- 🏗️ **Mermaid System Architecture & Data Flow Diagrams**
- 🎙️ **Interview Talking Points & System Design Q&A**

---

## 📌 Project Architecture

```
NBA Spatial Efficiency Analysis/
├── data/
│   ├── raw/
│   │   └── GSW_2022_Roster_Shots.csv       # Raw spatial shot extraction
│   └── processed/
│       ├── Fact_Shots.csv                  # Granular shot fact table with EV metrics
│       ├── Dim_Player.csv                  # Player dimension table with aggregated stats
│       └── Dim_Shot_Zone.csv               # Spatial shot zone baselines
├── src/
│   ├── __init__.py
│   ├── config.py                           # Central configuration & path management
│   ├── ingestion.py                        # NBA Stats REST API fetcher with retry logic
│   ├── processing.py                       # Spatial math, coordinate scaling & EV model
│   └── pipeline.py                         # CLI ETL orchestrator script
├── powerbi/
│   ├── DAX_Measures.dax                    # Ready-to-use Power BI DAX metrics
│   └── Court_Coordinate_Mapping_Guide.md   # Step-by-step court scatter chart setup
├── logs/
│   └── etl_pipeline.log                    # Execution history and diagnostic logs
├── RESUME_SHOWCASE.md                      # Copy-paste resume bullets & interview guide
├── requirements.txt                        # Python dependencies
└── README.md
```

---

## 🧮 Mathematical & Analytical Framework

### 1. Spatial Coordinate Normalization
NBA court coordinates ($X \in [-250, 250]$, $Y \in [-52, 418]$) in tenths of a foot are transformed to standard court feet dimensions ($50\text{ft} \times 47\text{ft}$) for Power BI visual scatter rendering:
$$\text{POWERBI\_X} = \frac{\text{LOC\_X} + 250}{10}$$
$$\text{POWERBI\_Y} = \frac{\text{LOC\_Y} + 52}{10}$$

### 2. Shot Valuation & Expected Value (EV)
- **Point Valuation**:
  $$\text{SHOT\_VALUE} = \begin{cases} 3, & \text{if 3PT Field Goal} \\ 2, & \text{if 2PT Field Goal} \end{cases}$$
- **Zone Baseline FG%**: Average FG% for each spatial zone ($Z_{\text{basic}}, Z_{\text{area}}$).
- **Expected Value (EV)**:
  $$\text{EV} = \text{SHOT\_VALUE} \times \text{ZONE\_BASELINE\_FG\_PCT}$$
- **Points Above Expected (PAE)**:
  $$\text{PAE} = \text{POINTS\_SCORED} - \text{EXPECTED\_VALUE}$$

---

## 🚀 Quick Start Guide

### 1. Installation
Ensure Python 3.9+ is installed, then install requirements:
```bash
pip install -r requirements.txt
```

### 2. Run Automated ETL Pipeline
Execute the pipeline via Python CLI:
```bash
# Uses cached raw data if present
python -m src.pipeline

# Force refresh from NBA Stats REST API
python -m src.pipeline --force-refresh
```

---

## 📊 Power BI Setup

1. Import `Fact_Shots.csv`, `Dim_Player.csv`, and `Dim_Shot_Zone.csv` into Power BI Desktop.
2. Establish 1-to-Many relationships:
   - `Dim_Player[PLAYER_NAME]` $\rightarrow$ `Fact_Shots[PLAYER_NAME]`
   - `Dim_Shot_Zone[SHOT_ZONE_BASIC], [SHOT_ZONE_AREA]` $\rightarrow$ `Fact_Shots[SHOT_ZONE_BASIC], [SHOT_ZONE_AREA]`
3. Copy DAX formulas from `powerbi/DAX_Measures.dax`.
4. Follow `powerbi/Court_Coordinate_Mapping_Guide.md` to plot spatial shot chart scatter visuals with court background overlays.
