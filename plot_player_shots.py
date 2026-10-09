import pandas as pd
from pathlib import Path
from src.court_visualizer import plot_player_shot_chart
from src.config import FACT_SHOTS_CSV, BASE_DIR

def generate_sample_shot_charts():
    output_dir = BASE_DIR / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading Fact_Shots dataset from: {FACT_SHOTS_CSV}")
    df_shots = pd.read_csv(FACT_SHOTS_CSV)

    top_players = ["Stephen Curry", "Klay Thompson", "Andrew Wiggins", "Gary Payton II"]

    for player in top_players:
        output_file = output_dir / f"{player.replace(' ', '_')}_Shot_Chart.png"
        print(f"Generating spatial shot chart for {player}...")
        plot_player_shot_chart(df_shots, player_name=player, output_path=str(output_file))

if __name__ == "__main__":
    generate_sample_shot_charts()
