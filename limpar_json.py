import json
import shutil
from pathlib import Path

# Caminho para o JSON
json_path = Path("ingressos/fixtures/assentos_completos.json")

# Cria backup
backup_path = json_path.with_suffix(".backup.json")
shutil.copy(json_path, backup_path)
print(f"Backup criado em {backup_path}")

# Lê o JSON
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Remove o campo "ocupado"
for item in data:
    if "fields" in item and "ocupado" in item["fields"]:
        del item["fields"]["ocupado"]

# Salva de volta
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Arquivo atualizado sem o campo 'ocupado'.")
