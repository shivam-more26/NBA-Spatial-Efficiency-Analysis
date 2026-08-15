# Power BI Half-Court Spatial Visualization Setup Guide

This guide details how to set up interactive NBA half-court shot charts and spatial Expected Value (EV) heatmaps inside Power BI Desktop using our custom background court image.

---

## 🏀 Visual Assets Provided

Inside your project's `powerbi/` directory:
- 🖼️ **`powerbi/nba_half_court.jpg`**: Official high-resolution 2D NBA half-court background diagram.
- 📊 **`powerbi/Stephen_Curry_Shot_Chart.png`**: Sample generated shot chart visual.
- 📊 **`powerbi/Klay_Thompson_Shot_Chart.png`**: Sample generated shot chart visual.
- 📊 **`powerbi/Gary_Payton_II_Shot_Chart.png`**: Sample generated shot chart visual.

---

## 🛠️ Step-by-Step Power BI Setup

### Step 1: Import & Connect Data
1. Load `data/processed/Fact_Shots.csv` into Power BI Desktop.
2. Load `data/processed/Dim_Player.csv` and `data/processed/Dim_Shot_Zone.csv`.
3. Verify 1-to-Many relationships:
   - `Dim_Player[PLAYER_NAME]` $\rightarrow$ `Fact_Shots[PLAYER_NAME]`
   - `Dim_Shot_Zone[SHOT_ZONE_BASIC], [SHOT_ZONE_AREA]` $\rightarrow$ `Fact_Shots[SHOT_ZONE_BASIC], [SHOT_ZONE_AREA]`

---

### Step 2: Configure the Scatter Chart Visual
1. On your Power BI canvas, add a **Scatter Chart** visual.
2. Drag fields from `Fact_Shots`:
   - **X Axis**: `Fact_Shots[POWERBI_X]` $\rightarrow$ Right-click and choose **Don't summarize**.
   - **Y Axis**: `Fact_Shots[POWERBI_Y]` $\rightarrow$ Right-click and choose **Don't summarize**.
   - **Values / Legend**: `Fact_Shots[SHOT_MADE_FLAG]` (0 = Miss, 1 = Make).
   - **Tooltips**: `PLAYER_NAME`, `ACTION_TYPE`, `SHOT_DISTANCE`, `EXPECTED_VALUE`, `POINTS_SCORED`, `POINTS_ABOVE_EXPECTED`.

---

### Step 3: Set Exact Court Axes Range
To align shots precisely with the court layout:
1. Open the **Format Visual** pane (paint roller icon).
2. Expand **X Axis**:
   - Set **Minimum**: `0`
   - Set **Maximum**: `50`
   - Turn **Title**: OFF
3. Expand **Y Axis**:
   - Set **Minimum**: `0`
   - Set **Maximum**: `47`
   - Turn **Title**: OFF

---

### Step 4: Apply the Half-Court Background Image
1. In the **Format Visual** pane, expand **Plot Area Background**.
2. Click **Add Image** and select:
   `d:\projects\NBA Spatial Efficiency Analysis\powerbi\nba_half_court.jpg`
3. Change **Image Fit** to **Fit**.
4. Adjust **Transparency** slider to **20% – 30%** (so dark/white court lines are clearly visible behind shot dots).

---

### Step 5: Customize Shot Markers & Colors
1. Expand **Markers**:
   - **Shape**: Circle or Cross
   - **Size**: `-2` or `-3` (keeps scatter plot clean with 1000+ points)
2. Expand **Data Colors**:
   - **Shot Made (1)**: Vibrant Green (`#10B981`) or Gold (`#FFB703`)
   - **Shot Missed (0)**: Coral Red (`#EF4444`)

---

## 🐍 Python Method (Alternative / Standalone Visualization)

You can also generate half-court shot charts directly from Python using our built-in court visualizer:

```bash
# Generate sample shot charts for top players
python plot_player_shots.py
```

Or write custom plotting scripts:
```python
from src.court_visualizer import plot_player_shot_chart
import pandas as pd

df = pd.read_csv("data/processed/Fact_Shots.csv")
plot_player_shot_chart(df, player_name="Stephen Curry", output_path="powerbi/Stephen_Curry_Shot.png")
```
