# Universo en 1 Minuto (@fisicacosmica)

Cuenta de Instagram Reels / YouTube Shorts de astronomía y física. Todo en español rioplatense ("sentís", "podés", "seguinos").

## Flujo
- Semana: 3–4 videos, base 1 hallazgo + 3 curiosidades, flexible. Proceso completo en `contenido/PROCESO.md`.
- Guiones en `contenido/`, specs en `produccion/specs/`, render con `python produccion/build_video.py <spec>` (ffmpeg + edge-tts + imágenes NASA). Ver `produccion/README.md`.
- Una tarea programada ("universo-semana-contenido", domingos 18:47) hace todo el ciclo y manda los videos al dueño.

## Reglas
- Solo imágenes reales de NASA/ESA con `nasa_id` verificado; nunca IA generativa de video ni ilustraciones inventadas.
- Voz por defecto `es-ES-AlvaroNeural`. Videos ≤ 58 s, 1080×1920.
- Datos siempre con 2 fuentes; lo no confirmado va como "posible"/"candidato".
- Publicación manual por ahora (VidIQ no deja conectar `@fisicacosmica`). No publicar nada sin OK del dueño.
