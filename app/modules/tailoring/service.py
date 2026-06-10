from __future__ import annotations

from pathlib import Path
from typing import Any

STRICT_SYSTEM_PROMPT = (
    'You are an expert resume tailoring assistant. Rewrite candidate bullet points so they align with '
    'the job description, but do not hallucinate any skill or experience not present in the master resume.'
)


class TailoringError(RuntimeError):
    pass


async def generate_tailored_resume_pdf(master_resume: dict[str, Any], raw_jd: str, output_path: Path) -> Path:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ModuleNotFoundError as exc:
        raise TailoringError('reportlab is required for PDF generation') from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prompt = f"{STRICT_SYSTEM_PROMPT}\n\nMaster Resume:\n{master_resume}\n\nJob Description:\n{raw_jd}"

    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    pdf.drawString(72, 750, 'Tailored Resume Preview')
    pdf.drawString(72, 730, prompt[:2000])
    pdf.save()
    return output_path
