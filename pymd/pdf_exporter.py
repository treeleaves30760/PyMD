"""
PDF export functionality for PyMD
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from .logger import get_logger

logger = get_logger("pdf_exporter")


class PDFExporter:
    """Handles PDF export functionality"""

    def __init__(self):
        self.available_engines = self._detect_engines()

    def _detect_engines(self) -> list:
        """Detect available PDF rendering engines"""
        engines = []

        # Check for wkhtmltopdf
        try:
            subprocess.run(
                ["wkhtmltopdf", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            engines.append("wkhtmltopdf")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check for weasyprint (Python library)
        try:
            import weasyprint

            engines.append("weasyprint")
        except ImportError:
            pass

        # Check for pandoc
        try:
            subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            engines.append("pandoc")
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if engines:
            logger.info(f"Available PDF engines: {', '.join(engines)}")
        else:
            logger.warning("No PDF export engines found. Install wkhtmltopdf, weasyprint, or pandoc.")

        return engines

    def export_html_to_pdf(
        self,
        html_content: str,
        output_path: str,
        engine: Optional[str] = None,
    ) -> bool:
        """
        Export HTML content to PDF

        Args:
            html_content: HTML string to convert
            output_path: Path for output PDF file
            engine: Specific engine to use (auto-detect if None)

        Returns:
            True if successful, False otherwise
        """
        if not self.available_engines:
            logger.error("No PDF export engines available. Please install one:")
            logger.error("  - pip install weasyprint")
            logger.error("  - Or install wkhtmltopdf from https://wkhtmltopdf.org/")
            logger.error("  - Or install pandoc from https://pandoc.org/")
            return False

        # Choose engine
        if engine and engine in self.available_engines:
            selected_engine = engine
        else:
            # Prefer weasyprint for better CSS support
            if "weasyprint" in self.available_engines:
                selected_engine = "weasyprint"
            elif "wkhtmltopdf" in self.available_engines:
                selected_engine = "wkhtmltopdf"
            else:
                selected_engine = self.available_engines[0]

        logger.info(f"Exporting PDF using {selected_engine}")

        try:
            if selected_engine == "weasyprint":
                return self._export_with_weasyprint(html_content, output_path)
            elif selected_engine == "wkhtmltopdf":
                return self._export_with_wkhtmltopdf(html_content, output_path)
            elif selected_engine == "pandoc":
                return self._export_with_pandoc(html_content, output_path)
            else:
                logger.error(f"Unknown engine: {selected_engine}")
                return False
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return False

    def _export_with_weasyprint(self, html_content: str, output_path: str) -> bool:
        """Export using WeasyPrint (Python library)"""
        try:
            from weasyprint import HTML

            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"PDF exported successfully: {output_path}")
            return True
        except Exception as e:
            logger.error(f"WeasyPrint export failed: {e}")
            return False

    def _export_with_wkhtmltopdf(self, html_content: str, output_path: str) -> bool:
        """Export using wkhtmltopdf command-line tool"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False
        ) as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [
                    "wkhtmltopdf",
                    "--enable-local-file-access",
                    "--quiet",
                    tmp_path,
                    output_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info(f"PDF exported successfully: {output_path}")
                return True
            else:
                logger.error(f"wkhtmltopdf failed: {result.stderr}")
                return False
        finally:
            os.unlink(tmp_path)

    def _export_with_pandoc(self, html_content: str, output_path: str) -> bool:
        """Export using pandoc"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False
        ) as tmp:
            tmp.write(html_content)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [
                    "pandoc",
                    tmp_path,
                    "-o",
                    output_path,
                    "--pdf-engine=xelatex",  # Requires LaTeX
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                logger.info(f"PDF exported successfully: {output_path}")
                return True
            else:
                logger.error(f"pandoc failed: {result.stderr}")
                return False
        finally:
            os.unlink(tmp_path)

    def get_install_instructions(self) -> str:
        """Get installation instructions for PDF engines"""
        if self.available_engines:
            return f"Available PDF engines: {', '.join(self.available_engines)}"

        instructions = """
PDF Export is not available. Please install one of the following:

1. WeasyPrint (Recommended - Python package):
   pip install weasyprint

2. wkhtmltopdf (Command-line tool):
   - Ubuntu/Debian: sudo apt-get install wkhtmltopdf
   - macOS: brew install wkhtmltopdf
   - Windows: Download from https://wkhtmltopdf.org/downloads.html

3. Pandoc (with LaTeX):
   - Ubuntu/Debian: sudo apt-get install pandoc texlive-xetex
   - macOS: brew install pandoc basictex
   - Windows: Download from https://pandoc.org/installing.html
"""
        return instructions
