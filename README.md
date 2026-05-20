# EvidencIA Backend — Guía de Despliegue
## Developed by Miranda · EC0301 CONOCER

---

## PASO 1 — Obtener API Key de Anthropic

1. Ir a: https://platform.anthropic.com
2. Crear cuenta o iniciar sesión con Gmail
3. Ir a "API Keys" → "Create Key"
4. Copiar la clave (empieza con `sk-ant-...`)
5. **Guardarla en un lugar seguro** — solo se muestra una vez

Costo estimado: ~$0.003 USD por evaluación

---

## PASO 2 — Crear cuenta en GitHub (si no tiene)

1. Ir a: https://github.com
2. Registrarse con Gmail
3. Crear repositorio nuevo llamado `evidencia-backend`
4. Marcar como **Privado**

---

## PASO 3 — Subir el código a GitHub

Opción A (fácil — desde el navegador):
1. Entrar al repositorio recién creado
2. Clic en "uploading an existing file"
3. Arrastrar los archivos: `main.py`, `requirements.txt`, `Procfile`
4. Clic en "Commit changes"

---

## PASO 4 — Crear cuenta en Render.com

1. Ir a: https://render.com
2. Clic en "Get Started for Free"
3. Registrarse con Gmail (misma cuenta)
4. **No necesita tarjeta de crédito**

---

## PASO 5 — Crear el Web Service en Render

1. En el dashboard de Render → "New +" → "Web Service"
2. Conectar con GitHub → seleccionar `evidencia-backend`
3. Configurar:
   - **Name:** `evidencia-api`
   - **Region:** Oregon (US West)
   - **Branch:** main
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Clic en "Create Web Service"

---

## PASO 6 — Agregar la API Key como variable de entorno

1. En el servicio creado → tab "Environment"
2. Clic en "Add Environment Variable"
3. Key: `ANTHROPIC_API_KEY`
4. Value: pegar la clave `sk-ant-...`
5. Clic en "Save Changes"
6. El servicio se reinicia automáticamente

---

## PASO 7 — Obtener la URL del backend

Render asignará una URL como:
`https://evidencia-api.onrender.com`

Copiar esa URL — se necesita en el siguiente paso.

---

## PASO 8 — Conectar EvidencIA con el backend

En el archivo `EvidencIA_v2.html`, buscar la línea:

```javascript
const BACKEND_URL = ""; // Pegar aquí la URL de Render
```

Y reemplazar con:

```javascript
const BACKEND_URL = "https://evidencia-api.onrender.com";
```

---

## VERIFICAR QUE TODO FUNCIONA

Abrir en el navegador:
`https://evidencia-api.onrender.com`

Debe mostrar:
```json
{
  "sistema": "EvidencIA API",
  "version": "2.0.0",
  "desarrollado_por": "Miranda",
  "status": "activo"
}
```

---

## NOTAS IMPORTANTES

- El plan gratuito de Render "duerme" después de 15 min sin uso
  → La primera petición tarda ~30 seg en "despertar"
  → Para uso continuo, el plan Starter ($7/mes) mantiene el servicio activo

- La API Key de Anthropic se cobra por uso:
  ~$0.003 USD por evaluación completa (48 reactivos)
  26 candidatos × 3 versiones = ~$0.23 USD total del curso

- **No compartir la API Key** — guardarla solo en Render

---

## ARCHIVOS DEL PROYECTO

```
evidencia-backend/
├── main.py          ← Servidor principal FastAPI
├── requirements.txt ← Dependencias Python
├── Procfile         ← Instrucciones para Render
└── README.md        ← Esta guía
```

---

Developed by Miranda · EvidencIA v2.0 · EC0301 CONOCER
