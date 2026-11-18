# Proceso semanal automatizado — Universo en 1 Minuto

Esta guía la sigue Claude cada semana (tarea programada) para investigar, elegir y escribir los guiones. El dueño de la cuenta solo graba/edita/publica.

## Qué se produce cada semana (3 a 4 guiones, flexible)

**Base:** 4 videos = **1 hallazgo/descubrimiento + 3 curiosidades**. Si el dueño pide 3, se omite la curiosidad más floja.

| Día sugerido | Pilar | Origen |
|---|---|---|
| Lunes | 🔭 Hallazgo / descubrimiento de la semana (el más fuerte) | Noticias de los últimos 7 días |
| Miércoles | 🤯 Curiosidad (Escalas / Cotidiano) | Siguiente tema sin hacer de `lanzamiento.md` ("Próximos videos") o `cola.md` |
| Viernes | ❓ Curiosidad (¿Qué pasaría si…? / Mito) | Ídem |
| Sábado/Domingo | 🤯 Curiosidad o 📅 Lo que se viene (eventos del cielo de la semana próxima) | Ídem / EarthSky, in-the-sky.org |

**Flexibilidad (regla de oro):** no es estricto. Si la semana trae **varias novedades realmente buenas** (puntaje alto en el Paso 2), reemplazar curiosidades por hallazgos: hasta 2 o 3 hallazgos y 1 curiosidad. Si una noticia es excepcional (misión, descubrimiento histórico), proponerla como video urgente, marcado "SACAR YA" al tope del resumen. Si la semana está floja, quedarse con 1 hallazgo o ninguno y rellenar con curiosidades; nunca forzar una noticia mediocre. Las curiosidades se pueden adelantar y dejar de reserva en la cola.

Archivos: `contenido/video-NN-tema-corto.md` con NN = siguiente número libre (mirar los existentes). Mismo formato que `video-03-sol-pelota-futbol.md`: formato, duración 45–55 s, pilar, tabla de guion por tiempos, texto de publicación con hashtags, título para Shorts, **tabla "Datos verificados" con fuentes**, "Para no equivocarse en comentarios" y "Producción gratis". Voz rioplatense ("mirá", "imaginá", "seguinos").

## Paso 1 — Buscar noticias (últimos 7 días)

Buscar en la web (WebSearch, modo extended la primera vez y standard para verificar). Fuentes preferidas, en orden: NASA (science.nasa.gov, nasa.gov/news), ESA, ESO, Hubble/Webb (stsci, esawebb), JPL, Nature/Science/arXiv con nota de prensa, universidades; luego ScienceDaily, Space.com, Phys.org, Universe Today, EarthSky. Para eventos del cielo: EarthSky, timeanddate, in-the-sky.org.

## Paso 2 — Elegir (puntuar de 1 a 5 cada criterio)

1. **Gancho**: se entiende en 3 segundos, genera "¡¿qué?!" (récord, "primera vez", "no debería existir", mundo nuevo).
2. **Visual**: hay imagen/animación libre de NASA/ESA/ESO para mostrar.
3. **Explicable en 1 minuto** sin fórmulas.
4. **Confiable**: confirmado por paper revisado o comunicado oficial.
5. **Cercanía**: se puede comparar con algo cotidiano (Argentina, fútbol, ciudad, tiempo).

Elegir los 2 con mayor puntaje total. No repetir temas ya en `contenido/` ni en `contenido/cola.md`.

## Paso 3 — Verificar (obligatorio)

- Abrir la fuente original (comunicado o paper), no solo el resumen de un medio.
- Confirmar con al menos **2 fuentes independientes** las cifras clave. Anotarlas en "Datos verificados" con link.
- Si algo es **candidato / no confirmado / preliminar**, el guion lo dice ("posible", "los científicos creen"). Nunca afirmar de más.
- Descartar: blogs de baja calidad, titulares tipo "rompe la física", notas de un solo medio chico sin respaldo. Anotarlas en `cola.md` como descartadas con el motivo.
- Los cálculos propios (escalas, comparaciones) se muestran en la tabla y se rehacen dos veces.

## Paso 4 — Escribir los guiones

Gancho en los primeros 3 s con la cifra o la frase más fuerte. Cierre fijo: "¿Sabías esto? Seguinos para entender el universo en un minuto." Incluir créditos de imagen (NASA/ESA/ESO) en "Producción gratis".

## Paso 5 — Registrar y guardar

- Actualizar `contenido/cola.md`: video usado, fecha, fuente principal; hallazgos descartados; 3–5 candidatos "para después" por si falta material.
- Agregar al final de `contenido/CALENDARIO.md` la semana con título y día de cada video.
- `git add contenido && git commit` con mensaje en español, y `git push origin claude/contenido-astronomia`. Si el push falla, dejar el commit local y avisarlo.

## Resumen final de cada corrida (lo que lee el dueño)

Lista corta: los 4 videos con día, título y gancho; qué se descartó y por qué; cualquier dato que no se pudo confirmar y requiere ojo humano.
