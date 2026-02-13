#!/bin/bash
# Generate llms-full.txt from all markdown files in framework/docs/
# This flat export is what agents fetch to learn Wheelwright

OUTPUT="framework/docs/llms-full.txt"

echo "# Wheelwright AI Framework Documentation" > "$OUTPUT"
echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT"
echo "# Source: framework/docs/" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Find all .md files, sort, concatenate with source paths
find framework/docs -name "*.md" -not -name "llms-full.txt" | sort | while read -r file; do
    # Extract title from first line (assumes "# Title" format)
    title=$(head -1 "$file" | sed 's/^# //')

    echo "# $title" >> "$OUTPUT"
    echo "Source: $file" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
    echo -e "\n\n---\n" >> "$OUTPUT"
done

echo "Generated: $OUTPUT"
echo "$(wc -l < "$OUTPUT") lines"
