from typing import Dict, Any, Optional
import re

class DocumentEditor:
    """Handles natural language editing of BRD documents."""
    
    def parse_edit_request(self, instruction: str, section: Optional[str] = None) -> Dict[str, Any]:
        """Parse natural language edit instruction."""
        instruction_lower = instruction.lower()
        
        # Detect operation type
        operation = self._detect_operation(instruction_lower)
        
        # Detect target section if not specified
        if not section:
            section = self._detect_section(instruction_lower)
        
        # Extract content to add/modify
        content = self._extract_content(instruction)
        
        return {
            "operation": operation,
            "section": section,
            "content": content,
            "original_instruction": instruction
        }
    
    def _detect_operation(self, instruction: str) -> str:
        """Detect the type of edit operation."""
        if any(word in instruction for word in ["add", "include", "insert"]):
            return "add"
        elif any(word in instruction for word in ["remove", "delete", "exclude"]):
            return "remove"
        elif any(word in instruction for word in ["change", "modify", "update", "replace"]):
            return "modify"
        elif any(word in instruction for word in ["rewrite", "rephrase"]):
            return "rewrite"
        return "modify"
    
    def _detect_section(self, instruction: str) -> Optional[str]:
        """Detect which section the edit targets."""
        section_keywords = {
            "executive_summary": ["summary", "executive", "overview"],
            "business_objectives": ["objective", "goal", "business goal"],
            "stakeholder_analysis": ["stakeholder", "stakeholders"],
            "functional_requirements": ["functional", "feature", "functionality"],
            "non_functional_requirements": ["non-functional", "performance", "security"],
            "assumptions": ["assumption", "assumptions"],
            "success_metrics": ["metric", "metrics", "kpi", "measure"],
            "timeline": ["timeline", "schedule", "deadline"],
        }
        
        for section, keywords in section_keywords.items():
            if any(keyword in instruction for keyword in keywords):
                return section
        
        return None
    
    def _extract_content(self, instruction: str) -> str:
        """Extract the actual content from instruction."""
        # Look for quoted content
        quoted = re.findall(r'"([^"]*)"', instruction)
        if quoted:
            return quoted[0]
        
        # Look for content after "to" or ":"
        patterns = [
            r'(?:add|include|change to|modify to|update to):\s*(.+)',
            r'(?:add|include|change to|modify to|update to)\s+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return instruction
    
    def apply_edit(self, document: Dict[str, Any], edit_request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply edit to document based on parsed request."""
        operation = edit_request["operation"]
        section = edit_request["section"]
        content = edit_request["content"]
        
        if not section:
            # Apply to entire document
            return self._apply_global_edit(document, operation, content)
        
        if section not in document["sections"]:
            return document
        
        if operation == "add":
            return self._add_to_section(document, section, content)
        elif operation == "remove":
            return self._remove_from_section(document, section, content)
        elif operation == "modify":
            return self._modify_section(document, section, content)
        elif operation == "rewrite":
            return self._rewrite_section(document, section, content)
        
        return document
    
    def _add_to_section(self, document: Dict, section: str, content: str) -> Dict:
        """Add content to a section."""
        section_data = document["sections"][section]
        
        if isinstance(section_data, dict) and "items" in section_data:
            new_item = {
                "id": f"REQ-MANUAL-{len(section_data['items']) + 1}",
                "content": content,
                "manually_added": True
            }
            section_data["items"].append(new_item)
        elif isinstance(section_data, dict) and "content" in section_data:
            section_data["content"] += f" {content}"
        
        return document
    
    def _remove_from_section(self, document: Dict, section: str, content: str) -> Dict:
        """Remove content from a section."""
        section_data = document["sections"][section]
        
        if isinstance(section_data, dict) and "items" in section_data:
            section_data["items"] = [
                item for item in section_data["items"]
                if content.lower() not in item["content"].lower()
            ]
        
        return document
    
    def _modify_section(self, document: Dict, section: str, content: str) -> Dict:
        """Modify section content."""
        section_data = document["sections"][section]
        
        if isinstance(section_data, dict) and "content" in section_data:
            section_data["content"] = content
        
        return document
    
    def _rewrite_section(self, document: Dict, section: str, content: str) -> Dict:
        """Completely rewrite a section."""
        document["sections"][section] = {"content": content, "manually_edited": True}
        return document
    
    def _apply_global_edit(self, document: Dict, operation: str, content: str) -> Dict:
        """Apply edit across entire document."""
        # Simple implementation: add note to executive summary
        if "executive_summary" in document["sections"]:
            summary = document["sections"]["executive_summary"]
            if isinstance(summary, dict) and "content" in summary:
                summary["content"] += f" Note: {content}"
        
        return document
