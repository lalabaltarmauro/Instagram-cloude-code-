#!/usr/bin/env python
"""Arma un Reel/Short vertical 1080x1920 a partir de un spec JSON.

Uso:  python produccion/build_video.py produccion/specs/video-01.json

Gratis: imágenes NASA (images-api.nasa.gov), voz es-AR con edge-tts, edición con ffmpeg.
Salida: produccion/salida/<id>.mp4 (+ <id>-contactos.png para revisar las imágenes).
Spec: ver produccion/README.md
"""
import asyncio, json, os, subprocess, sys, shutil, textwrap, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "cache"
OUT = ROOT / "salida"
FONT_SRC = Path("C:/Windows/Fonts/arialbd.ttf")
W, H, FPS = 1080, 1920, 30


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise RuntimeError(f"{cmd[0]} falló:\n{r.stderr[-1500:]}")
    return r.stdout


def nasa_image(spec):
    """Devuelve ruta a una imagen NASA (por nasa_id o por búsqueda). Cachea."""
    CACHE.mkdir(exist_ok=True)
    nid = spec.get("nasa_id")
    if not nid:
        q = urllib.parse.quote(spec["query"])
        url = f"https://images-api.nasa.gov/search?q={q}&media_type=image&page_size=5"
        with urllib.request.urlopen(url, timeout=60) as r:
            items = json.load(r)["collection"]["items"]
        if not items:
            raise RuntimeError(f"Sin resultados NASA para: {spec['query']}")
        nid = items[int(spec.get("pick", 0))]["data"][0]["nasa_id"]
    dest = CACHE / f"{nid}.jpg"
    if not dest.exists():
        for size in ("large", "medium", "orig"):
            try:
                u = f"https://images-assets.nasa.gov/image/{nid}/{nid}~{size}.jpg"
                urllib.request.urlretrieve(u, dest)
                break
            except Exception:
                continue
        else:
            raise RuntimeError(f"No pude bajar {nid}")
    return dest


def prep_background(img_path, focus_x, focus_y, out_png):
    """Recorte 9:16 'cover' con foco, algo más grande que la pantalla (para zoom)."""
    im = Image.open(img_path).convert("RGB")
    tw, th = int(W * 1.25), int(H * 1.25)
    scale = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.LANCZOS)
    cx = int(im.width * focus_x); cy = int(im.height * focus_y)
    left = min(max(cx - tw // 2, 0), im.width - tw)
    top = min(max(cy - th // 2, 0), im.height - th)
    im.crop((left, top, left + tw, top + th)).save(out_png)


async def tts(text, voice, rate, out_mp3):
    import edge_tts
    for intento in range(5):  # el servicio a veces no devuelve audio: reintentar
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(str(out_mp3))
            return
        except edge_tts.exceptions.NoAudioReceived:
            await asyncio.sleep(2 * (intento + 1))
    raise RuntimeError(f"Sin audio TTS tras 5 intentos: {text[:50]}")


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", str(path)]).strip())


def wrap(text, width):
    return "\n".join(textwrap.wrap(text, width))


def build(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    vid = spec["id"]
    work = ROOT / "tmp" / vid
    shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    OUT.mkdir(exist_ok=True)
    shutil.copy(FONT_SRC, work / "f.ttf")
    voice = spec.get("voz", "es-AR-ElenaNeural")
    rate = spec.get("velocidad", "+8%")
    clips = []
    thumbs = []
    for i, sc in enumerate(spec["escenas"], 1):
        n = f"{i:02d}"
        mp3 = work / f"{n}.mp3"
        asyncio.run(tts(sc["voz"], voice, rate, mp3))
        dur = duration(mp3) + 0.35
        src = nasa_image(sc["imagen"])
        bg = work / f"{n}.png"
        prep_background(src, sc["imagen"].get("foco_x", 0.5), sc["imagen"].get("foco_y", 0.5), bg)
        thumbs.append(Image.open(bg).resize((216, 384)))
        # textos
        open(work / f"{n}_big.txt", "w", encoding="utf-8", newline="").write(wrap(sc.get("texto", ""), 14))
        open(work / f"{n}_cap.txt", "w", encoding="utf-8", newline="").write(wrap(sc["voz"], 30))
        frames = int(dur * FPS)
        zin = 0.00018 if i % 2 else -0.00018  # alterna zoom in/out
        z0 = 1.0 if zin > 0 else 1.18
        vf = (f"zoompan=z='{z0}+({zin})*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
              "format=yuv420p,"
              "drawbox=x=0:y=ih*0.60:w=iw:h=ih*0.34:color=black@0.45:t=fill,"
              f"drawtext=fontfile=f.ttf:expansion=none:textfile={n}_cap.txt:fontcolor=white:fontsize=46:line_spacing=4:x=(w-text_w)/2:y=h*0.64:borderw=3:bordercolor=black")
        if sc.get("texto"):
            vf += (f",drawtext=fontfile=f.ttf:expansion=none:textfile={n}_big.txt:fontcolor=#FFD34D:fontsize=92:line_spacing=2:"
                   "x=(w-text_w)/2:y=h*0.10:borderw=6:bordercolor=black")
        clip = work / f"clip{n}.mp4"
        run(["ffmpeg", "-y", "-loop", "1", "-i", f"{n}.png", "-i", f"{n}.mp3",
             "-vf", vf, "-t", f"{dur:.2f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "160k", "-af", "apad", "-shortest", f"clip{n}.mp4"], cwd=work)
        clips.append(clip)
        print(f"escena {n}: {dur:.1f}s")
    # concatenar
    (work / "lista.txt").write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
    final = OUT / f"{vid}.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "lista.txt", "-c:v", "libx264", "-preset", "medium",
         "-crf", "20", "-c:a", "aac", "-movflags", "+faststart", str(final)], cwd=work)
    total = duration(final)
    run(["ffmpeg","-y","-loglevel","error","-ss","1.2","-i",str(final),"-frames:v","1",str(OUT / f"{vid}-portada.png")])
    # hoja de contactos
    sheet = Image.new("RGB", (216 * len(thumbs), 384))
    for k, t in enumerate(thumbs):
        sheet.paste(t, (216 * k, 0))
    sheet.save(OUT / f"{vid}-contactos.png")
    print(f"\nListo: {final}  ({total:.1f}s)")
    if total > 59:
        print("AVISO: Dura más de 59 s: acortar el guion (límite Shorts/Reels).")
    return final


if __name__ == "__main__":
    build(sys.argv[1])
