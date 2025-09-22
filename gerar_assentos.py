import json
import re

coordenadas_file = 'coordenadas.txt'  # todas as coordenadas
json_saida = 'assentos_completos.json'

# Lê todas as coordenadas
with open(coordenadas_file, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Regex para pegar nome e coords
pattern = r'<area [^>]*alt="([^"]+)"[^>]*coords="([^"]+)"'
matches = re.findall(pattern, conteudo)

assentos = []
pk = 1

for nome, coords in matches:
    assento = {
        "model": "ingressos.assento",
        "pk": pk,
        "fields": {
            "nome": nome,
            "coords": coords,
            "ocupado": False
        }
    }
    assentos.append(assento)
    pk += 1

# Salva o JSON completo
with open(json_saida, 'w', encoding='utf-8') as f:
    json.dump(assentos, f, indent=2, ensure_ascii=False)

print(f"{len(assentos)} assentos salvos em {json_saida}")
