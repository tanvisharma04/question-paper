import re
import json

def parse_modules(text):
    modules = []

    # Split based on "Module X:"
    module_splits = re.split(r'(Module \d+: [^\n]+)', text)

    for i in range(1, len(module_splits), 2):
        module_name = module_splits[i].strip()
        content_block = module_splits[i+1].strip()

        # First line/paragraph as description
        lines = content_block.split('\n')
        description = lines[0].strip()

        # Full content (cleaned)
        content = " ".join([line.strip() for line in lines if line.strip()])

        modules.append({
            "module_name": module_name,
            "description": description,
            "content": content
        })

    return modules

