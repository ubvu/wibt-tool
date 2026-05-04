#!/bin/bash

# --- CONFIGURATION: Add your pairs here ---
# Format: paper_name_without_extension|context_string
INPUT_DATA="
2024.04.19.24304365v1.full|general
3716553.3750816|psychology
CLS_Transnationalism in the Works of Cornélie Huygens_v2|general
EVOSTAR_2026_hexacopters (3)|tweede-kamer
Final Paper_Transnationalism and Cornélie Huygens_CJS|general
Infancy - 2022 - Chen - Infant locomotion shapes proximity to adults during everyday play in the U S|psychology
Korthals Altes (2023) belonging online classrooms|psychology
PP___Is_there_a_paradox_in_blockchain_governance____CBI__Lisbon_|tweede-kamer
PP___The_Human_Factor_in_blockchain_governance___CBA__Lille_|tweede-kamer
PROOFREAD|general
Reallocation_not_expansion|tweede-kamer
Rosbrook_2025_Shorttermheatacclimationcarbohydrates_MSSE|general
Short_sale_collateral|tweede-kamer
WCCI_2026_LamarkianLimits (1)|tweede-kamer
Willemse et al (2025) Cross-faculty perspectives of teachers on inclusive higher education  a university-wide study in the Netherlands|psychology
zsz156|general
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
