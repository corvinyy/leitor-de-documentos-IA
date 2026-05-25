import spacy
import fitz
from spacy.matcher import Matcher

# Carrega o script
nlp = spacy.load("pt_core_news_sm")

def extrair_inteligente(caminho_pdf):
    # Extração do texto
    doc_pdf = fitz.open(caminho_pdf)
    texto_bruto = " ".join([pagina.get_text() for pagina in doc_pdf])
    
    # Verificação de espaços vazios no PDF
    texto_limpo = " ".join(texto_bruto.split())
    doc_ai = nlp(texto_limpo)

    matcher = Matcher(nlp.vocab)

    # Padrão utilizado pela IA para detectar as variáveis desejadas
    # Contém variáveis como se houve aumento ou diminuição, se há %, mês, etc
    padrao_metrica = [
        {"LOWER": {"IN": ["aumento", "queda", "total", "valor", "diminuição", "crescimento", "subiu"]}, "OP": "?"}, 
        {"LOWER": "de", "OP": "?"},                                          
        {"LIKE_NUM": True},                                                
        {"TEXT": "%", "OP": "?"},                                            
        {"LOWER": "em"},                                                     
        {"LOWER": {"IN": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
                          "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]}}
    ]

    matcher.add("METRICA_MENSAL", [padrao_metrica])
    matches = matcher(doc_ai)
    
    # Filtro de resultados, sem isso, vários resultados iguais/extremamente parecidos são adquiridos
    from spacy.util import filter_spans
    all_spans = [doc_ai[start:end] for match_id, start, end in matches]
    spans_filtrados = filter_spans(all_spans)
    
    # Listas onde valores são armazenados
    resultados = []
    valores = []
    valores_formatados = []

    for span in spans_filtrados:
        texto = span.text.lower()
        
        palavras_positivas = ["aumento","crescimento","subiu"]
        palavras_negativas = ["queda","diminuição"]
        
        sinal = ""
        
        # Verificação do sinal, palavras consideradas positivas tem um '+' adicionado e valores considerados negativos um '-'
        if any(p in texto for p in palavras_positivas):
            resultados.append(span.text)
            sinal = "+"
        elif any(p in texto for p in palavras_negativas):
            resultados.append(span.text)
            sinal = "-"

        for num in span:
            if num.like_num:
                if "," in num.text:
                    # Alteração de valores 'string' para 'integer'
                    # Para a criação de gráficos, os valores devem ser transformados para números reais
                    numero_arrumado = num.text.replace(".","").replace(",",".")
                    valor_formatado = f"{sinal}{numero_arrumado}%"
                    valores.append(float(numero_arrumado))
                    valores_formatados.append(valor_formatado)
                else:
                    valores.append(int(num.text))
                    valor_formatado = f"{sinal}{num.text}%"
                    valores_formatados.append(valor_formatado)
                    break

    return resultados, valores, valores_formatados

# Local do arquivo PDF que será lido
caminho = r"C:\VSCode\GitHub\IA\teste.pdf"
info, numeros, formatado = extrair_inteligente(caminho)

print(f"Dados encontrados: {info}")
print(f"Valores separados: {numeros}")
print(f"Valores formatados: {formatado}")
