"""
TechPulse - FastAPI Server & Vercel Python Entrypoint
Serves static AMP Web Stories distribution, JSON APIs, and portal pages.
Satisfies Vercel Python runtime entrypoint requirements.
"""

import sys
import json
import mimetypes
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles

import config

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

app = FastAPI(
    title=f"{config.SITE_NAME} Portal API",
    description=config.SITE_DESCRIPTION,
    version="1.0.0"
)

# Ensure dist and static directories exist
config.DIST_DIR.mkdir(parents=True, exist_ok=True)
static_path = config.DIST_DIR / "static"
if not static_path.exists() and config.STATIC_DIR.exists():
    static_path = config.STATIC_DIR

if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


def serve_file_or_404(path: Path, media_type: str = "text/html") -> Response:
    """Reads and returns a static file or raises a 404 error."""
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Page not found: {path.name}")
    content = path.read_bytes()
    return Response(
        content=content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=0, must-revalidate"}
    )


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_home():
    """Serves the main TechPulse Cyberpunk Portal homepage."""
    index_file = config.DIST_DIR / "index.html"
    if not index_file.exists():
        from fetch_and_generate import run_pipeline
        run_pipeline()
    return serve_file_or_404(index_file)


@app.api_route("/stories/{slug}/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/stories/{slug}", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_story(slug: str):
    """Serves an individual 100% compliant Google AMP Web Story."""
    story_file = config.DIST_DIR / "stories" / slug / "index.html"
    return serve_file_or_404(story_file)


@app.api_route("/about/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/about", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_about():
    return serve_file_or_404(config.DIST_DIR / "about" / "index.html")


@app.api_route("/privacy/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/privacy", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_privacy():
    return serve_file_or_404(config.DIST_DIR / "privacy" / "index.html")


@app.api_route("/terms/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/terms", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_terms():
    return serve_file_or_404(config.DIST_DIR / "terms" / "index.html")


@app.api_route("/contact/", methods=["GET", "HEAD"], response_class=HTMLResponse)
@app.api_route("/contact", methods=["GET", "HEAD"], response_class=HTMLResponse)
def get_contact():
    return serve_file_or_404(config.DIST_DIR / "contact" / "index.html")


@app.api_route("/sitemap.xml", methods=["GET", "HEAD"])
def get_sitemap():
    return serve_file_or_404(config.DIST_DIR / "sitemap.xml", media_type="application/xml; charset=utf-8")


@app.api_route("/robots.txt", methods=["GET", "HEAD"])
def get_robots():
    return serve_file_or_404(config.DIST_DIR / "robots.txt", media_type="text/plain; charset=utf-8")


@app.api_route("/stories.json", methods=["GET", "HEAD"])
def get_stories_json():
    return serve_file_or_404(config.DIST_DIR / "stories.json", media_type="application/json; charset=utf-8")


@app.get("/api/stories")
def api_stories():
    """Returns active stories in machine-readable JSON format."""
    manifest_file = config.DIST_DIR / "stories.json"
    if not manifest_file.exists():
        return JSONResponse(content={"stories": [], "count": 0})
    with open(manifest_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content={"stories": data, "count": len(data)})


if __name__ == "__main__":
    import uvicorn
    print(f"[*] Starting {config.SITE_NAME} server on http://127.0.0.1:8000 ...")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
