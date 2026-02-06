# Small Tier Benchmark Task

## Objective
Add structured logging to the DataFormatter class to track all formatting operations.

## Requirements
1. Import the StructuredLogger from src.utils.logger
2. Add a logger instance to the DataFormatter class
3. Log at the start of the `format()` method with input data
4. Log after each field is formatted (name, email, timestamp)
5. Log the final result before returning
6. Use appropriate log levels (info for normal operations, error for failures)

## Success Criteria
- Logger properly imported
- Logger instance created in __init__
- At least 5 log statements added to format() method
- Logs include relevant context (field names, values)
- No errors introduced
- Tests still pass

## Files Needed
- src/formatters/data.py (primary - needs modification)
- src/utils/logger.py (reference - understand the API)

## Files NOT Needed
- reference/*.md (large documentation files - irrelevant to this task)
- tests/test_formatter.py (not changing test behavior)
