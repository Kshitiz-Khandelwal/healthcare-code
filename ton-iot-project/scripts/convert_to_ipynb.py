"""
Convert annotated .py scripts into .ipynb Jupyter Notebooks
Uses nbformat to construct and save notebooks.
"""
import os
import glob
import nbformat as nbf

def convert_script_to_notebook(py_path, ipynb_path):
    print(f"Converting {py_path} -> {ipynb_path}...")
    
    with open(py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    nb = nbf.v4.new_notebook()
    
    current_cell_type = None # 'code' or 'markdown'
    current_cell_source = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check for cell markers
        if stripped.startswith("# %% [markdown]"):
            # Save previous cell if exists
            if current_cell_source:
                add_cell(nb, current_cell_type, current_cell_source)
            current_cell_type = 'markdown'
            current_cell_source = []
        elif stripped.startswith("# %%"):
            # Save previous cell if exists
            if current_cell_source:
                add_cell(nb, current_cell_type, current_cell_source)
            current_cell_type = 'code'
            current_cell_source = []
        else:
            # If no cell has started, default to code (except for imports at the top)
            if current_cell_type is None:
                current_cell_type = 'code'
            current_cell_source.append(line)
            
    # Add the last cell
    if current_cell_source:
        add_cell(nb, current_cell_type, current_cell_source)
        
    with open(ipynb_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"  [OK] Saved {ipynb_path}")

def add_cell(nb, cell_type, lines_list):
    # Strip leading/trailing blank lines
    while lines_list and lines_list[0].strip() == "":
        lines_list.pop(0)
    while lines_list and lines_list[-1].strip() == "":
        lines_list.pop()
        
    if not lines_list:
        return
        
    source_str = "".join(lines_list).strip()
    
    if cell_type == 'markdown':
        # Remove comment marks (# ) from markdown lines
        cleaned_lines = []
        for line in lines_list:
            stripped_line = line.strip()
            if stripped_line.startswith("#"):
                # Remove leading '#' and up to one space after it
                content = line.lstrip().lstrip("#")
                if content.startswith(" "):
                    content = content[1:]
                cleaned_lines.append(content)
            else:
                cleaned_lines.append(line)
        source_str = "".join(cleaned_lines).strip()
        nb['cells'].append(nbf.v4.new_markdown_cell(source_str))
    else:
        nb['cells'].append(nbf.v4.new_code_cell(source_str))

def main():
    notebooks_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notebooks")
    py_files = sorted(glob.glob(os.path.join(notebooks_dir, "*.py")))
    
    if not py_files:
        print(f"No .py files found in {notebooks_dir}!")
        return
        
    for py_file in py_files:
        ipynb_file = py_file[:-3] + ".ipynb"
        convert_script_to_notebook(py_file, ipynb_file)
        
if __name__ == "__main__":
    main()
