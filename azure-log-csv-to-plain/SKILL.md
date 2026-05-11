---
name: azure-log-csv-to-plain
description: >
  Convert Azure-exported log CSV files such as query_data.csv into readable plain log files.
  Use when the user has an Azure Logs or Log Analytics export with columns like "TimeGenerated [UTC]"
  and "LogEntry", and wants the CSV wrapper, header row, escaped double quotes removed,
  and inline JSON payloads reformatted across multiple lines.
  Keywords: azure log export, query_data.csv, csv-wrapped logs, log analytics csv, readable log file,
  plain log format.
---

# Azure Log CSV To Plain

Use this skill when a user gives you the path to an Azure-exported CSV log file and wants it rewritten
into a normal line-oriented log file with a `.log` extension.

## Expected Input

The user should provide a file path.

Typical source shape:
- Header row with `"TimeGenerated [UTC]",LogEntry`
- Each following line starts with a quoted timestamp column
- The actual log message is wrapped as the second CSV field
- Embedded quotes inside the log message are doubled as `""`

## Workflow

1. Read a small sample from the file to confirm it matches the Azure CSV export pattern.
2. Rewrite the file in place by:
- removing the CSV header row
- removing the first CSV column and outer CSV quoting
- converting doubled quotes `""` back to normal `"`
- pretty-printing valid inline JSON payloads using standard multi-line JSON formatting
3. Rename the converted file so the output ends with `.log`.
4. Validate by reading the first few lines and confirming they are plain log entries with no CSV header.

## Command

Run the bundled script with the file path the user provided:

```bash
perl /Users/pabasara/.agents/skills/azure-log-csv-to-plain/azure_csv_logs_to_plain.pl "/path/to/query_data.csv"
```

The script rewrites the content and renames the result to `/path/to/query_data.log`.

## Validation

- The first line should now begin with the real log content, not `"TimeGenerated [UTC]",LogEntry`
- Lines should no longer start with the exported timestamp column
- JSON fragments inside log messages should use normal quotes instead of doubled CSV quotes
- Inline JSON payloads should be expanded across multiple lines with indentation
- The converted file should now have a `.log` extension

## Notes

- This rewrites the content and renames the result to a `.log` file in the same directory.
- If the file does not match the expected export pattern, stop and tell the user instead of forcing the conversion.