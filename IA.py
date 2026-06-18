from google import genai
from google.genai import types  
from pydantic import BaseModel
import json
import os
import matplotlib.pyplot as plt
from fpdf import FPDF

# Lógica da IA--------------------------------------------------------------------------------------------------------------------------------------------------

# Estrutura dos valores que serão adquiridos
class AnaliseValores(BaseModel):
    rotulo: str
    valor: float
    tipo: str

class AnaliseCronologica(BaseModel):
    historico: list[AnaliseValores]
    resumo: str
    estilo: str

def analise(caminho_pdf):
    # Inicializalização do cliente 
    client = genai.Client(api_key="") 
    
    # Envio dos arquivos ao cliente
    arquivo = client.files.upload(file=caminho_pdf) 
    
    # Prompt que é enviado ao Gemini
    objetivo = (
        "Analise o documento e extraia os dados principais de variação ou distribuição."
        "Para cada dado encontrado, preencha a estrutura:"
        "- 'rotulo': Identifique o nome da categoria, produto ou mês correspondente (ex: 'Abril', 'Filmes', 'Roupas')."
        "- 'valor': Identifique o valor numérico ou percentual. Se o texto indicar uma 'queda' ou prejuízo, salve como NEGATIVO. Se indicar 'aumento' ou ganho, POSITIVO."
        "- 'tipo': Descreva brevemente o tipo do dado."
        "No campo 'resumo', faça uma síntese dos dados analisados."
        "No campo 'estilo', defina se será melhor um gráfico de 'pizza' ou 'barras':"
        "- Escolha 'barras' se os dados mostrarem uma evolução no tempo (meses/anos) ou contiverem valores negativos."
        "- Escolha 'pizza' se os dados representarem a divisão/distribuição de categorias de um todo (composição) e forem todos positivos."
    )
    
    # Chamada que envia o arquivo (teste.pdf) e objetivo (separar os valores)
    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = [arquivo, objetivo],
        config = types.GenerateContentConfig(
            response_schema = AnaliseCronologica,
            response_mime_type = "application/json",
            system_instruction = "Seja preciso e extraia os valores textuais ou numéricos conforme solicitado."
        )
    )
    
    # Converte o JSON em Python para mais fácil visualização
    return response.parsed

# Funções para geração de gráficos--------------------------------------------------------------------------------------------------------------------------------------------------

def grafico_barras(dados, caminho_saida="Grafico_Final.png"):
    historico = dados.historico
    
    meses = [ponto.rotulo.capitalize() for ponto in historico]
    valores = [ponto.valor for ponto in historico]
    
    plt.figure(figsize=(8,5), layout="constrained")
    
    cores = ["limegreen" if val >= 0 else "indianred" for val in valores]
    
    barras = plt.bar(meses, valores, linestyle="-", color=cores, edgecolor="black", label="Variação %")
    
    plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    
    for barra in barras:
        val = barra.get_height()
        
        pos_y = val + (max(valores) * 0.02 if val >= 0 else min(valores) * 0.02)
        
        plt.text(barra.get_x() + barra.get_width() / 2, pos_y, f"{val}%", ha="center", va="bottom" if val >= 0 else "top", fontsize=9, fontweight="bold")
            
    #plt.scatter(meses[i], val, color=cor, zorder=5) 

    plt.title('Evolução das Variações Percentuais no Tempo', fontsize=12, fontweight='bold')
    plt.xlabel('Meses', fontsize=10)
    plt.ylabel('Variação (%)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)

    # Define os limites do eixo Y para dar folga para os textos
    margem = (max(valores) - min(valores)) * 0.2 if valores else 15
    plt.ylim(min(valores) - margem, max(valores) + margem)
    
    plt.savefig(caminho_saida)
    plt.show()
    plt.close()
    return caminho_saida

def grafico_pizza(dados, caminho_saida="Grafico_Pizza.png"):
    historico = dados.historico
    
    nomes = [ponto.rotulo.capitalize() for ponto in historico]
    valores = [ponto.valor for ponto in historico]

    valores_pos = [abs(v) for v in valores]

    plt.figure(figsize=(6,6))

    plt.pie(valores_pos, labels=nomes, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'black', 'linewidth': 2}, colors=plt.cm.Set1.colors)

    plt.title("Distribuição Proporcional por Período", fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(caminho_saida)
    plt.show()
    plt.close()
    return caminho_saida

# Criação de PDFs--------------------------------------------------------------------------------------------------------------------------------------------------
class RelatorioPDF(FPDF):
    def header(self):
        self.set_fill_color(10, 45, 80)

        self.rect(0, 0, 210, 25, "F")
        self.set_text_color(255, 255, 255)

        self.set_font("Arial", "B", 22)
        self.cell(0, 15, "RELATÓRIO DE PERFORMANCE", ln=True, align="C")

        self.ln(5)

    def footer(self):
        self.set_y(-15)

        self.set_font("Arial", "", 8)
        self.set_text_color(100,100,100)

        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")
        
def gerar_pdf(dados, grafico_path):
    pdf = RelatorioPDF()
    pdf.add_page()

    pdf.set_text_color(0,0,0)

    # Título da análise
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Resumo Executivo", ln=True)

    pdf.ln(3)

    # Resumo gerado pelo Gemini
    pdf.set_font("Arial", "", 11)

    pdf.multi_cell(0,6,dados.resumo)

    pdf.ln(5)

    # Inserção do gráfico
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Indicadores", ln=True)

    pdf.image(grafico_path, x=30, w=150)

    pdf.ln(100)

    altura_cabecalho = 10
    altura_linha = 10

    altura_tabela = altura_cabecalho + (len(dados.historico) * altura_linha)

    espaco_restante = pdf.h - pdf.get_y() - pdf.b_margin

    if altura_tabela > espaco_restante:
        pdf.add_page()

    # Tabela de dados
    pdf.set_font("Arial", "B", 12)

    if dados.estilo == "barras":
        pdf.cell(70, 10, "Rotulo", 1)
        pdf.cell(50, 10, "Valor", 1)
        pdf.cell(70, 10, "Tipo", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 11)

        for item in dados.historico:
            pdf.cell(70, 10, item.rotulo, 1)
            pdf.cell(50, 10, f"{str(item.valor)}%", 1)
            pdf.cell(70, 10, item.tipo, 1)

            pdf.ln()

    else:
        pdf.output("Relatorio_Final.pdf")

    print("PDF criado com sucesso!")   
    
# Método inicial--------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Local do arquivo PDF que será lido
    caminhopdf = r"C:\VSCode\GitHub\IA\leitor-de-documentos-ia\teste_pizza.pdf" 
    
    resultado = analise(caminhopdf)
    
    estilo_escolhido = resultado.estilo.lower()
    print(estilo_escolhido)
    
    if "pizza" in estilo_escolhido:
        grafico = grafico_pizza(resultado)
        
    else:
        grafico = grafico_barras(resultado)
        
    gerar_pdf(resultado, grafico)