#!/bin/bash

# --- CONFIGURATION ---
# Replace this with the actual path to your translation program
PROGRAM="src/cli/translation.py" 

# The subfolders to look for inside the provided results directory.
# Format: "subfolder_name:context_value"
FOLDERS=("psychology:psychology" "general:general" "tweede-kamer:tweede-kamer")

# --- ARGUMENT CHECK ---

# Check if the user provided the results directory argument
if [ -z "$1" ]; then
    echo "Error: No results directory provided."
    echo "Usage: $0 <path_to_results_folder>"
    echo "Example: $0 ./results"
    exit 1
fi

# Assign the first argument to RESULTS_DIR
RESULTS_DIR="${1%/}"

# Check if the provided path is actually a directory
if [ ! -d "$RESULTS_DIR" ]; then
    echo "Error: '$RESULTS_DIR' is not a valid directory."
    exit 1
fi

echo "Starting translation batch process..."
echo "Results Directory: $RESULTS_DIR"
echo "----------------------------------------------------------"

# --- SCRIPT LOGIC ---

for entry in "${FOLDERS[@]}"; do
    # Split the entry into subfolder name and context
    IFS=":" read -r SUB_NAME CONTEXT <<< "$entry"

    # Construct the full path to the subfolder inside results/
    SUBFOLDER_PATH="$RESULTS_DIR/$SUB_NAME"

    echo "----------------------------------------------------------"
    echo "Checking folder: $SUB_NAME (Context: $CONTEXT)"
    echo "----------------------------------------------------------"

    # Check if the subfolder exists
    if [ ! -d "$SUBFOLDER_PATH" ]; then
        echo "Warning: Subfolder '$SUB_NAME' not found in '$RESULTS_DIR'. Skipping..."
        continue
    fi

    # Loop through only the files that end with '-english-summary.md'
    shopt -s nullglob
    found_files=0
    for INPUT_FILE in "$SUBFOLDER_PATH"/*-english-summary.md; do
        found_files=$((found_files + 1))
        
        # Generate the output filename by replacing '-english-summary.md' 
        # with '-translated-summary.md'
        OUT_FILE="${INPUT_FILE/-english-summary.md/-translated-summary.md}"

        # Check if the translated file already exists
        if [ -f "$OUT_FILE" ]; then
            echo "Skipping: '$(basename "$INPUT_FILE")' (Translation already exists)"
            continue
        fi

        echo "Translating: $(basename "$INPUT_FILE")"

        # Execute the command
        uv run "$PROGRAM" \
            -tc "$CONTEXT" \
            -i "$INPUT_FILE" \
            -o "$OUT_FILE"

        # Check if the command succeeded
        if [ $? -eq 0 ]; then
            echo "Successfully translated: $(basename "$OUT_FILE")"
        else
            echo "ERROR: Failed to translate $(basename "$INPUT_FILE")"
        fi
    done

    if [ $found_files -eq 0 ]; then
        echo "No '-english-summary.md' files found in $SUBFOLDER_PATH"
    fi

    shopt -u nullglob
done

echo "----------------------------------------------------------"
echo "Translation batch processing complete."
