from google import genai
from google.genai import types  
from pydantic import BaseModel
import json

def plan_goal():
    plan_prompt = "Analise o seguinte texto e retire deles os valores. Classifique-os em Positivos se possuírem valores positivos ou Negativos caso possuam valores negativos"
    plans = callmodel(plan_prompt, list[PlanSteps])
    plans = json.loads(plans)
    steps = [ plan['step_name'].strip() for plan in plans if plan['step_name'].strip()]
    return steps
    
class PlanSteps(BaseModel):
    step_name: str
    
def callmodel(prompt, schema):
    response = chat.send_message(prompt, config=types.GenerateContentConfig(response_schema=schema, 
                                                                 response_mime_type="application/json", 
                                                                 system_instruction="Answer within 30 words"))
    
    return response.text

def run_agent():
    steps = plan_goal()
    for step in steps:
        print(step)
    print("\nPasso completo!")
    
if __name__ == "__main__":
    client = genai.Client(api_key="") # Insira sua chave da API aqui
    
    # Informações para o uso da IA (modelo, obejtivo, caminho do documento)
    caminhopdf = r"C:\VSCode\GitHub\IA\teste.pdf" 
    arquivo = client.files.upload(file=caminhopdf) 
    model = "gemini-2.5-flash"
    chat = client.chats.create(model=model)
    objetivo = "Analise o seguinte texto e retire deles os valores. Classifique-os em Positivos se possuírem valores positivos ou Negativos caso possuam valores negativos"
    print(f"Objetivo: {objetivo}")
    
    # Envio da mensagem a IA
    chat.send_message([arquivo, objetivo])
    run_agent()
