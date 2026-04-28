import pandas as pd
import plotly.graph_objects as go
import argparse
import os
import sys

def main():
    # 1. Set up Command Line Argument Parsing
    parser = argparse.ArgumentParser(
        description="Compare 4 datasets (2 models x 2 methods) where each combo has a unique color."
    )
    parser.add_argument(
        "base_path", 
        help="Base path prefix (e.g., '/path/to/file' looks for '/path/to/file_gemma3_refine.csv', etc.)"
    )
    
    args = parser.parse_args()
    base = args.base_path

    # 2. Define the 4 combinations and their unique color assignments
    # Colors: Blue/Cyan for Gemma, Red/Magenta for GPT-OSS
    combinations = [
        ('gemma3', 'refine', '#0000FF'),  # Pure Blue
        ('gemma3', 'static', '#00FFFF'),  # Cyan
        ('gpt-oss', 'refine', '#FF0000'), # Red
        ('gpt-oss', 'static', '#FF00FF'), # Magenta
    ]
    
    models = ['gemma3', 'gpt-oss']
    methods = ['refine', 'static']
    
    data_store = {}
    missing_files = []

    # 3. Load the 4 files
    for model, method, color in combinations:
        filename = f"{base}_{method}_{model}.csv"
        if os.path.exists(filename):
            try:
                data_store[(model, method)] = pd.read_csv(filename)
                print(f"Successfully loaded: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        else:
            missing_files.append(filename)

    if missing_files:
        print("\nError: The following files are missing:")
        for f in missing_files:
            print(f"  - {f}")
        sys.exit(1)

    # Constants
    score_columns = ['syntactic_clarity', 'jargon', 'information_density', 
                     'structural_cohesion', 'faithfulness', 'completeness']
    total_column = 'total_score'
    markers = ['circle', 'square', 'triangle-up', 'diamond', 'cross', 'star']

    # 4. Create Figure
    fig = go.Figure()

    # 5. Plotting Loop
    for model, method, combo_color in combinations:
        df = data_store[(model, method)]
        combo_name = f"{method}_{model}"
        
        # A. Plot Individual Metrics (Thin & Transparent)
        for i, col in enumerate(score_columns):
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode='lines+markers',
                    name=f"{combo_name} - {col}",
                    line=dict(color=combo_color, width=1.5),
                    marker=dict(symbol=markers[i % len(markers)], size=5),
                    opacity=0.5,  # Make metrics faded so they don't overwhelm the total
                    yaxis='y1'
                )
            )
        
        # B. Plot Total Score (Thick & Bold)
        # This is the "Identity" line for this combination
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[total_column],
                mode='lines+markers',
                name=f"TOTAL: {combo_name}",
                line=dict(color=combo_color, width=5),
                marker=dict(symbol='diamond', size=12),
                yaxis='y2'
            )
        )

    # 6. Configure Layout
    fig.update_layout(
        title='Comprehensive Comparison: 4-Way Model/Method Breakdown',
        xaxis=dict(title='Row Index'),
        
        # Left Y-Axis: Metrics (Scale 0-5)
        yaxis=dict(
            title=dict(text='Metric Scores (Faded)', font=dict(color='blue')),
            tickfont=dict(color='blue'),
            range=[0, 5],
            gridcolor='lightgray'
        ),
        
        # Right Y-Axis: Totals (Scale 0-30)
        yaxis2=dict(
            title=dict(text='Total Score (Bold)', font=dict(color='black')),
            tickfont=dict(color='black'),
            range=[0, 30], # Updated to 30 as requested
            overlaying='y',
            side='right'
        ),
        
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        ),
        
        template='plotly_white',
        hovermode='x unified'
    )

    # 7. Show
    print("\nGenerating interactive graph in your browser...")
    fig.show()

if __name__ == "__main__":
    main()
