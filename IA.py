from google import genai
from google.genai import types  
from pydantic import BaseModel
import json

# Estrutura dos valores que serão adquiridos
class AnaliseValores(BaseModel):
    valores_positivos: list[str]
    valores_negativos: list[str]

def analisar_documento_em_uma_chamada(caminho_pdf):
    # Inicializalização do cliente 
    client = genai.Client(api_key="") 
    
    # Envio dos arquivos ao cliente
    arquivo = client.files.upload(file=caminho_pdf) 
    
    # Prompt que é enviado ao Gemini
    objetivo = (
        "Analise o seguinte PDF e retire deles os valores. "
        "Classifique-os em Positivos se possuírem valores positivos ou Negativos caso possuam valores negativos."
    )
    
    # Chamada que envia o arquivo (teste.pdf), objetivo (separar os valores) e o formato JSON 
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[arquivo, objetivo],
        config=types.GenerateContentConfig(
            response_schema=AnaliseValores,
            response_mime_type="application/json",
            system_instruction="Seja preciso e extraia os valores textuais ou numéricos conforme solicitado."
        )
    )
    
    # Converte o JSON em Python para mais fácil visualização
    dados_estruturados = json.loads(response.text)
    return dados_estruturados

if __name__ == "__main__":
    # Local do arquivo PDF que será lido
    caminhopdf = r"C:\VSCode\GitHub\IA\leitor-de-documentos-\teste.pdf" 
    
    resultado = analisar_documento_em_uma_chamada(caminhopdf)
    
    # Exibe os resultados na tela de forma organizada
    print("\nVALORES POSITIVOS")
    for item in resultado["valores_positivos"]:
        print(f"+ {item}")
        
    print("\nVALORES NEGATIVOS")
    for item in resultado["valores_negativos"]:
        print(f"- {item}")