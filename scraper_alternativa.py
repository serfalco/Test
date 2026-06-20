import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# Búsqueda general en La Plata
URL = "https://www.alternativateatral.com/buscar.asp?objetivo=espectaculos&texto=la+plata"

def get_fechas_finde():
    hoy = datetime.now()
    # Calcular días hasta el próximo viernes (weekday 4)
    dias_para_viernes = 4 - hoy.weekday()
    if dias_para_viernes <= 0:
        dias_para_viernes += 7
        
    viernes = hoy + timedelta(days=dias_para_viernes)
    sabado = viernes + timedelta(days=1)
    domingo = viernes + timedelta(days=2)
    
    return [viernes.date(), sabado.date(), domingo.date()]

def scrape():
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error HTTP: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    espectaculos = []
    
    # Selectores orientativos. Alternativa Teatral requiere ajustar 
    # las clases dependiendo de si es la lista de búsqueda o la ficha.
    # Esta es la lógica base de extracción.
    resultados = soup.find_all('div', class_='resultados') # Ajustar clase real
    
    for item in resultados:
        titulo_tag = item.find('h2')
        titulo = titulo_tag.text.strip() if titulo_tag else "Sin título"
        
        sala_tag = item.find('a', href=lambda href: href and 'espacio' in href)
        sala = sala_tag.text.strip() if sala_tag else "Sin sala"
        
        # Alternativa suele poner las fechas en texto crudo dentro de párrafos o listas
        # Aquí capturamos el bloque de información para luego parsear
        info_fechas = item.find('div', class_='funciones') # Ajustar clase real
        fechas_texto = info_fechas.text.strip() if info_fechas else "Sin datos de fecha"
        
        # Para la prueba, guardamos el texto crudo. 
        # Luego se implementa regex para aislar "Viernes XX/XX - HH:MM"
        
        espectaculos.append({
            "obra": titulo,
            "sala": sala,
            "fechas_horarios_raw": fechas_texto
        })

    # Guardar resultados
    with open('cartelera_finde.json', 'w', encoding='utf-8') as f:
        json.dump(espectaculos, f, ensure_ascii=False, indent=4)
        
if __name__ == '__main__':
    scrape()
