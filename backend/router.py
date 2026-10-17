import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse

router = APIRouter()

TEMPLATES_DIR = Path("~/AbrarCloud/templates")

@router.get("/health")
def healthcheck():
    return {"status": "ok", "service": "root-integration-bridge"}

@router.get("", response_class=HTMLResponse)
def list_templates_ui():
    """Returns a simple, clean UI showing all registered templates in the system."""
    template_folders = []
    if TEMPLATES_DIR.exists():
        template_folders = [d.name for d in TEMPLATES_DIR.iterdir() if d.is_dir()]
    
    links = "".join([
        f'<li><a href="/backend/router/templates/{folder}" style="color: #00f2fe; text-decoration: none; font-size: 1.1rem; font-weight: 500;">{folder}</a></li>'
        for folder in sorted(template_folders)
    ])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Abrar Cloud - Templates Index</title>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
      <style>
        body {{
          background: #cbdbe6;
          font-family: 'Outfit', sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          margin: 0;
        }}
        .card {{
          background-color: #121418;
          width: 90%;
          max-width: 500px;
          border-radius: 20px;
          border: 1.5px solid rgba(0, 242, 254, 0.5);
          box-shadow: 0 0 25px rgba(0, 242, 254, 0.25);
          padding: 40px;
          color: white;
        }}
        h1 {{
          text-align: center;
          text-transform: uppercase;
          letter-spacing: 0.15em;
          margin-bottom: 30px;
          font-size: 1.75rem;
          color: #ffffff;
        }}
        ul {{
          list-style: none;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 15px;
        }}
        li {{
          background: #1f232b;
          padding: 12px 20px;
          border-radius: 50px;
          text-align: center;
          border: 1px solid transparent;
          transition: all 0.3s ease;
        }}
        li:hover {{
          border-color: #00f2fe;
          box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
          transform: translateY(-2px);
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>Abrar Cloud Templates</h1>
        <ul>
          {links if links else '<li>No templates configured yet.</li>'}
        </ul>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.get("/templates/{template_name}", response_class=HTMLResponse)
def serve_template(template_name: str):
    """
    Reads the index.html from templates/[template_name] and returns it.
    """
    template_path = TEMPLATES_DIR / template_name / "index.html"
    
    if not template_path.exists() or not template_path.is_file():
        # Fallback template if index.html is missing
        fallback_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>Abrar Cloud - {template_name}</title>
          <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">
          <style>
            body {{ background: #cbdbe6; font-family: 'Outfit', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background-color: #121418; border-radius: 20px; border: 1.5px solid rgba(0, 242, 254, 0.5); padding: 40px; color: white; text-align: center; max-width: 450px; }}
            h1 {{ color: #00f2fe; margin-bottom: 15px; }}
            p {{ color: #8a8f9d; line-height: 1.6; }}
            .btn {{ display: inline-block; background: #0d2c54; color: white; padding: 12px 24px; border-radius: 50px; text-decoration: none; margin-top: 20px; font-weight: 600; }}
          </style>
        </head>
        <body>
          <div class="card">
            <h1>{template_name.replace('-', ' ').title()} Page</h1>
            <p>The layout for this workspace module is currently being finalized. Check back soon for the full interactive interface.</p>
            <a href="/backend/router" class="btn">Back to Templates</a>
          </div>
        </body>
        </html>
        """
        return HTMLResponse(content=fallback_html, status_code=200)
        
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading template: {str(e)}"
        )
