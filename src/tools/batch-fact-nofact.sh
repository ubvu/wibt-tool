#!/bin/bash

# --- CONFIGURATION: Add your pairs here ---
# Format: paper_name_without_extension|context_string
INPUT_DATA="
"
# ------------------------------------------

# Create results directory if it doesn't exist
mkdir -p results

# Read the input data line by line
echo "$INPUT_DATA" | while IFS='|' read -r paper_base context; do
    
    # Skip empty lines
    [[ -z "$paper_base" ]] && continue

    # Define the actual file name (adding .md)
    paper_file="${paper_base}.md"

    # Run twice: once for 'fact' and once for 'nofact'
    for mode in "fact" "nofact"; do
        
        # Define the primary output file path to check for existence
        # We use the '-ot' flag file as the indicator that this run is complete
        output_check_file="results/${paper_base}_summary_english_${mode}.md"

        # Check if the output file already exists
        if [[ -f "$output_check_file" ]]; then
            echo ">>> Skipping $paper_file ($mode) - Output already exists: $output_check_file"
            continue
        fi

        # Determine the -pf flag based on mode
        pf_flag=""
        if [[ "$mode" == "fact" ]]; then
            pf_flag="-pf"
        fi

        echo "------------------------------------------------"
        echo "Processing: $paper_file | Mode: $mode"
        echo "------------------------------------------------"

        # Execute the command
        uv run src/cli/summary.py \
            -i /var/home/geoffrey/Documents/papers-tussentijdse-evaluatie/"$paper_file" \
            -st static \
            -it 10 \
            -sc "$context" \
            -fc "$context" \
            -tc "$context" \
            # -ot "results/${paper_base}_summary_translated_${mode}.md" \
            -oh "results/${paper_base}_history_${mode}.json" \
            -osh "results/${paper_base}_score_history_${mode}.csv" \
            -oes "results/${paper_base}_summary_english_${mode}.md" \
            -okf "results/${paper_base}_keyfacts_${mode}.json" \
            $pf_flag

    done
done

echo "------------------------------------------------"
echo "All tasks completed!"
