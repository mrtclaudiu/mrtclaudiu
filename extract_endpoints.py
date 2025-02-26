import os
import re

# Directorul unde ai documentația descărcată
DOCS_DIR = "/root/binance-spot-api-docs-master"

# Expresie regulată pentru a găsi endpoint-uri API
ENDPOINT_REGEX = re.compile(r'\b(GET|POST|PUT|DELETE)\s+(/api/v[0-9]+/[\w/-]+)')

# Lista în care vom stoca endpoint-urile găsite
endpoints = set()

# Parcurgem toate fișierele Markdown din documentație
for root, _, files in os.walk(DOCS_DIR):
    for file in files:
        if file.endswith(".md"):
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

                # Caută endpoint-urile API
                matches = ENDPOINT_REGEX.findall(content)
                for method, endpoint in matches:
                    endpoints.add(f"{method} {endpoint}")

# Salvează endpoint-urile într-un fișier
with open("endpoints.txt", "w") as f:
    for endpoint in sorted(endpoints):
        f.write(endpoint + "\n")

print(f"✅ Extracted {len(endpoints)} unique endpoints. Saved to endpoints.txt.")
