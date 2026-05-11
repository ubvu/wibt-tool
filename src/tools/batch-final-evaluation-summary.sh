#!/bin/bash

# --- CONFIGURATION ---
PROGRAM="src/cli/summary.py" 

# Set the number of iterations here (cannot be changed via command line)
ITERATIONS=1

# The subfolders to look for inside the provided directory.
# Format: "subfolder_name:context_value"
# This allows you to have a folder named 'psych_data' but a context of 'psychology'
FOLDERS=("psychology:psychology" "general:general" "tweede-kamer:tweede-kamer")

# --- ARGUMENT CHECK ---

# Check if the user provided a directory argument
if [ -z "$1" ]; then
    echo "Error: No directory provided."
    echo "Usage: $0 <path_to_root_folder>"
    echo "Example: $0 ./my_data_folder"
    exit 1
fi

# Assign the first argument to ROOT_DIR and remove trailing slashes
ROOT_DIR="${1%/}"

# Check if the provided path is actually a directory
if [ ! -d "$ROOT_DIR" ]; then
    echo "Error: '$ROOT_DIR' is not a valid directory."
    exit 1
fi

echo "Starting batch process..."
echo "Root Directory: $ROOT_DIR"
echo "Iterations:     $ITERATIONS"
echo "----------------------------------------------------------"

# --- SCRIPT LOGIC ---

for entry in "${FOLDERS[@]}"; do
    # Split the entry into subfolder name and context using ':' as delimiter
    IFS=":" read -r SUB_NAME CONTEXT <<< "$entry"

    # Construct the full path to the subfolder
    SUBFOLDER_PATH="$ROOT_DIR/$SUB_NAME"

    echo "----------------------------------------------------------"
    echo "Processing folder: $SUB_NAME (Context: $CONTEXT)"
    echo "----------------------------------------------------------"

    # Check if the subfolder exists within the provided ROOT_DIR
    if [ ! -d "$SUBFOLDER_PATH" ]; then
        echo "Warning: Subfolder '$SUB_NAME' not found in '$ROOT_DIR'. Skipping..."
        continue
    fi

    # Create the results directory if it doesn't exist
    OUTPUT_DIR="results/$CONTEXT"
    mkdir -p "$OUTPUT_DIR"

    # Loop through all .md files in the subfolder
    shopt -s nullglob
    for INPUT_FILE in "$SUBFOLDER_PATH"/*.md; do
        
        # Get the filename without the directory and without the .md extension
        BASENAME=$(basename "$INPUT_FILE" .md)

        # Define output file paths
        OUT_SUM="$OUTPUT_DIR/${BASENAME}-english-summary.md"
        OUT_KEY="$OUTPUT_DIR/${BASENAME}-keyfacts.json"
        OUT_HIS="$OUTPUT_DIR/${BASENAME}-history.json"
        OUT_SCH="$OUTPUT_DIR/${BASENAME}-score-history.csv"

        # Check if the main output file already exists
        if [ -f "$OUT_SUM" ]; then
            echo "Skipping: '$BASENAME' (Summary already exists at $OUT_SUM)"
            continue
        fi

        echo "Running: $INPUT_FILE"

        # Execute the command
        uv run "$PROGRAM" \
            -st static \
            -sc "$CONTEXT" \
            -fc "$CONTEXT" \
            -tc "$CONTEXT" \
            -it "$ITERATIONS" \
            -i "$INPUT_FILE" \
            -oes "$OUT_SUM" \
            -okf "$OUT_KEY" \
            -oh "$OUT_HIS" \
            -osh "$OUT_SCH"

        # Check if the previous command succeeded
        if [ $? -eq 0 ]; then
            echo "Successfully processed: $BASENAME"
        else
            echo "ERROR: Failed to process $BASENAME"
        fi

    done
    shopt -u nullglob
done

echo "----------------------------------------------------------"
echo "Batch processing complete."
