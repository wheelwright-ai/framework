import re
from pathlib import Path

file_path = Path("wai/teach_reconciliation.py")
content = file_path.read_text()

# Pattern to find the second 'warnings = []' inside perform_teaching_adoption
# It needs to be precise enough to not match the first one.
# It should be after 'merge_strategy = ...' and before 'try:'
pattern = re.compile(r"""(    safe_to_auto_adopt = teaching\['metadata'\].get\('safe_to_auto_adopt', False\)
    merge_strategy = teaching\['metadata'\].get\('merge_strategy', 'overwrite'\)
    
    warnings = \[\]

    try:)""")

# Replace the matched section by removing the 'warnings = []' line
new_content = pattern.sub(r"""    safe_to_auto_adopt = teaching['metadata'].get('safe_to_auto_adopt', False)
    merge_strategy = teaching\['metadata'\].get\('merge_strategy', 'overwrite'\)
    
    try:""", content, count=1) # Ensure only one replacement

file_path.write_text(new_content)
print("Successfully removed duplicate warnings = [] from wai/teach_reconciliation.py")