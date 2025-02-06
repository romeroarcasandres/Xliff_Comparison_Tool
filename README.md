# XLIFF Comparison Tool

This script compares two XLIFF files and generates a detailed HTML report highlighting the differences between translation units.

## Overview

The XLIFF Comparison Tool is designed to analyze and compare two XLIFF files, generating a comprehensive HTML report that shows:
- Source text from the first file
- Target translations from both files
- Detailed differences between translations
- Missing translation units in either file

The tool uses diff-match-patch algorithm for difference analysis to highlight changes between translations and presents the results in a clean, user-friendly HTML format with proper styling and formatting.

## Requirements

- Python 3
- xml.etree.ElementTree (included in Python standard library)
- diff_match_patch (Google's diff-match-patch library)
- sys (included in Python standard library)

## Features

- Side-by-side comparison of translations
- Difference highlighting in the target translations
- Source text reference for context
- Detection of missing translation units
- Clean, responsive HTML report generation
- Debug mode for troubleshooting
- Support for XLIFF 1.2 format
- Proper handling of XML namespaces
- Customizable output file naming

## Usage

Run the script from the command line:
```
python compare_xliff.py file1.xliff file2.xliff [output.html]
```

Arguments:
- `file1.xliff`: First XLIFF file (source of comparison)
- `file2.xliff`: Second XLIFF file to compare against
- `output.html`: Optional output file name (defaults to "report.html")

## Report Format

The generated HTML report includes:
- File information header
- Comparison table with columns for:
  - Translation Unit ID
  - Source text
  - Target text from File 1
  - Target text from File 2
  - Highlighted differences
- Color-coded difference highlighting
- Responsive design for better readability
- Proper handling of whitespace and special characters

## Debug Mode

Set `DEBUG = True` at the start of the script to enable detailed debug messages, including:
- File parsing progress
- Translation unit detection
- Content extraction details
- Error messages for troubleshooting

## Error Handling

The script includes robust error handling for:
- Missing command line arguments
- File parsing errors
- Missing translation units
- Output file writing issues
- XML namespace resolution
- Empty or malformed elements

## Important Notes

- The script assumes XLIFF 1.2 format with proper namespace declarations
- All files should be properly formatted XLIFF files
- The tool preserves all text content, including nested elements
- Translation unit IDs are used for matching entries between files
- The report is generated with responsive CSS for better viewing

## License

This project is governed by the CC BY-NC 4.0 license. For comprehensive details, kindly refer to the LICENSE file included with this project.
