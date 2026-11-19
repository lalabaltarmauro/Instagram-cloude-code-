# Producción automática de videos (gratis)

`python produccion/build_video.py produccion/specs/video-NN.json` → `produccion/salida/<id>.mp4` (1080×1920, ≤ 59 s).

Usa: imágenes NASA (images-api.nasa.gov, uso libre), voz es-AR (edge-tts: `es-ES-AlvaroNeural` (la elegida) / `es-AR-TomasNeural`), ffmpeg.
Requisitos: `ffmpeg` en el PATH y `pip install edge-tts pillow`.

## Spec JSON
```json
{ "id": "video-NN-tema", "voz": "es-ES-AlvaroNeural", "velocidad": "+10%",
  "escenas": [
    {"voz": "Texto que se dice (también sale como subtítulo).",
     "texto": "Texto grande amarillo arriba",
     "imagen": {"nasa_id": "PIA25628", "foco_x": 0.5, "foco_y": 0.5}}
  ] }
```
`imagen` admite `nasa_id` (recomendado, verificado) o `query` (+ `pick` = posición del resultado). Cada guion `.md` lleva su spec en `specs/`.
Reglas: total ≤ 58 s (ajustar texto o `velocidad`), 6–8 escenas, la imagen debe ser real y coincidir con lo que se dice (nunca ilustraciones inventadas).
