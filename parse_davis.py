"""
Parser para archivos downldXX.txt exportados por WeatherLink (Davis).
Formato: columnas de ancho fijo separadas por espacios múltiples.

Columnas esperadas (en orden), a partir de la línea de datos:
0  Date          (dd/mm/aa)
1  Time          (h:mm)
2  TempOut       (°C)
3  HiTemp
4  LowTemp
5  OutHum        (%)
6  DewPt
7  WindSpeed     (km/h)
8  WindDir       (texto: N, NNE, etc. o '---')
9  WindRun
10 HiSpeed
11 HiDir
12 WindChill
13 HeatIndex
14 THWIndex
15 Bar           (presión, hPa)
16 Rain
17 RainRate
18 HeatD-D
19 CoolD-D
20 InTemp
21 InHum
22 InDew
23 InHeat
24+  (columnas extra variables según config: Wind Samp, ISS Recept, Arc Int, etc.)
"""
import re

# Índices de las columnas que nos interesan para el dashboard.
FIELD_INDEXES = {
    "date": 0,
    "time": 1,
    "temp_out": 2,
    "out_hum": 5,
    "wind_speed": 7,
    "wind_dir": 8,
    "bar": 15,
    "rain": 16,
    "in_temp": 20,
}

# Una línea de datos empieza con fecha dd/mm/aa
DATA_LINE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{2}\s")


def _to_float(value):
    """Convierte a float; si no se puede (p.ej. '---'), devuelve None."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def parse_wlk_txt(raw_text):
    """
    Recibe el contenido completo del archivo .txt y devuelve una lista de
    dicts, uno por cada registro de datos, en el orden en que aparecen
    en el archivo (más viejo -> más nuevo).
    """
    records = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not DATA_LINE_RE.match(line):
            continue  # es encabezado, separador, o línea vacía

        parts = line.split()
        if len(parts) < 21:
            # línea rota/incompleta, la salteamos en vez de romper todo
            continue

        try:
            record = {
                "date": parts[FIELD_INDEXES["date"]],
                "time": parts[FIELD_INDEXES["time"]],
                "temp_out": _to_float(parts[FIELD_INDEXES["temp_out"]]),
                "out_hum": _to_float(parts[FIELD_INDEXES["out_hum"]]),
                "wind_speed": _to_float(parts[FIELD_INDEXES["wind_speed"]]),
                "wind_dir": parts[FIELD_INDEXES["wind_dir"]],
                "bar": _to_float(parts[FIELD_INDEXES["bar"]]),
                "rain": _to_float(parts[FIELD_INDEXES["rain"]]),
                "in_temp": _to_float(parts[FIELD_INDEXES["in_temp"]]),
            }
        except IndexError:
            continue

        records.append(record)

    return records


if __name__ == "__main__":
    # Prueba rápida con el archivo de muestra
    with open("sample.txt", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    result = parse_wlk_txt(content)
    print(f"Registros encontrados: {len(result)}")
    for r in result:
        print(r)
