import pandas as pd
import plotly.graph_objects as go
import argparse
import os
import sys
import glob
import numpy as np

def main():
    parser = argparse.ArgumentParser(
        description="Compare scores and convergence speed."
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

    models = ['gemma3', 'gpt-oss']
    methods = ['refine', 'static']
    
    combo_colors = {
        ('gemma3', 'refine'): '#0000FF', ('gemma3', 'static'): '#00FFFF',
        ('gpt-oss', 'refine'): '#FF0000', ('gpt-oss', 'static'): '#FF00FF',
    }
    
    score_columns = ['syntactic_clarity', 'jargon', 'information_density', 
                     'structural_cohesion', 'faithfulness', 'completeness']
    total_column = 'total_score'
    markers = ['circle', 'square', 'triangle-up', 'diamond', 'cross', 'star']

    score_averages = {} 
    peak_iterations = {} 

    print(f"Scanning directory: {data_dir}\n")

    # Loop through each combination to find matching files
    for model in models:
        for method in methods:
            pattern = os.path.join(data_dir, f"*_{method}_{model}.csv")
            matching_files = glob.glob(pattern)

            if not matching_files:
                print(f"⚠️  No files found for {method}_{model}. Skipping.")
                continue
            
            print(f"\n📂 Processing Combination: {method}_{model}")
            print(f"   Found {len(matching_files)} matching files.")
            
            dfs_for_averaging = []
            peak_indices_for_this_combo = []

            for f in matching_files:
                try:
                    # Load the specific file
                    file_df = pd.read_csv(f)
                    
                    # --- DEBUG: Check if total_column exists ---
                    if total_column not in file_df.columns:
                        print(f"   ❌ ERROR: '{total_column}' column missing in {os.path.basename(f)}")
                        continue
                    
                    # --- DEBUG: Force numeric conversion ---
                    numeric_scores = pd.to_numeric(file_df[total_column], errors='coerce')
                    if numeric_scores.isna().all():
                        print(f"   ❌ ERROR: '{total_column}' is not numeric in {os.path.basename(f)}")
                        continue
                    
                    # --- THE FIX: Find the peak on THIS file's data ---
                    peak_idx = numeric_scores.idxmax()
                    peak_max_val = numeric_scores.max()
                    peak_indices_for_this_combo.append(peak_idx)
                    
                    print(f"   📄 {os.path.basename(f):<40} | Peak Row: {peak_idx:<5} | Max Score: {peak_max_val:.1f}")
                    
                    dfs_for_averaging.append(file_df)
                    
                except Exception as e:
                    print(f"   ❌ Exception reading {os.path.basename(f)}: {e}")

            if dfs_for_averaging:
                print(f"   📊 Success: {len(dfs_for_averaging)} files processed.")
                
                # Combine for averaging scores
                combined_df = pd.concat(dfs_for_averaging)
                numeric_only_df = combined_df.select_dtypes(include=['number'])
                avg_df = numeric_only_df.groupby(combined_df.index).mean()
                
                score_averages[(model, method)] = avg_df
                peak_iterations[(model, method)] = peak_indices_for_this_combo

    if not score_averages:
        print("\n❌ Error: No valid data files were found.")
        sys.exit(1)

    # --- DEBUG OUTPUT: Show all raw peaks found ---
    print("\n" + "="*70)
    print("DETAILED PEAK ANALYSIS")
    print("="*70)
    for combo, indices in peak_iterations.items():
        avg_val = np.mean(indices)
        print(f"{combo[0]}_{combo[1]}: Indices = {indices}")
        print(f"  → Avg Peak Iteration: {avg_val:.2f}")
        print("-" * 70)
    print("="*70 + "\n")

    # --- FIGURE 1: Score Comparison Graph ---
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

    # --- FIGURE 2: Speed Bar Chart ---
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

    print("🚀 Opening graphs in browser...")
    fig_scores.show()
    fig_speed.show()

if __name__ == "__main__":
    main()
