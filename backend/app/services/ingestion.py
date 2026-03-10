from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class DataIngestionService:
    """Handles data collection from multiple sources."""
    
    async def ingest_gmail(self, credentials: Dict, date_range: tuple, keywords: List[str] = None) -> List[Dict]:
        """Ingest emails from Gmail API."""
        # Placeholder for Gmail API integration
        # In production, use google-api-python-client
        return []
    
    async def ingest_slack(self, token: str, channels: List[str], date_range: tuple) -> List[Dict]:
        """Ingest messages from Slack API."""
        # Placeholder for Slack API integration
        # In production, use slack-sdk
        return []
    
    async def ingest_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Ingest content from uploaded files."""
        content = ""
        source_metadata = {"file_type": file_type}
        
        if file_type == "pdf":
            content = self._extract_pdf_content(file_path)
        elif file_type in ["doc", "docx"]:
            content = self._extract_docx_content(file_path)
        elif file_type == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        return {
            "source_type": "file",
            "source_id": file_path,
            "content": content,
            "source_metadata": source_metadata,
            "timestamp": datetime.utcnow(),
        }
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error extracting DOCX: {str(e)}"
    
    async def ingest_meeting_transcript(self, transcript_data: Dict) -> Dict[str, Any]:
        """Ingest meeting transcript data."""
        return {
            "source_type": "meeting",
            "source_id": transcript_data.get("meeting_id", "unknown"),
            "content": transcript_data.get("transcript", ""),
            "source_metadata": {
                "meeting_title": transcript_data.get("title"),
                "participants": transcript_data.get("participants", []),
                "duration": transcript_data.get("duration"),
            },
            "timestamp": transcript_data.get("timestamp", datetime.utcnow()),
            "author": transcript_data.get("organizer"),
        }
