import re
from typing import List, Dict, Tuple
from app.models import RequirementType, SentimentType

class InformationExtractor:
    """Extracts structured information from raw text using NLP and pattern matching."""
    
    def __init__(self):
        self.requirement_patterns = {
            RequirementType.FUNCTIONAL: [
                r"(?:system|application|platform|user)\s+(?:shall|must|should|will)\s+(.+?)(?:\.|$)",
                r"(?:the|a)\s+(?:system|user|application)\s+(?:can|could|may)\s+(.+?)(?:\.|$)",
                r"(?:requirement|feature):\s*(.+?)(?:\.|$)",
            ],
            RequirementType.NON_FUNCTIONAL: [
                r"(?:performance|security|scalability|reliability|availability):\s*(.+?)(?:\.|$)",
                r"(?:must|should)\s+(?:be|have|support)\s+(?:secure|fast|scalable|reliable|available)(.+?)(?:\.|$)",
            ],
            RequirementType.BUSINESS_OBJECTIVE: [
                r"(?:goal|objective|aim):\s*(.+?)(?:\.|$)",
                r"(?:we|business)\s+(?:want|need|require)\s+to\s+(.+?)(?:\.|$)",
                r"(?:increase|decrease|improve|reduce|enhance)\s+(.+?)(?:\.|$)",
            ],
            RequirementType.ASSUMPTION: [
                r"(?:assume|assuming|assumption):\s*(.+?)(?:\.|$)",
                r"(?:we|i)\s+assume\s+(?:that\s+)?(.+?)(?:\.|$)",
            ],
            RequirementType.SUCCESS_METRIC: [
                r"(?:metric|kpi|measure):\s*(.+?)(?:\.|$)",
                r"(?:success|measured)\s+(?:by|through|via)\s+(.+?)(?:\.|$)",
                r"(?:\d+%|\d+\s+percent)\s+(.+?)(?:\.|$)",
            ],
        }
        
        self.sentiment_keywords = {
            SentimentType.POSITIVE: ["great", "excellent", "good", "happy", "agree", "perfect", "love", "excited"],
            SentimentType.NEGATIVE: ["concern", "worried", "issue", "problem", "disagree", "bad", "poor", "risk"],
        }
    
    def extract_requirements(self, text: str, project_keywords: List[str] = None) -> List[Dict]:
        """Extract requirements from text."""
        if not self._is_relevant(text, project_keywords):
            return []
        
        extracted = []
        for req_type, patterns in self.requirement_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    content = match.group(1) if match.lastindex else match.group(0)
                    extracted.append({
                        "type": req_type,
                        "content": content.strip(),
                        "confidence": 0.7,
                        "sentiment": self._analyze_sentiment(content)
                    })
        
        return extracted
    
    def _is_relevant(self, text: str, keywords: List[str] = None) -> bool:
        """Check if text is relevant to project context."""
        if not keywords:
            return True
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)
    
    def _analyze_sentiment(self, text: str) -> SentimentType:
        """Analyze sentiment of text."""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.sentiment_keywords[SentimentType.POSITIVE] if word in text_lower)
        negative_count = sum(1 for word in self.sentiment_keywords[SentimentType.NEGATIVE] if word in text_lower)
        
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE
        return SentimentType.NEUTRAL
    
    def detect_conflicts(self, items: List[Dict]) -> List[Tuple[int, int, str]]:
        """Detect conflicting requirements."""
        conflicts = []
        negation_words = ["not", "no", "never", "cannot", "won't", "shouldn't"]
        
        for i, item1 in enumerate(items):
            for j, item2 in enumerate(items[i+1:], start=i+1):
                if self._are_conflicting(item1["content"], item2["content"], negation_words):
                    conflicts.append((i, j, "Potential contradiction detected"))
        
        return conflicts
    
    def _are_conflicting(self, text1: str, text2: str, negation_words: List[str]) -> bool:
        """Check if two texts are conflicting."""
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Simple heuristic: check for negation patterns
        text1_has_negation = any(word in text1_lower for word in negation_words)
        text2_has_negation = any(word in text2_lower for word in negation_words)
        
        # Check for similar content with opposite negation
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        
        return overlap > 0.5 and text1_has_negation != text2_has_negation
