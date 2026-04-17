#!/bin/bash
# Generate llms-full.txt from all documentation sources
# This comprehensive export is what agents fetch to learn Wheelwright

OUTPUT="framework/docs/llms-full.md"

# Read version dynamically from WAI-State.json
VERSION=$(jq -r '.wheel.version // "unknown"' "WAI-Spoke/WAI-State.json" 2>/dev/null || echo "unknown")

echo "# Wheelwright AI Framework - Complete Documentation" > "$OUTPUT"
echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUTPUT"
echo "# Version: $VERSION" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "This file contains the complete Wheelwright documentation including:" >> "$OUTPUT"
echo "- Framework guides and setup instructions" >> "$OUTPUT"
echo "- Lug Schema Specification (complete field reference)" >> "$OUTPUT"
echo "- Skill Contract Specification (how to build skills)" >> "$OUTPUT"
echo "- Hub policies and communication protocols" >> "$OUTPUT"
echo "- Built-in skills documentation" >> "$OUTPUT"
echo "- E2E benchmark validation details" >> "$OUTPUT"
echo "- Use cases and real-world examples" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Add root-level specification files first (architectural foundation)
echo "Adding root specs..." >&2

if [ -f "WAI-Lug-Schema-Spec.md" ]; then
    echo "# Lug Schema Specification (Complete)" >> "$OUTPUT"
    echo "Source: WAI-Lug-Schema-Spec.md" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "WAI-Lug-Schema-Spec.md" >> "$OUTPUT"
    echo -e "\n\n---\n" >> "$OUTPUT"
fi

if [ -f "WAI-Skill-Contract-Spec.md" ]; then
    echo "# Skill Contract Specification (Complete)" >> "$OUTPUT"
    echo "Source: WAI-Skill-Contract-Spec.md" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "WAI-Skill-Contract-Spec.md" >> "$OUTPUT"
    echo -e "\n\n---\n" >> "$OUTPUT"
fi

# Add hub policies (inherited by all spokes)
echo "Adding hub policies..." >&2

if [ -f "hub/BRIEF.md" ]; then
    echo "# Hub Policies and Communication Style" >> "$OUTPUT"
    echo "Source: hub/BRIEF.md" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "hub/BRIEF.md" >> "$OUTPUT"
    echo -e "\n\n---\n" >> "$OUTPUT"
fi

if [ -f "hub/WAI-Integrity.md" ]; then
    echo "# WAI Integrity Contract (Data Protection)" >> "$OUTPUT"
    echo "Source: hub/WAI-Integrity.md" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "hub/WAI-Integrity.md" >> "$OUTPUT"
    echo -e "\n\n---\n" >> "$OUTPUT"
fi

# Add all framework/docs markdown files (guides, tutorials, references)
echo "Adding framework docs..." >&2

find framework/docs -name "*.md" -not -name "llms-full.md" | sort | while read -r file; do
    title=$(head -1 "$file" | sed 's/^# //')
    echo "# $title" >> "$OUTPUT"
    echo "Source: $file" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
    echo -e "\n\n---\n" >> "$OUTPUT"
done

# Add summary footer
echo "" >> "$OUTPUT"
echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "**End of Documentation**" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Wheelwright AI Framework v${VERSION}" >> "$OUTPUT"
echo "Agents communicate through files. Institutions remember through Lugs." >> "$OUTPUT"
echo "" >> "$OUTPUT"

echo "✓ Generated: $OUTPUT"
echo "  $(wc -l < "$OUTPUT") lines"
echo "  $(wc -w < "$OUTPUT") words"
echo "  $(du -h "$OUTPUT" | cut -f1) size"
