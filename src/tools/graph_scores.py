import pandas as pd
import plotly.graph_objects as go
import argparse
import os
import sys

def main():
    # 1. Set up Command Line Argument Parsing
    parser = argparse.ArgumentParser(
        description="Compare two score history CSV files (refine and static) using an interactive Plotly graph."
    )
    parser.add_argument(
        "base_path", 
        help="The base path and filename prefix (e.g., '/path/to/file' will look for '/path/to/file_refine.csv' and '/path/to/file_static.csv')"
    )
    
    args = parser.parse_args()
    
    # 2. Construct the full file paths
    refine_path = f"{args.base_path}_refine.csv"
    static_path = f"{args.base_path}_static.csv"

    # 3. Validate that both files actually exist before proceeding
    missing_files = []
    if not os.path.exists(refine_path):
        missing_files.append(refine_path)
    if not os.path.exists(static_path):
        missing_files.append(static_path)

    if missing_files:
        print("Error: The following files could not be found:")
        for f in missing_files:
            print(f"  - {f}")
        sys.exit(1)

    # 4. Load the data
    print(f"Loading Refine: {refine_path}")
    df_refine = pd.read_csv(refine_path)
    print(f"Loading Static: {static_path}")
    df_static = pd.read_csv(static_path)

    # Define columns
    score_columns = ['syntactic_clarity', 'jargon', 'information_density', 
                     'structural_cohesion', 'faithfulness', 'completeness']
    total_column = 'total_score'

    # 5. Create the Figure
    fig = go.Figure()

    # Color sequence for metrics
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']

    # 6. Add Metric Traces (Comparison Logic)
    for i, col in enumerate(score_columns):
        color = colors[i % len(colors)]
        
        # Add Refine Metric (Solid Line)
        fig.add_trace(
            go.Scatter(
                x=df_refine.index, 
                y=df_refine[col],
                mode='lines+markers',
                name=f'Refine: {col}',
                line=dict(color=color, dash='solid'),
                yaxis='y1'
            )
        )
        
        # Add Static Metric (Dashed Line)
        fig.add_trace(
            go.Scatter(
                x=df_static.index, 
                y=df_static[col],
                mode='lines+markers',
                name=f'Static: {col}',
                line=dict(color=color, dash='dash'),
                yaxis='y1'
            )
        )

    # 7. Add Total Score Traces (The heavy hitters)
    # Refine Total: Thick Black
    fig.add_trace(
        go.Scatter(
            x=df_refine.index, 
            y=df_refine[total_column],
            mode='lines+markers',
            name='TOTAL (Refine)',
            line=dict(color='black', width=5),
            marker=dict(symbol='square'),
            yaxis='y2'
        )
    )

    # Static Total: Thick Grey
    fig.add_trace(
        go.Scatter(
            x=df_static.index, 
            y=df_static[total_column],
            mode='lines+markers',
            name='TOTAL (Static)',
            line=dict(color='grey', width=5, dash='dot'),
            marker=dict(symbol='diamond'),
            yaxis='y2'
        )
    )

    # 8. Configure Layout (Dual Axes and Scales)
    fig.update_layout(
        title='Comparison: Refine vs. Static Score History',
        xaxis=dict(title='Row Index'),
        
        # Left Y-Axis (Metrics 0-5)
        yaxis=dict(
            title=dict(text='Individual Metric Scores', font=dict(color='blue')),
            tickfont=dict(color='blue'),
            range=[0, 5],
            gridcolor='lightgray'
        ),
        
        # Right Y-Axis (Totals 0-25)
        yaxis2=dict(
            title=dict(text='Total Score', font=dict(color='black')),
            tickfont=dict(color='black'),
            range=[0, 25],
            overlaying='y',
            side='right'
        ),
        
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        
        template='plotly_white',
        hovermode='x unified'
    )

    # 9. Show the plot
    fig.show()

if __name__ == "__main__":
    main()
