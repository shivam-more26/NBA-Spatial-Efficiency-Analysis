# NBA Spatial Efficiency & Expected Value Analytics

This project answers two questions: which Golden State Warriors players created the most value above their expected shot output, and how much of that performance was driven by shot location and zone efficiency during the 2021-22 season? It combines NBA shot logs, spatial zone baselines, and expected-value calculations into a reproducible data-science workflow.

## Key analytics & insights

- Among players with at least 200 attempts, Gary Payton II led the roster at +0.1569 PAE per shot on 344 attempts (+53.98 total PAE), ahead of Klay Thompson (+0.0443 per shot; +25.38 total PAE) and Otto Porter Jr. (+0.0365 per shot; +15.19 total PAE). Stephen Curry had the most attempts (1,224) but produced only +0.0126 PAE per shot (+15.44 total PAE), while Andrew Wiggins posted +29.34 total PAE on 1,019 attempts.
- Volume and efficiency were not the same story: Curry took 1,224 shots and made 535, for a 43.71% FG% and +15.44 total PAE, while Payton II shot 61.63% (212 makes on 344 attempts) and delivered +53.98 total PAE and +0.1569 per shot.
- The most valuable zone by PAE per shot was Mid-Range – Right Side (R): 223 attempts, +0.8296 total PAE, +0.0037 PAE per shot. The next-best zone was Mid-Range – Left Side (L): 203 attempts, +0.0444 total PAE, +0.0002 PAE per shot.
- The weakest overall zone was Above the Break 3 – Left Side Center (LC): 965 attempts, -0.0004 total PAE, with a per-shot value effectively at zero. This indicates the team’s long-range center looks were close to neutral after adjusting for their own zone baseline, while the right-side mid-range look was the clearest above-average spot.
- 2-point attempts accounted for 3,851 shots (54.38% of all attempts) but were -1.7469 total PAE, while 3-point attempts were 3,230 shots (45.62%) and produced +2.6217 total PAE. In other words, the team’s 3-point volume was more valuable than its 2-point volume once adjusted for zone-average expectations.
- The team total was +0.8748 PAE across all shots, which suggests that the roster as a whole was slightly above the team’s zone-average expectation over the full 2021-22 sample.

### How to read PAE

PAE compares each shot to the zone average for that same shot location within this team’s own shot profile. It is a location-adjusted finishing metric: it reflects the shot’s expected value given the team’s historical make rate in that area, not defender distance, shot clock pressure, or shot creation quality.

### Methodology notes

- Zone Baseline FG% is computed from this team’s own shot logs in `src/processing.py`, where the code groups shots by `SHOT_ZONE_BASIC` and `SHOT_ZONE_AREA` and then takes the mean of `SHOT_MADE_FLAG`: `df.groupby(['SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA']) ... ('SHOT_MADE_FLAG', 'mean')`. It is therefore the team’s own zone baseline, not a league-wide benchmark.
- PAE is then calculated as `POINTS_SCORED - EXPECTED_VALUE`, where `EXPECTED_VALUE = SHOT_VALUE * ZONE_BASELINE_FG_PCT`. That means the metric captures how much a shot outperformed or underperformed the team’s own baseline for that zone, rather than a generic league-wide expectation.

## Visual showcase

### Stephen Curry
![Stephen Curry shot chart](images/stephen_curry_shot_chart.png)

### Player comparisons
| Player | Shot chart |
| --- | --- |
| Klay Thompson | ![Klay Thompson shot chart](images/klay_thompson_shot_chart.png) |
| Gary Payton II | ![Gary Payton II shot chart](images/gary_payton_ii_shot_chart.png) |
| Andrew Wiggins | ![Andrew Wiggins shot chart](images/andrew_wiggins_shot_chart.png) |

## Results table

| Player | Total shots | FG% | Total PAE | PAE per shot |
| --- | ---: | ---: | ---: | ---: |
| Gary Payton II | 344 | 0.6163 | 53.99 | 0.1569 |
| Andrew Wiggins | 1019 | 0.4661 | 29.32 | 0.0288 |
| Klay Thompson | 573 | 0.4293 | 25.36 | 0.0443 |
| Stephen Curry | 1224 | 0.4371 | 15.41 | 0.0126 |
| Otto Porter Jr. | 416 | 0.4639 | 15.19 | 0.0365 |

## Charts

- [images/stephen_curry_shot_chart.png](images/stephen_curry_shot_chart.png)
- [images/klay_thompson_shot_chart.png](images/klay_thompson_shot_chart.png)
- [images/gary_payton_ii_shot_chart.png](images/gary_payton_ii_shot_chart.png)
- [images/andrew_wiggins_shot_chart.png](images/andrew_wiggins_shot_chart.png)
- [images/nba_half_court.jpg](images/nba_half_court.jpg)

## Project structure

```text
NBA-Spatial-Efficiency-Analysis/
├── data/
│   ├── raw/
│   │   └── gsw_2022_roster_shots_root.csv
│   └── processed/
│       └── gsw_2022_processed_ev.csv
├── images/
│   ├── andrew_wiggins_shot_chart.png
│   ├── gary_payton_ii_shot_chart.png
│   ├── klay_thompson_shot_chart.png
│   ├── nba_half_court.jpg
│   └── stephen_curry_shot_chart.png
├── notebooks/
│   ├── 01_gsw_data_ingestion.ipynb
│   └── 02_gsw_feature_engineering.ipynb
├── reports/
│   ├── court_coordinate_mapping_guide.md
│   └── dax_measures.dax
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── court_visualizer.py
│   ├── ingestion.py
│   ├── pipeline.py
│   └── processing.py
├── .gitignore
├── LICENSE
├── README.md
├── RESUME_SHOWCASE.md
├── plot_player_shots.py
├── requirements.txt
└── .
```

## How to run

```bash
git clone <repo-url>
cd <repo>
pip install -r requirements.txt
jupyter notebook notebooks/01_gsw_data_ingestion.ipynb
```

To reproduce the feature engineering workflow:

```bash
jupyter notebook notebooks/02_gsw_feature_engineering.ipynb
```

## Data

- Source: NBA Stats API via `nba_api` and the team shot chart endpoint for the Golden State Warriors.
- Seasons covered: 2021-22 regular season.
- Collection method: roster and player shot requests were retrieved programmatically, cleaned into a single raw dataset, and saved in `data/raw/gsw_2022_roster_shots_root.csv` before feature engineering.
- Processed output: `data/processed/gsw_2022_processed_ev.csv`.

## Analytical framework

### Coordinate normalization

Raw NBA API coordinates are normalized from the standard NBA shot chart coordinate system into a 50ft x 47ft half-court layout used for spatial analysis and plotting.

### Expected Value

- Shot value = 3 for three-point attempts, 2 for two-point attempts.
- Zone baseline FG% = the historical make rate for each spatial court zone.
- Expected value = shot value × zone baseline FG%.
- PAE = actual points scored − expected value.

## Limitations

- Sample size is limited to the 2021-22 Golden State Warriors roster and season window.
- Data quality depends on API availability and the shot-chart record coverage returned by NBA endpoints.
- This project is descriptive, not causal: it identifies spatial efficiency patterns rather than proving causal drivers.
- No model claims are made beyond the observed relationship between shot location, expected value, and actual scoring output.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Numbers changed for this README

This README uses only values already present in the project outputs and notebooks: 1,224 total attempts for Stephen Curry, 1,019 for Andrew Wiggins, 344 for Gary Payton II, +15.41 total PAE for Curry, +29.32 total PAE for Wiggins, and +53.99 total PAE with +0.1569 PAE per shot for Payton II.
