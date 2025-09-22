import json

# Arquivos
arquivo_json = "assentos.json"
arquivo_coordenadas = "coordenadas.txt"
arquivo_novo = "assentos_atualizado.json"

# Lê assentos já existentes
with open(arquivo_json, "r", encoding="utf-8") as f:
    assentos = json.load(f)

# Extrai nomes já existentes
nomes_existentes = {a["fields"]["nome"] for a in assentos}

# Último PK usado
ultimo_pk = max(a["pk"] for a in assentos)

# Lê o arquivo de coordenadas
novos_assentos = []
with open(arquivo_coordenadas, "r", encoding="utf-8") as f:
    for linha in f:
        linha = linha.strip()
        if 'alt="ASSENTO' in linha:
            # Extrai nome
            inicio_nome = linha.find('alt="ASSENTO') + len('alt="ASSENTO')
            fim_nome = linha.find('"', inicio_nome)
            nome = linha[inicio_nome:fim_nome]

            if nome not in nomes_existentes:
                # Extrai coords
                inicio_coords = linha.find('coords="') + len('coords="')
                fim_coords = linha.find('"', inicio_coords)
                coords = linha[inicio_coords:fim_coords]

                novos_assentos.append({"nome": nome, "coords": coords, "ocupado": False})

# Adiciona os novos assentos com PKs corretos
for i, assento in enumerate(novos_assentos, start=ultimo_pk+1):
    registro = {
        "model": "ingressos.assento",
        "pk": i,
        "fields": assento
    }
    assentos.append(registro)

# Salva novo arquivo
with open(arquivo_novo, "w", encoding="utf-8") as f:
    json.dump(assentos, f, indent=2, ensure_ascii=False)

print(f"Arquivo atualizado com {len(assentos)} assentos salvo em {arquivo_novo}")
