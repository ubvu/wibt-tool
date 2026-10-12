#!/bin/bash

# --- CONFIGURATION ---

# The directory where your papers are located
INPUT_DIR="/var/home/geoffrey/Documents/papers-tussentijdse-evaluatie"

# List of models to run
MODELS=(
    "gemma3-12b-120k"
    "gpt-oss-120b-120k"
)

# List of "tuples" in the format: "filename|context"
PAPERS_DATA=(
    "title|context"
)

# Create results directory if it doesn't exist
mkdir -p results

# --- SCRIPT LOGIC ---

for entry in "${PAPERS_DATA[@]}"; do
    # Split the entry into paper and context
    IFS='|' read -r paper CONTEXT <<< "$entry"

    echo "=================================================="
    echo "FILE: $paper"
    echo "CONTEXT: $CONTEXT"
    echo "=================================================="

    for model in "${MODELS[@]}"; do
        # Set the environment variable for the command
        export DEFAULT_SUMMARY_MODEL="$model"

        # Determine the short postfix for the filename
        case "$model" in
            "gemma3-12b-120k")
                POSTFIX="gemma3"
                ;;
            "gpt-oss-120b-120k")
                POSTFIX="gpt-oss"
                ;;
            *)
                POSTFIX="unknown"
                ;;
        esac

        echo ">> MODEL: $model (Postfix: $POSTFIX)"

        for mode in "refine" "static"; do
            echo "   >> Running mode: $mode"

            # Strip extension for clean filenames
            PAPER_BASE="${paper%.*}"

            # We inject ${POSTFIX} into the filename to distinguish between model runs
            uv run src/cli/summary.py \
                -i "$INPUT_DIR/$paper" \
                -st "$mode" \
                -it 15 \
                -sc "$CONTEXT" \
                -fc "$CONTEXT" \
                -tc "$CONTEXT" \
                -o "results/${PAPER_BASE}_summary_${mode}_${POSTFIX}.md" \
                -oh "results/${PAPER_BASE}_history_${mode}_${POSTFIX}.json" \
                -osh "results/${PAPER_BASE}_score_history_${mode}_${POSTFIX}.csv" \
                -oes "results/${PAPER_BASE}_summary_english_${mode}_${POSTFIX}.md" \
                -okf "results/${PAPER_BASE}_keyfacts_${mode}_${POSTFIX}.json"
                
            echo "   >> Finished $mode"
        done
        echo ""
    done
done

echo "All tasks completed!"
