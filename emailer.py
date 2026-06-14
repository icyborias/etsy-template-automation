import os
import json
import smtplib
from email.message import EmailMessage
from typing import List, Optional

from config import BRIEFS_DIR


def build_html(scout_json_path: str, brief_paths: List[str]) -> str:
    # Build a clean, mobile-friendly HTML digest
    scout_name = os.path.basename(scout_json_path)
    try:
        with open(scout_json_path, "r", encoding="utf-8") as f:
            scout = json.load(f)
    except Exception:
        scout = None

    css = """
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; color:#111; padding:16px }
    h1 { font-size:20px; margin-bottom:8px }
    .niche { margin-top:12px }
    .idea { margin-left:14px }
    a.brief { color:#0b63d6; text-decoration:none }
    .meta { color:#666; font-size:13px }
    """

    parts = [f"<html><head><meta charset=\"utf-8\"><title>Etsy Template Briefing</title><style>{css}</style></head><body>"]
    parts.append(f"<h1>Etsy Template Briefing — {scout_name}</h1>")

    if scout and isinstance(scout, dict):
        for n in scout.get("niches", []):
            niche_key = n.get("niche")
            parts.append(f"<div class=\"niche\"><strong>{niche_key}</strong>")
            parts.append("<div class=\"idea\"><ul>")
            for r in n.get("results", []):
                parts.append(f"<li><span class=\"meta\">op={r.get('opportunity')} </span>{r.get('keyword')}</li>")
            parts.append("</ul></div></div>")
    else:
        parts.append("<p>No scout JSON available.</p>")

    parts.append("<h2>Briefs</h2><ul>")
    for b in brief_paths:
        display = os.path.basename(b)
        path = f"file://{os.path.abspath(b)}"
        parts.append(f"<li><a class=\"brief\" href=\"{path}\">{display}</a></li>")
    parts.append("</ul>")
    parts.append("</body></html>")
    return "\n".join(parts)


def save_digest(html: str, out_path: Optional[str] = None) -> str:
    if out_path is None:
        import time
        timestamp = int(time.time() * 1000) % 1000000  # Use millisecond timestamp
        out_path = os.path.join(BRIEFS_DIR, f"digest-{timestamp}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def send_email(smtp_host: str, smtp_port: int, user: str, password: str, to: str, subject: str, html: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    msg.set_content("This is an HTML email")
    msg.add_alternative(html, subtype="html")
    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        s.login(user, password)
        s.send_message(msg)


if __name__ == "__main__":
    print("emailer module")
