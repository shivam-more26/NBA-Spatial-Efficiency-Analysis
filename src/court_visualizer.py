import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import pandas as pd
import numpy as np

def draw_nba_half_court(ax=None, color='#1E293B', lw=2, background_color='#0F172A'):
    """
    Draw an official NBA half court on a Matplotlib Axes object.
    Coordinates are in feet relative to hoop center (0,0).
    Court bounds: X in [-25, 25], Y in [-5.25, 41.75].
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 9.4), facecolor=background_color)

    ax.set_facecolor(background_color)

    # 1. Hoop & Backboard
    hoop = Circle((0, 0), radius=0.75, linewidth=lw, color='#F97316', fill=False)
    backboard = Rectangle((-3, -1.25), 6, 0, linewidth=lw, color='white')

    # 2. Key / Paint Area (16ft wide, 19ft deep from baseline = 13.75ft from hoop)
    outer_box = Rectangle((-8, -5.25), 16, 19, linewidth=lw, color='white', fill=False)
    inner_box = Rectangle((-6, -5.25), 12, 19, linewidth=lw, color='white', fill=False)

    # 3. Free Throw Circles
    top_free_throw = Arc((0, 13.75), 12, 12, theta1=0, theta2=180, linewidth=lw, color='white', fill=False)
    bottom_free_throw = Arc((0, 13.75), 12, 12, theta1=180, theta2=360, linewidth=lw, color='white', linestyle='dashed')

    # 4. Restricted Area Arc (4ft radius from hoop)
    restricted = Arc((0, 0), 8, 8, theta1=0, theta2=180, linewidth=lw, color='white', fill=False)

    # 5. 3-Point Line
    # Corner 3 lines (straight lines 14ft from baseline)
    corner_three_left = Rectangle((-22, -5.25), 0, 14, linewidth=lw, color='white')
    corner_three_right = Rectangle((22, -5.25), 0, 14, linewidth=lw, color='white')
    # 3PT Arc (23.75 ft radius, arc theta from ~22 deg to ~158 deg)
    three_arc = Arc((0, 0), 47.5, 47.5, theta1=22, theta2=158, linewidth=lw, color='white', fill=False)

    # 6. Center Court Arc (6ft radius)
    center_outer_arc = Arc((0, 41.75), 12, 12, theta1=180, theta2=360, linewidth=lw, color='white', fill=False)

    # Add court elements to axes
    court_elements = [
        hoop, backboard, outer_box, inner_box,
        top_free_throw, bottom_free_throw, restricted,
        corner_three_left, corner_three_right, three_arc, center_outer_arc
    ]

    for element in court_elements:
        ax.add_patch(element)

    # Outer Half-Court Boundary
    half_court_box = Rectangle((-25, -5.25), 50, 47, linewidth=lw+1, color='white', fill=False)
    ax.add_patch(half_court_box)

    # Set Axes Limits & Clean Up
    ax.set_xlim(-26, 26)
    ax.set_ylim(-6, 43)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')

    return ax

def plot_player_shot_chart(df_shots: pd.DataFrame, player_name: str, output_path: str = None):
    """
    Plot player spatial shot chart overlay on half-court.
    """
    player_data = df_shots[df_shots['PLAYER_NAME'] == player_name].copy()
    if player_data.empty:
        raise ValueError(f"No shot data found for player '{player_name}'.")

    # Convert LOC_X and LOC_Y from tenths of a foot to feet
    x_feet = player_data['LOC_X'] / 10.0
    y_feet = player_data['LOC_Y'] / 10.0

    fig, ax = plt.subplots(figsize=(10, 9.5), facecolor='#0F172A')
    draw_nba_half_court(ax, color='white', lw=1.8, background_color='#0F172A')

    # Separate makes and misses
    makes = player_data[player_data['SHOT_MADE_FLAG'] == 1]
    misses = player_data[player_data['SHOT_MADE_FLAG'] == 0]

    # Scatter Misses (Red X)
    ax.scatter(
        misses['LOC_X'] / 10.0, misses['LOC_Y'] / 10.0,
        c='#EF4444', marker='x', s=45, alpha=0.7, label=f"Missed ({len(misses)})"
    )

    # Scatter Makes (Green Circles)
    ax.scatter(
        makes['LOC_X'] / 10.0, makes['LOC_Y'] / 10.0,
        c='#10B981', marker='o', s=55, edgecolors='white', linewidth=0.5, alpha=0.9, label=f"Made ({len(makes)})"
    )

    # Stats Summary
    total_shots = len(player_data)
    total_makes = len(makes)
    fg_pct = (total_makes / total_shots) * 100 if total_shots > 0 else 0
    total_pae = player_data['POINTS_ABOVE_EXPECTED'].sum() if 'POINTS_ABOVE_EXPECTED' in player_data.columns else 0.0

    plt.title(
        f"{player_name} - 2021-22 Spatial Shot Chart\n"
        f"Shots: {total_shots} | Makes: {total_makes} | FG%: {fg_pct:.1f}% | Points Above EV: {total_pae:+.1f}",
        fontsize=14, fontweight='bold', color='white', pad=15
    )

    legend = ax.legend(loc='upper right', facecolor='#1E293B', edgecolor='white', labelcolor='white', fontsize=11)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        print(f"Shot chart saved successfully to: {output_path}")
    else:
        plt.show()

    return fig
