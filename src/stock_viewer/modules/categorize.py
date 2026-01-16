import json

def categorize_stocks(file_path):
    # Abrir e ler o arquivo JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    

    categories={}
    for stock in data:
        # agrego a categoria "*"
        data[stock]["category"]=list(set(data[stock].get("category", ["*"]))|set(["*"]))
        
        for category in data[stock]["category"]:
            categories[category]=categories.get(category,[])+[stock]
    
    return categories

# Exemplo de uso:
#file_path = 'stock.json'  # Substitua pelo caminho do seu arquivo JSON
#result = categorize_stocks(file_path)
#print(result)

