"""
Gemini AI Engine for BRD Platform
Uses Google Gemini API for requirement extraction and analysis
"""
import json
from typing import List, Dict, Optional
from google import genai
from app.core.config import settings
from app.core.logging import logger

class GeminiEngine:
    """Gemini AI engine for requirement extraction and analysis."""
    
    def __init__(self):
        """Initialize Gemini with API key from settings."""
        api_key = settings.GEMINI_API_KEY
        
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            self.enabled = False
            logger.warning("GEMINI_API_KEY not configured. AI features disabled.")
            return
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_name = "models/gemini-2.5-flash"
            self.enabled = True
            logger.info(f"Gemini AI engine initialized successfully with {self.model_name} model")
        except Exception as e:
            self.enabled = False
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def extract_requirements(self, text: str) -> List[Dict]:
        """
        Extract structured requirements from text using Gemini.
        
        Args:
            text: Raw text containing requirements
            
        Returns:
            List of extracted requirements with structure
        """
        if not self.enabled:
            logger.warning("Gemini not enabled, using fallback extraction")
            return self._fallback_extract(text)
        
        try:
            prompt = f"""Extract all business requirements from the following text.
Categorize each requirement into one of these types:
- functional: Features and functionality the system must provide
- non_functional: Performance, security, scalability requirements
- business_objective: Business goals and objectives
- assumption: Assumptions made about the project
- success_metric: Metrics to measure success
- timeline: Dates, deadlines, or schedule information
- risk: Potential risks or concerns

For each requirement, provide:
- content: The requirement text
- type: One of the categories above
- priority: critical, high, medium, or low
- confidence: A score from 0.0 to 1.0

Text to analyze:
{text}

Return ONLY a valid JSON array with this structure:
[
  {{
    "content": "requirement text",
    "type": "functional",
    "priority": "high",
    "confidence": 0.9
  }}
]

Do not include any markdown formatting or code blocks, just the JSON array."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result_text = response.text.strip()
            
            # Clean up response (remove markdown if present)
            if result_text.startswith('```'):
                # Remove code block markers
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else result_text
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            # Parse JSON
            requirements = json.loads(result_text)
            
            # Validate structure
            if not isinstance(requirements, list):
                logger.warning("Gemini returned non-list response, using fallback")
                return self._fallback_extract(text)
            
            logger.info(f"Gemini extracted {len(requirements)} requirements")
            return requirements
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.debug(f"Raw response: {result_text[:500]}")
            return self._fallback_extract(text)
        except Exception as e:
            logger.error(f"Gemini extraction error: {e}")
            return self._fallback_extract(text)
    
    def _fallback_extract(self, text: str) -> List[Dict]:
        """
        Fallback extraction using simple pattern matching.
        Used when Gemini is unavailable or fails.
        """
        requirements = []
        
        # Split by sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Determine type based on keywords
            if any(word in sentence_lower for word in ['must', 'shall', 'will', 'should', 'feature', 'function']):
                req_type = 'functional'
            elif any(word in sentence_lower for word in ['performance', 'security', 'scalability']):
                req_type = 'non_functional'
            elif any(word in sentence_lower for word in ['goal', 'objective', 'aim']):
                req_type = 'business_objective'
            elif any(word in sentence_lower for word in ['assume', 'assumption']):
                req_type = 'assumption'
            elif any(word in sentence_lower for word in ['metric', 'measure', 'kpi']):
                req_type = 'success_metric'
            elif any(word in sentence_lower for word in ['deadline', 'date', 'schedule', 'timeline']):
                req_type = 'timeline'
            elif any(word in sentence_lower for word in ['risk', 'concern', 'issue']):
                req_type = 'risk'
            else:
                req_type = 'functional'
            
            # Determine priority
            if any(word in sentence_lower for word in ['critical', 'urgent', 'must have']):
                priority = 'critical'
            elif any(word in sentence_lower for word in ['important', 'high priority']):
                priority = 'high'
            elif any(word in sentence_lower for word in ['nice to have', 'optional', 'low priority']):
                priority = 'low'
            else:
                priority = 'medium'
            
            requirements.append({
                'content': sentence,
                'type': req_type,
                'priority': priority,
                'confidence': 0.6
            })
        
        return requirements
    
    def generate_brd_summary(self, requirements: List[str]) -> Dict:
        """
        Generate BRD sections from requirements using Gemini.
        
        Args:
            requirements: List of requirement texts
            
        Returns:
            Dictionary with BRD sections
        """
        if not self.enabled:
            return self._fallback_brd(requirements)
        
        try:
            req_text = "\n".join([f"- {req}" for req in requirements[:50]])
            
            prompt = f"""Create a Business Requirements Document from these requirements:

{req_text}

Generate these sections in JSON format:
- executive_summary: 2-3 paragraph overview of the project
- functional_requirements: List of key functional requirements
- non_functional_requirements: List of quality attributes and constraints
- timeline: Estimated timeline and key milestones
- assumptions: List of assumptions made
- risks: Potential risks identified

Return ONLY valid JSON with this structure:
{{
  "executive_summary": "text",
  "functional_requirements": ["req1", "req2"],
  "non_functional_requirements": ["req1", "req2"],
  "timeline": "text",
  "assumptions": ["assumption1", "assumption2"],
  "risks": ["risk1", "risk2"]
}}

Do not include markdown formatting, just the JSON."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result_text = response.text.strip()
            
            # Clean up response
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else result_text
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            brd = json.loads(result_text)
            logger.info("Gemini generated BRD successfully")
            return brd
            
        except Exception as e:
            logger.error(f"Gemini BRD generation error: {e}")
            return self._fallback_brd(requirements)
    
    def _fallback_brd(self, requirements: List[str]) -> Dict:
        """Fallback BRD generation without AI."""
        return {
            'executive_summary': f'This document outlines the business requirements for the project based on {len(requirements)} identified requirements.',
            'functional_requirements': requirements[:10],
            'non_functional_requirements': [],
            'timeline': 'To be determined based on project scope and resources.',
            'assumptions': ['All stakeholders are available for requirements validation'],
            'risks': ['Requirements may change during development']
        }
    
    def detect_conflicts(self, req1: str, req2: str) -> Optional[str]:
        """
        Detect if two requirements conflict using Gemini.
        
        Args:
            req1: First requirement text
            req2: Second requirement text
            
        Returns:
            Conflict description if found, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""Analyze if these two requirements conflict or contradict each other:

Requirement 1: {req1}
Requirement 2: {req2}

If they conflict, explain why in 1-2 sentences.
If they don't conflict, respond with exactly: "No conflict detected"

Response:"""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result = response.text.strip()
            
            if "no conflict" in result.lower():
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini conflict detection error: {e}")
            return None
    
    async def classify_requirement(self, text: str) -> Dict:
        """
        Classify a single requirement using Gemini.
        
        Args:
            text: Requirement text to classify
            
        Returns:
            Dictionary with type, priority, confidence
        """
        if not self.enabled:
            return self._fallback_classify(text)
        
        try:
            prompt = f"""Classify this requirement:

"{text}"

Provide classification in JSON format:
{{
  "type": "functional|non_functional|business_objective|assumption|success_metric|timeline|risk",
  "priority": "critical|high|medium|low",
  "confidence": 0.0-1.0,
  "sentiment": "positive|neutral|negative"
}}

Return ONLY the JSON, no markdown."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result_text = response.text.strip()
            
            # Clean markdown
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else result_text
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            classification = json.loads(result_text)
            return classification
            
        except Exception as e:
            logger.error(f"Gemini classification error: {e}")
            return self._fallback_classify(text)
    
    def _fallback_classify(self, text: str) -> Dict:
        """Fallback classification without AI."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['must', 'shall', 'will']):
            req_type = 'functional'
        elif any(word in text_lower for word in ['performance', 'security']):
            req_type = 'non_functional'
        else:
            req_type = 'functional'
        
        if any(word in text_lower for word in ['critical', 'urgent']):
            priority = 'critical'
        elif any(word in text_lower for word in ['important', 'high']):
            priority = 'high'
        else:
            priority = 'medium'
        
        return {
            'type': req_type,
            'priority': priority,
            'confidence': 0.6,
            'sentiment': 'neutral'
        }
    
    async def rewrite_requirement(self, text: str, instruction: str) -> str:
        """
        Rewrite a requirement based on instruction using Gemini.
        
        Args:
            text: Original requirement text
            instruction: How to rewrite it
            
        Returns:
            Rewritten requirement text
        """
        if not self.enabled:
            return text
        
        try:
            prompt = f"""Rewrite this requirement according to the instruction:

Original: {text}
Instruction: {instruction}

Provide only the rewritten requirement, nothing else."""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini rewrite error: {e}")
            return text
    
    def detect_duplicates(self, requirements: List[Dict]) -> List[Dict]:
        """
        Detect duplicate requirements.
        
        Args:
            requirements: List of requirement dicts with id and content
            
        Returns:
            List of duplicate pairs
        """
        duplicates = []
        
        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements[i+1:], start=i+1):
                # Simple similarity check
                content1 = req1.get('content', '').lower()
                content2 = req2.get('content', '').lower()
                
                # Check word overlap
                words1 = set(content1.split())
                words2 = set(content2.split())
                
                if len(words1) > 0 and len(words2) > 0:
                    overlap = len(words1 & words2) / max(len(words1), len(words2))
                    
                    if overlap > 0.7:  # 70% similarity threshold
                        duplicates.append({
                            'req1_id': req1.get('id'),
                            'req2_id': req2.get('id'),
                            'similarity': overlap,
                            'reason': 'High content similarity detected'
                        })
        
        return duplicates

# Create singleton instance
gemini_engine = GeminiEngine()
