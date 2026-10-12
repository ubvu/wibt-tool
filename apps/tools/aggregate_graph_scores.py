import pandas as pd
import plotly.graph_objects as go
import argparse
import os
import sys
import glob
import numpy as np

def main():
    # 1. Set up Command Line Argument Parsing
    parser = argparse.ArgumentParser(
        description="Compare scores and convergence speed for 4 combinations."
    )
    parser.add_argument(
        "directory", 
        help="The directory containing the CSV files (e.g., '/path/to/data/')"
    )
    
    args = parser.parse_args()
    data_dir = args.directory

    if not os.path.isdir(data_dir):
        print(f"Error: {data_dir} is not a valid directory.")
        sys.exit(1)

    # 2. Define Combinations and Visual Settings
    models = ['gemma3', 'gpt-oss']
    methods = ['refine', 'static']
    
    # Color Mapping: Unique color per combination
    combo_colors = {
        ('gemma3', 'refine'): '#0000FF',   # Blue
        ('gemma3', 'static'): '#00FFFF',   # Cyan
        ('gpt-oss', 'refine'): '#FF0000',  # Red
        ('gpt-oss', 'static'): '#FF00FF',  # Magenta
    }
    
    score_columns = ['syntactic_clarity', 'jargon', 'information_density', 
                     'structural_cohesion', 'faithfulness', 'completeness']
    total_column = 'total_score'
    markers = ['circle', 'square', 'triangle-up', 'diamond', 'cross', 'star']

    # Data Containers
    score_averages = {} 
    peak_iterations = {} 

    print(f"Scanning directory: {data_dir}\n")

    # 3. Load and Aggregate Data
    for model in models:
        for method in methods:
            # Pattern matches: _{method}_{model}.csv
            pattern = os.path.join(data_dir, f"*_{method}_{model}.csv")
            matching_files = glob.glob(pattern)

            if not matching_files:
                print(f"⚠️  No files found for {method}_{model}. Skipping.")
                continue
            
            print(f"Processing {len(matching_files)} files for {method}_{model}...")
            
            dfs_for_averaging = []
            peak_indices_for_this_combo = []

            for f in matching_files:
                try:
                    # Load the specific file
                    temp_df = pd.read_csv(f)
                    
                    # --- THE FIX: Use temp_df, not a global df ---
                    if total_column in temp_df.columns:
                        # Ensure total_column is numeric so idxmax doesn't fail
                        temp_df[total_column] = pd.to_numeric(temp_df[total_column], errors='coerce')
                        
                        # Find the index of the highest score in THIS file
                        # idxmax() returns the first index where the max occurs
                        peak_idx = temp_df[total_column].idxmax()
                        peak_indices_for_this_combo.append(peak_idx)
                    
                    dfs_for_averaging.append(temp_df)
                except Exception as e:
                    print(f"  ❌ Error reading {os.path.basename(f)}: {e}")

            if dfs_for_averaging:
                # Combine all dataframes for this combination
                combined_df = pd.concat(dfs_for_averaging)
                
                # Select only numeric columns to prevent TypeError on mean()
                numeric_only_df = combined_df.select_dtypes(include=['number'])
                
                # Average the scores by row index (point in time)
                avg_df = numeric_only_df.groupby(combined_df.index).mean()
                
                score_averages[(model, method)] = avg_df
                peak_iterations[(model, method)] = peak_indices_for_this_combo
                print(f"  ✅ Done. (Files: {len(dfs_for_averaging)}, Peaks: {len(peak_indices_for_this_combo)})")

    if not score_averages:
        print("\nError: No valid data files were found.")
        sys.exit(1)

    # --- PRINT SUMMARY STATISTICS TO CONSOLE ---
    print("\n" + "="*50)
    print("CONVERGENCE SPEED SUMMARY (Avg Iteration to Peak)")
    print("="*50)
    for combo, indices in peak_iterations.items():
        if indices:
            print(f"{combo[0]}_{combo[1]:<7} | Avg Peak Row: {np.mean(indices):.2f} | Range: [{min(indices)}-{max(indices)}]")
    print("="*50 + "\n")

    # 4. Create FIGURE 1: Score Comparison Graph
    fig_scores = go.Figure()
    for (model, method), df in score_averages.items():
        combo_name = f"{model}_{method}"
        combo_color = combo_colors.get((model, method), '#888888')

        for i, col in enumerate(score_columns):
            if col in df.columns:
                fig_scores.add_trace(go.Scatter(
                    x=df.index, y=df[col], mode='lines+markers',
                    name=f"{combo_name}-{col}",
                    line=dict(color=combo_color, width=1.5),
                    marker=dict(symbol=markers[i % len(markers)], size=5),
                    opacity=0.4, yaxis='y1'
                ))
        
        if total_column in df.columns:
            fig_scores.add_trace(go.Scatter(
                x=df.index, y=df[total_column], mode='lines+markers',
                name=f"TOTAL: {combo_name}",
                line=dict(color=combo_color, width=5),
                marker=dict(symbol='diamond', size=12),
                yaxis='y2'
            ))

    fig_scores.update_layout(
        title='Aggregated Score Comparison (Averages)',
        xaxis=dict(title='Row Index'),
        yaxis=dict(title='Metric Scores', range=[0, 5], gridcolor='lightgray'),
        yaxis2=dict(title='Total Score', range=[0, 30], overlaying='y', side='right'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
        template='plotly_white', hovermode='x unified'
    )

    # 5. Create FIGURE 2: Speed Bar Chart
    fig_speed = go.Figure()
    for (model, method), indices in peak_iterations.items():
        combo_name = f"{model}_{method}"
        fig_speed.add_trace(go.Bar(
            x=[combo_name], y=[np.mean(indices)], name=combo_name,
            marker_color=combo_colors.get((model, method)),
            text=[f"{np.mean(indices):.2f}"], textposition='auto'
        ))

    fig_speed.update_layout(
        title='Average Iteration to Reach Peak Score (Lower is Faster)',
        xaxis=dict(title='Combination'),
        yaxis=dict(title='Average Row Index (Iteration)'),
        template='plotly_white'
    )

    # 6. Show both
    print("Opening Comparison and Speed graphs...")
    fig_scores.show()
    fig_speed.show()

if __name__ == "__main__":
    main()
