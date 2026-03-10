from typing import List, Dict, Any, Union
from datetime import datetime
from app.models import RequirementType, ExtractedItem, ExtractedRequirement, DataSource

class DocumentGenerator:
    """Generates structured BRD documents from extracted information."""
    
    def generate_brd(self, project_name: str, items: List[Union[ExtractedItem, ExtractedRequirement]], 
                     sources: List[DataSource], conflicts: List = None) -> Dict[str, Any]:
        """Generate a complete BRD document."""
        
        items_by_type = self._group_by_type(items)
        
        brd = {
            "title": f"Business Requirements Document - {project_name}",
            "generated_at": datetime.utcnow().isoformat(),
            "version": 1,
            "sections": {
                "executive_summary": self._generate_executive_summary(items, project_name),
                "business_objectives": self._generate_section(items_by_type.get("business_objective", [])),
                "stakeholder_analysis": self._generate_stakeholder_analysis(sources, items),
                "functional_requirements": self._generate_requirements_section(items_by_type.get("functional", [])),
                "non_functional_requirements": self._generate_requirements_section(items_by_type.get("non_functional", [])),
                "assumptions": self._generate_section(items_by_type.get("assumption", [])),
                "success_metrics": self._generate_section(items_by_type.get("success_metric", [])),
                "timeline": self._generate_timeline(sources),
                "conflicts": self._generate_conflicts_section(conflicts) if conflicts else None,
            }
        }
        
        return brd
    
    def _get_item_type(self, item: Union[ExtractedItem, ExtractedRequirement]) -> str:
        """Get item type from either ExtractedItem or ExtractedRequirement."""
        if isinstance(item, ExtractedRequirement):
            return item.requirement_type
        else:
            return item.item_type.value if hasattr(item.item_type, 'value') else str(item.item_type)
    
    def _get_confidence(self, item: Union[ExtractedItem, ExtractedRequirement]) -> float:
        """Get confidence score normalized to 0-1 range."""
        if isinstance(item, ExtractedRequirement):
            # ExtractedRequirement stores confidence as 0-100
            return item.confidence_score / 100.0 if item.confidence_score > 1 else item.confidence_score
        else:
            # ExtractedItem stores confidence as 0-1
            return item.confidence_score if item.confidence_score <= 1 else item.confidence_score / 100.0
    
    def _group_by_type(self, items: List[Union[ExtractedItem, ExtractedRequirement]]) -> Dict[str, List]:
        """Group extracted items by type."""
        grouped = {}
        for item in items:
            item_type = self._get_item_type(item)
            if item_type not in grouped:
                grouped[item_type] = []
            grouped[item_type].append(item)
        return grouped
    
    def _generate_executive_summary(self, items: List[Union[ExtractedItem, ExtractedRequirement]], project_name: str) -> Dict[str, Any]:
        """Generate executive summary section."""
        objectives = [item for item in items if self._get_item_type(item) == "business_objective"]
        
        summary_text = f"This document outlines the business requirements for {project_name}. "
        summary_text += f"The project encompasses {len(items)} identified requirements across functional, "
        summary_text += f"non-functional, and business objective categories. "
        
        if objectives:
            summary_text += f"Key objectives include: {', '.join([obj.content[:50] + '...' for obj in objectives[:3]])}."
        
        return {
            "content": summary_text,
            "statistics": {
                "total_requirements": len(items),
                "functional": len([i for i in items if self._get_item_type(i) == "functional"]),
                "non_functional": len([i for i in items if self._get_item_type(i) == "non_functional"]),
            }
        }
    
    def _generate_section(self, items: List[Union[ExtractedItem, ExtractedRequirement]]) -> Dict[str, Any]:
        """Generate a generic section with items and citations."""
        section_items = []
        for item in items:
            item_data = {
                "id": f"REQ-{item.id}",
                "content": item.content,
                "confidence": self._get_confidence(item),
            }
            
            # Add citation only if item has source (ExtractedItem)
            if hasattr(item, 'source') and item.source:
                item_data["citation"] = {
                    "source_id": item.source_id,
                    "source_type": item.source.source_type.value if item.source else None,
                    "author": item.source.author if item.source else None,
                    "timestamp": item.source.timestamp.isoformat() if item.source and item.source.timestamp else None,
                }
            
            section_items.append(item_data)
        
        return {"items": section_items}
    
    def _generate_requirements_section(self, items: List[Union[ExtractedItem, ExtractedRequirement]]) -> Dict[str, Any]:
        """Generate requirements section with priority."""
        section_items = []
        for item in items:
            confidence = self._get_confidence(item)
            
            # Use priority from ExtractedRequirement if available, otherwise calculate from confidence
            if isinstance(item, ExtractedRequirement) and hasattr(item, 'priority'):
                priority = item.priority.capitalize()
            else:
                priority = "High" if confidence > 0.8 else "Medium" if confidence > 0.5 else "Low"
            
            item_data = {
                "id": f"REQ-{item.id}",
                "content": item.content,
                "priority": priority,
            }
            
            # Add citation only if item has source (ExtractedItem)
            if hasattr(item, 'source') and item.source:
                item_data["citation"] = {
                    "source_id": item.source_id,
                    "source_type": item.source.source_type.value if item.source else None,
                    "author": item.source.author if item.source else None,
                }
            
            section_items.append(item_data)
        
        return {"items": section_items}
    
    def _generate_stakeholder_analysis(self, sources: List[DataSource], items: List[Union[ExtractedItem, ExtractedRequirement]]) -> Dict[str, Any]:
        """Generate stakeholder analysis section."""
        authors = {}
        for source in sources:
            if source.author:
                if source.author not in authors:
                    authors[source.author] = {"contributions": 0, "sentiment": []}
                authors[source.author]["contributions"] += 1
        
        # Only process sentiment for ExtractedItem (which has sentiment attribute)
        for item in items:
            if isinstance(item, ExtractedItem) and hasattr(item, 'source') and item.source and item.source.author and item.sentiment:
                if item.source.author in authors:
                    authors[item.source.author]["sentiment"].append(item.sentiment.value)
        
        stakeholders = []
        for author, data in authors.items():
            sentiment_summary = "neutral"
            if data["sentiment"]:
                positive = data["sentiment"].count("positive")
                negative = data["sentiment"].count("negative")
                if positive > negative:
                    sentiment_summary = "positive"
                elif negative > positive:
                    sentiment_summary = "negative"
            
            stakeholders.append({
                "name": author,
                "contributions": data["contributions"],
                "overall_sentiment": sentiment_summary
            })
        
        return {"stakeholders": stakeholders}
    
    def _generate_timeline(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Generate timeline section."""
        timestamps = [s.timestamp for s in sources if s.timestamp]
        
        if not timestamps:
            return {"content": "Timeline information not available from source data."}
        
        return {
            "project_start": min(timestamps).isoformat(),
            "latest_activity": max(timestamps).isoformat(),
            "total_days": (max(timestamps) - min(timestamps)).days
        }
    
    def _generate_conflicts_section(self, conflicts: List) -> Dict[str, Any]:
        """Generate conflicts section."""
        return {
            "total_conflicts": len(conflicts),
            "conflicts": [
                {
                    "id": f"CONFLICT-{c.id}",
                    "description": c.description,
                    "item1": c.item1.content if c.item1 else None,
                    "item2_id": c.item2_id,
                    "resolved": bool(c.resolved)
                }
                for c in conflicts
            ]
        }
    
    def generate_traceability_matrix(self, items: List[Union[ExtractedItem, ExtractedRequirement]]) -> List[Dict[str, Any]]:
        """Generate requirement traceability matrix."""
        matrix = []
        for item in items:
            item_type = self._get_item_type(item)
            
            matrix_item = {
                "requirement_id": f"REQ-{item.id}",
                "requirement_type": item_type,
                "content": item.content,
                "confidence": self._get_confidence(item),
            }
            
            # Add source info only if available (ExtractedItem)
            if hasattr(item, 'source') and item.source:
                matrix_item.update({
                    "source_type": item.source.source_type.value if item.source else None,
                    "source_author": item.source.author if item.source else None,
                    "source_timestamp": item.source.timestamp.isoformat() if item.source and item.source.timestamp else None,
                })
            
            matrix.append(matrix_item)
        
        return matrix
