#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from diff_match_patch import diff_match_patch

# Enable debug messages by setting DEBUG to True
DEBUG = True

def debug_print(msg):
    if DEBUG:
        print(msg)

def generate_html_template(file1_name, file2_name):
    """Generate the HTML template for the report with updated headers."""
    return [f'''<html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
            }}
            .file-info {{
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <h1>Comparison Report</h1>
        <div class="file-info">
            <strong>File 1:</strong> {file1_name}<br>
            <strong>File 2:</strong> {file2_name}
        </div>
        <table>
            <tr>
                <th>Translation Unit</th>
                <th>Source</th>
                <th>{file1_name} (Target)</th>
                <th>{file2_name} (Target)</th>
                <th>Differences</th>
            </tr>
    ''']

def parse_xliff(file, include_source=False):
    """
    Parse an XLIFF file and return a dictionary.

    If include_source is True, each entry is a dict:
        { trans_unit_id: { "source": source_text, "target": target_text } }
    Otherwise, returns a dict mapping:
        { trans_unit_id: target_text }

    This function uses itertext() to extract all text from the element,
    and handles the default namespace used in the file.
    """
    debug_print(f"DEBUG: Parsing file {file}")
    try:
        tree = ET.parse(file)
    except Exception as e:
        debug_print(f"ERROR: Could not parse file {file}: {e}")
        return {}
    root = tree.getroot()
    debug_print(f"DEBUG: Root tag for {file}: {root.tag}")

    # Define a namespace dictionary for the default namespace.
    ns = {'ns': 'urn:oasis:names:tc:xliff:document:1.2'}

    # Use the namespace prefix in your XPath queries.
    trans_units = root.findall('.//ns:trans-unit', ns)
    debug_print(f"DEBUG: Found {len(trans_units)} trans-unit elements in {file}")

    data = {}
    for trans_unit in trans_units:
        tu_id = trans_unit.get('id')
        if not tu_id:
            debug_print("DEBUG: Found trans-unit without id, skipping")
            continue

        source_elem = trans_unit.find('ns:source', ns)
        target_elem = trans_unit.find('ns:target', ns)

        # Use itertext() to join all text inside the element.
        source_text = ''.join(source_elem.itertext()).strip() if source_elem is not None else ""
        target_text = ''.join(target_elem.itertext()).strip() if target_elem is not None else ""
        
        debug_print(f"DEBUG: trans-unit id={tu_id}\n        source='{source_text}'\n        target='{target_text}'")
        
        if include_source:
            data[tu_id] = {"source": source_text, "target": target_text}
        else:
            data[tu_id] = target_text
    return data

def main(file1, file2, output_file="report.html"):
    # Parse File 1 (with source) and File 2 (target only)
    data1 = parse_xliff(file1, include_source=True)
    data2 = parse_xliff(file2, include_source=False)

    debug_print(f"DEBUG: Translation unit IDs in {file1}: {list(data1.keys())}")
    debug_print(f"DEBUG: Translation unit IDs in {file2}: {list(data2.keys())}")

    # Determine common translation unit IDs.
    # Adjust sorting as needed if IDs have a specific format (e.g., "t1", "t2", etc.).
    common_ids = sorted(set(data1.keys()).intersection(set(data2.keys())),
                          key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
    debug_print(f"DEBUG: Common translation unit IDs: {common_ids}")

    # Create an instance of diff_match_patch.
    dmp = diff_match_patch()

    html_parts = generate_html_template(file1, file2)

    # Process each common translation unit.
    for tu_id in common_ids:
        source_text = data1[tu_id]["source"]
        target1 = data1[tu_id]["target"]
        target2 = data2[tu_id]

        # Compute differences between the two target texts.
        diffs = dmp.diff_main(target1, target2)
        dmp.diff_cleanupSemantic(diffs)
        diff_html = dmp.diff_prettyHtml(diffs)

        html_parts.append(f'''
            <tr>
                <td>{tu_id}</td>
                <td><pre>{source_text}</pre></td>
                <td><pre>{target1}</pre></td>
                <td><pre>{target2}</pre></td>
                <td>{diff_html}</td>
            </tr>
        ''')

    # Optionally, process units missing in one file.
    missing_in_file2 = sorted(set(data1.keys()) - set(data2.keys()),
                                key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
    for tu_id in missing_in_file2:
        source_text = data1[tu_id]["source"]
        target1 = data1[tu_id]["target"]
        diff_html = "<span style='color:red;'>Translation unit missing in File 2</span>"
        html_parts.append(f'''
            <tr>
                <td>{tu_id}</td>
                <td><pre>{source_text}</pre></td>
                <td><pre>{target1}</pre></td>
                <td><pre></pre></td>
                <td>{diff_html}</td>
            </tr>
        ''')

    missing_in_file1 = sorted(set(data2.keys()) - set(data1.keys()),
                                key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
    for tu_id in missing_in_file1:
        target2 = data2[tu_id]
        diff_html = "<span style='color:red;'>Translation unit missing in File 1</span>"
        html_parts.append(f'''
            <tr>
                <td>{tu_id}</td>
                <td><pre></pre></td>
                <td><pre></pre></td>
                <td><pre>{target2}</pre></td>
                <td>{diff_html}</td>
            </tr>
        ''')

    html_parts.append('''
        </table>
    </body>
</html>
    ''')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("".join(html_parts))
        print(f"Report generated: {output_file}")
    except Exception as e:
        debug_print(f"ERROR: Could not write to {output_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_xliff.py file1.xliff file2.xliff [output.html]")
        sys.exit(1)
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) >= 4 else "report.html"
    main(file1, file2, output_file)
