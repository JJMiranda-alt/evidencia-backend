"""
EvidencIA — Backend FastAPI
Sistema de Gestión de Evaluaciones EC0301 CONOCER
Developed by Miranda
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import anthropic
import docx
import io
import os
import json
from datetime import datetime

# ══════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════
app = FastAPI(
    title="EvidencIA API",
    description="Sistema de Gestión de Evaluaciones CONOCER EC0301 — Developed by Miranda",
    version="2.0.0"
)

# CORS — permite que EvidencIA (HTML) llame al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente Anthropic — usa la API key del entorno
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ══════════════════════════════════════════════
# PROMPT DEL SISTEMA PARA EVALUACIÓN EC0301
# ══════════════════════════════════════════════
PROMPT_EVALUADOR = """Eres un evaluador experto del CONOCER especializado en el estándar EC0301 
"Diseño de cursos de formación del capital humano de manera presencial grupal".

Tu tarea es evaluar una Carta Descriptiva (Elemento 1) usando los 48 reactivos del IEC EC0301.

REACTIVOS A EVALUAR (con sus pesos):

P1 — Presentación (16 reactivos × 0.25 pts):
1.1 Formato digital (.docx o .pdf)
2.2 Nombre del curso/sesión registrado
3.3 Nombre del instructor
4.4 Fecha y horario registrados y congruentes (horario debe sumar 180 min)
5.5 Perfil del participante descrito
6.6 Número de participantes especificado
7.7 Objetivo general y objetivos específicos presentes
8.8 4 momentos didácticos con tiempos que sumen exactamente 180 min
9.9 Contenido temático por etapa
10.10 Técnicas instruccionales diferenciadas de técnicas grupales (col6≠col7)
11.11 3 técnicas grupales: rompehielo(Encuadre), energizante(Desarrollo), cierre grupal(Cierre) en columna correcta
12.12 Actividades del instructor y participante descritas
13.13 Estrategias evaluativas (diagnóstica, formativa, sumativa)
14.14 Materiales/recursos por etapa
15.15 Tiempos acumulados = 180 min exactos
16.16 Sin errores ortográficos relevantes

P2 — Objetivo General (4 reactivos × 4.16 pts):
17.1 Sujeto identificable
18.2 Conducta observable
19.3 Condición de desempeño
20.4 Criterio cuantificable (% mínimo o número de aciertos concreto)

P3 — Objetivos Específicos (6 reactivos × 4.16 pts):
21.1 Sujeto en todos los objetivos por etapa
22.2 Conducta observable en todos
23.3 Condición en todos
24.4 Criterio cuantificable en todos los objetivos específicos
25.5 Objetivos congruentes con contenido temático
26.6 Objetivos congruentes con perfil del participante

P4 — Contenido Temático (3 reactivos × 0.58 pts):
27.1 Congruente con propósito del curso
28.2 Alineado a objetivos específicos
29.3 Secuencia progresiva de aprendizaje

P5 — Técnicas Instruccionales (3 reactivos × 0.58 pts):
30.1 Pertinentes a los objetivos
31.2 Adecuadas para el perfil
32.3 Pertinentes para el número de participantes

P6 — Técnicas Grupales (3 reactivos × 0.58 pts):
33.1 Congruentes con etapa y propósito
34.2 Adecuadas para el perfil
35.3 Pertinentes para el número de participantes

P7 — Actividades de Aprendizaje (4 reactivos × 0.58 pts):
36.1 Diferenciadas y secuenciadas por etapa
37.2 Congruentes con el contenido
38.3 Acordes al perfil
39.4 Con descripción clara y tiempos

P8 — Evaluación (5 reactivos, 4 × 0.58 pts + 1 × 4.16 pts):
40.1 Evaluaciones alineadas a cada momento didáctico (0.58)
41.2 Criterios e instrumentos definidos (0.58)
42.3 3 momentos evaluativos presentes (0.58)
43.4 Instrumentos especificados por etapa (0.58)
44.5 Evidencias sumativas con características mínimas y criterio de aceptación (4.16)

P9 — Recursos y Materiales (3 reactivos × 0.58 pts):
45.1 Corresponden a las actividades
46.2 Adecuados para el perfil
47.3 Pertinentes para el número de participantes

AHV — Secuencia Lógica (1 reactivo, 0 pts, solo observación):
48.1 Temas en secuencia progresiva

INSTRUCCIONES:
- Lee la carta descriptiva proporcionada
- Evalúa cada reactivo como SI o NO con base en el IEC
- Para 24.4: SI solo si TODOS los objetivos específicos por etapa tienen criterio cuantificable (% o número)
- Para 11.11: SI solo si hay rompehielo en Encuadre, energizante en Desarrollo Y cierre grupal en Cierre, en la columna de técnicas grupales (NO instruccionales)
- Para 8.8 y 15.15: verificar que los tiempos sumen exactamente 180 min
- Para 10.10: verificar que la columna de grupales y la de instruccionales tengan contenido DIFERENTE

Responde ÚNICAMENTE con JSON válido con esta estructura exacta:
{
  "candidato": "nombre del instructor encontrado en la carta",
  "curso": "nombre del curso/sesión",
  "fecha": "fecha y horario encontrados",
  "pts_total": 00.00,
  "pct": 00.0,
  "reactivos": {
    "1.1": {"resultado": "SI", "obs": "observación breve"},
    "2.2": {"resultado": "SI", "obs": "..."},
    ... (todos los 48 reactivos)
  },
  "pendientes": ["descripción corta de cada reactivo NO"],
  "retroalimentacion": "texto de retroalimentación en español, 3-5 párrafos, mencionando fortalezas y correcciones específicas",
  "dictamen": "COMPETENTE" o "AÚN NO COMPETENTE"
}"""


# ══════════════════════════════════════════════
# PESOS DE REACTIVOS
# ══════════════════════════════════════════════
PESOS = {
    "1.1":0.25,"2.2":0.25,"3.3":0.25,"4.4":0.25,"5.5":0.25,"6.6":0.25,
    "7.7":0.25,"8.8":0.25,"9.9":0.25,"10.10":0.25,"11.11":0.25,"12.12":0.25,
    "13.13":0.25,"14.14":0.25,"15.15":0.25,"16.16":0.25,
    "17.1":4.16,"18.2":4.16,"19.3":4.16,"20.4":4.16,
    "21.1":4.16,"22.2":4.16,"23.3":4.16,"24.4":4.16,"25.5":4.16,"26.6":4.16,
    "27.1":0.58,"28.2":0.58,"29.3":0.58,
    "30.1":0.58,"31.2":0.58,"32.3":0.58,
    "33.1":0.58,"34.2":0.58,"35.3":0.58,
    "36.1":0.58,"37.2":0.58,"38.3":0.58,"39.4":0.58,
    "40.1":0.58,"41.2":0.58,"42.3":0.58,"43.4":0.58,"44.5":4.16,
    "45.1":0.58,"46.2":0.58,"47.3":0.58,
    "48.1":0,
}


# ══════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════
def extraer_texto_docx(file_bytes: bytes) -> str:
    """Extrae texto completo de un archivo .docx"""
    doc = docx.Document(io.BytesIO(file_bytes))
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    # Extraer también texto de tablas (las cartas descriptivas son tablas)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                texto = cell.text.strip()
                if texto and texto not in parrafos:
                    parrafos.append(texto)
    
    return "\n".join(parrafos)


def calcular_pts(reactivos: dict) -> float:
    """Calcula el puntaje total de E1 a partir del diccionario de reactivos"""
    total = 0.0
    for cod, data in reactivos.items():
        if data.get("resultado") == "SI" and cod != "48.1":
            total += PESOS.get(cod, 0)
    return round(total, 2)


# ══════════════════════════════════════════════
# RUTAS
# ══════════════════════════════════════════════

@app.get("/")
async def root():
    return {
        "sistema": "EvidencIA API",
        "version": "2.0.0",
        "desarrollado_por": "Miranda",
        "estandar": "EC0301 CONOCER",
        "status": "activo"
    }


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.post("/evaluar")
async def evaluar_carta(
    archivo: UploadFile = File(...),
    candidato_id: str = Form(default=""),
    candidato_nombre: str = Form(default=""),
):
    """
    Recibe un archivo .docx con la carta descriptiva,
    lo envía a Claude para evaluación y devuelve el resultado completo.
    """

    # Validar tipo de archivo
    if not archivo.filename.endswith(('.docx', '.pdf')):
        raise HTTPException(400, "Solo se aceptan archivos .docx o .pdf")

    # Leer archivo
    contenido = await archivo.read()
    if len(contenido) > 10 * 1024 * 1024:  # 10MB límite
        raise HTTPException(400, "Archivo demasiado grande (máximo 10MB)")

    # Extraer texto
    try:
        if archivo.filename.endswith('.docx'):
            texto_carta = extraer_texto_docx(contenido)
        else:
            raise HTTPException(400, "PDF no soportado aún — por favor convierte a .docx")
    except Exception as e:
        raise HTTPException(422, f"Error al leer el archivo: {str(e)}")

    if len(texto_carta.strip()) < 100:
        raise HTTPException(422, "El archivo parece estar vacío o no contiene texto")

    # Llamar a Claude
    try:
        mensaje = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=PROMPT_EVALUADOR,
            messages=[
                {
                    "role": "user",
                    "content": f"""Evalúa la siguiente carta descriptiva para el EC0301.
Candidato declarado: {candidato_nombre or 'No especificado'}

TEXTO DE LA CARTA DESCRIPTIVA:
{texto_carta}

Responde SOLO con el JSON de evaluación, sin texto adicional."""
                }
            ]
        )

        # Parsear respuesta JSON
        respuesta_texto = mensaje.content[0].text.strip()

        # Limpiar posibles backticks de markdown
        if respuesta_texto.startswith("```"):
            respuesta_texto = respuesta_texto.split("```")[1]
            if respuesta_texto.startswith("json"):
                respuesta_texto = respuesta_texto[4:]
        if respuesta_texto.endswith("```"):
            respuesta_texto = respuesta_texto[:-3]

        resultado = json.loads(respuesta_texto.strip())

        # Recalcular pts para mayor precisión
        if "reactivos" in resultado:
            resultado["pts_total"] = calcular_pts(resultado["reactivos"])
            resultado["pct"] = round(resultado["pts_total"] / 61.03 * 100, 1)
            resultado["dictamen"] = "COMPETENTE" if resultado["pts_total"] >= 58.0 else "AÚN NO COMPETENTE"

        # Agregar metadata
        resultado["candidato_id"] = candidato_id
        resultado["fecha_evaluacion"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        resultado["archivo"] = archivo.filename
        resultado["modelo"] = "claude-sonnet-4-20250514"
        resultado["evaluador"] = "Dr. José Juan Miranda Torres"

        return JSONResponse(content=resultado)

    except json.JSONDecodeError as e:
        raise HTTPException(500, f"Error al parsear respuesta de IA: {str(e)}")
    except anthropic.AuthenticationError:
        raise HTTPException(401, "API Key de Anthropic inválida — verifica la variable ANTHROPIC_API_KEY")
    except anthropic.RateLimitError:
        raise HTTPException(429, "Límite de requests alcanzado — espera un momento")
    except Exception as e:
        raise HTTPException(500, f"Error en la evaluación: {str(e)}")


@app.post("/evaluar-texto")
async def evaluar_texto_directo(payload: dict):
    """
    Alternativa: recibe el texto directamente (para pruebas desde la plataforma).
    """
    texto = payload.get("texto", "")
    candidato_nombre = payload.get("candidato_nombre", "")

    if len(texto.strip()) < 50:
        raise HTTPException(400, "Texto demasiado corto")

    try:
        mensaje = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=PROMPT_EVALUADOR,
            messages=[{
                "role": "user",
                "content": f"Candidato: {candidato_nombre}\n\nCARTA DESCRIPTIVA:\n{texto}\n\nResponde SOLO con el JSON."
            }]
        )

        respuesta_texto = mensaje.content[0].text.strip()
        if "```" in respuesta_texto:
            respuesta_texto = respuesta_texto.split("```")[1]
            if respuesta_texto.startswith("json"):
                respuesta_texto = respuesta_texto[4:]

        resultado = json.loads(respuesta_texto.strip())
        if "reactivos" in resultado:
            resultado["pts_total"] = calcular_pts(resultado["reactivos"])
            resultado["pct"] = round(resultado["pts_total"] / 61.03 * 100, 1)
        resultado["fecha_evaluacion"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        resultado["evaluador"] = "Dr. José Juan Miranda Torres"

        return JSONResponse(content=resultado)

    except Exception as e:
        raise HTTPException(500, str(e))
