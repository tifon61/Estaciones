# Bitácora del Campo — Estación FCAGLP/LPO

Página que muestra las condiciones actuales e históricas de la estación
meteorológica, leyendo los datos directamente desde Nextcloud (sin depender
de la página de la facultad).

## Cómo funciona

```
Nextcloud (cloud.fcaglp.unlp.edu.ar)
        │  (GitHub Actions descarga el .txt cada 15 min, vía WebDAV)
        ▼
   fetch_data.py  →  docs/data.json
        │
        ▼
   docs/index.html  (la página que ves en el navegador, leyendo data.json)
```

El usuario y la contraseña de Nextcloud **nunca quedan visibles** en el
código: se guardan como "Secrets" de GitHub, y solo los usa el robot que
corre en los servidores de GitHub (GitHub Actions), no la página pública.

## Pasos para dejarlo funcionando

### 1. Crear el repositorio

En GitHub, creá un repositorio nuevo (público o privado, cualquiera sirve
para GitHub Pages). Subí todos estos archivos tal cual están, manteniendo
la estructura de carpetas.

### 2. Cargar los "Secrets"

En el repositorio: **Settings → Secrets and variables → Actions → New
repository secret**. Cargá estos tres:

| Nombre           | Valor                                                                 |
|-------------------|------------------------------------------------------------------------|
| `NEXTCLOUD_USER`  | `meteo` (o el usuario que corresponda)                                 |
| `NEXTCLOUD_PASS`  | la contraseña de esa cuenta                                             |
| `WEBDAV_URL`      | `https://cloud.fcaglp.unlp.edu.ar/remote.php/dav/files/meteo/Estaciones/LPO/WLink%20Campo/EMACampo/downld08.txt` |

**Importante:** confirmá que `WEBDAV_URL` sea exactamente correcta.
Podés probarla vos mismo antes: pegala en el navegador, iniciá sesión
con el usuario/contraseña, y verificá que descargue el archivo de texto
(no una página de error 404).

### 3. Activar GitHub Pages

**Settings → Pages** → en "Source" elegí la rama `main` (o la que uses)
y la carpeta **`/docs`**. Guardá. GitHub te va a dar una URL tipo
`https://tu-usuario.github.io/tu-repo/`.

### 4. Probar el workflow manualmente

Andá a la pestaña **Actions** del repositorio → elegí "Actualizar datos
de la estación" → botón **"Run workflow"** (esto lo corre ya, sin
esperar los 15 minutos). Revisá que termine en verde (✅). Si falla,
el log te va a decir por qué (usuario/contraseña incorrectos, URL mal
armada, etc.).

### 5. Ver la página

Entrá a la URL de GitHub Pages. Al principio puede tardar 1-2 minutos en
propagarse después de la primera corrida exitosa del workflow.

## Ajustes posibles

- **Frecuencia de actualización**: cambiá el `cron` en
  `.github/workflows/update-data.yml` (por defecto cada 15 minutos).
  Ojo con no poner algo demasiado frecuente (menos de 5 min) para no
  sobrecargar el servidor de Nextcloud.
- **Cantidad de historial mostrado**: en `fetch_data.py`, la constante
  `MAX_HISTORY_RECORDS` controla cuántos registros se guardan en
  `data.json`. En `docs/index.html`, la línea `.slice(-288)` controla
  cuántos puntos recientes se grafican (podés subir/bajar ese número).
- **Escala del dial de temperatura**: en `index.html`, dentro de
  `drawDialTicks()` y `setNeedle()`, las variables `min`/`max` (-10°C a
  40°C) definen el rango del instrumento. Ajustalas si hace mucho
  frío o calor en la zona.

## Archivos del proyecto

- `parse_davis.py` — interpreta el formato de ancho fijo de WeatherLink.
- `fetch_data.py` — descarga el archivo y genera `docs/data.json`.
- `docs/index.html` — la página pública (dashboard institucional con
  Tailwind: tarjetas de condiciones actuales, filtros Hoy/Semana/Mes con
  rango de fechas personalizado, y 5 gráficos históricos).
- `.github/workflows/update-data.yml` — automatización (GitHub Actions).
- `requirements.txt` — dependencias de Python.
