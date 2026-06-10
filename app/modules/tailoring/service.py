from __future__ import annotations

from pathlib import Path
from typing import Any

STRICT_SYSTEM_PROMPT = (
    'You are an expert resume tailoring assistant. Rewrite candidate bullet points so they align with '
    'the job description, but do not hallucinate any skill or experience not present in the master resume.'
)
MAX_PROMPT_LENGTH = 2_000
MAX_JD_LENGTH = 4_000
MAX_RESUME_LENGTH = 4_000


class TailoringError(RuntimeError):
    pass


async def generate_tailored_resume_pdf(master_resume: dict[str, Any], raw_jd: str, output_path: Path) -> Path:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ModuleNotFoundError as exc:
        raise TailoringError('reportlab is required for PDF generation') from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sanitized_resume = str(master_resume)[:MAX_RESUME_LENGTH]
    sanitized_jd = ' '.join(raw_jd.split())[:MAX_JD_LENGTH]
    prompt = (
        f"{STRICT_SYSTEM_PROMPT}\n\nMaster Resume:\n{sanitized_resume}\n\nJob Description:\n{sanitized_jd}"
    )[:MAX_PROMPT_LENGTH]

    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    pdf.drawString(72, 750, 'Tailored Resume Preview')
    pdf.drawString(72, 730, prompt)
    pdf.save()
    return output_path
