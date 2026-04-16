import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

app = FastAPI()

def generate_aac_stream(station: str):
    # Radiko の HLS を streamlink で取得
    streamlink_cmd = [
        "streamlink",
        f"https://radiko.jp/live/{station}",
        "best",
        "-O"
    ]

    # AAC に変換して出力（MASS が確実に再生できる形式）
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", "pipe:0",
        "-c:a", "aac",
        "-b:a", "64k",
        "-f", "adts",
        "pipe:1"
    ]

    try:
        p1 = subprocess.Popen(
            streamlink_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        p2 = subprocess.Popen(
            ffmpeg_cmd,
            stdin=p1.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        p1.stdout.close()

        while True:
            data = p2.stdout.read(4096)
            if not data:
                break
            yield data

    finally:
        for p in [p1, p2]:
            try:
                p.kill()
            except:
                pass


@app.get("/stream/{station}")
def stream_station(station: str):
    try:
        generator = generate_aac_stream(station)
        return StreamingResponse(generator, media_type="audio/aac")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
