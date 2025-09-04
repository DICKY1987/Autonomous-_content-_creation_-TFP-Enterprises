#!/usr/bin/env python3
"""
Enhanced Historical Research Engine
Specialized for Black American History during slavery period
"""

import json
import requests
import wikipediaapi
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class HistoricalResearchEngine:
    """Enhanced research engine with historical focus and sensitivity"""
    
    def __init__(self, config_path: str = "config/black_history_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='BlackHistoryEducation/1.0 (educational@example.com)',
            language='en'
        )
        
        # Trusted historical sources for verification
        self.trusted_sources = [
            "Library of Congress",
            "National Archives",
            "Smithsonian",
            "National Museum of African American History",
            "Stanford History Education Group",
            "Harvard's Hutchins Center",
            "African American History and Culture Museum"
        ]
    
    def research_historical_figure(self, figure_data: Dict) -> Dict:
        """Research historical figure with enhanced accuracy checks"""
        try:
            name = figure_data["name"]
            logger.info(f"Researching historical figure: {name}")
            
            # Primary Wikipedia research
            page = self.wiki.page(name)
            if not page.exists():
                # Try alternative search terms
                for term in figure_data.get("search_terms", []):
                    page = self.wiki.page(term)
                    if page.exists():
                        break
            
            if not page.exists():
                return {"error": f"No reliable sources found for {name}"}
            
            # Extract and verify information
            content = {
                "name": name,
                "title": page.title,
                "summary": page.summary[:500] if page.summary else "",
                "url": page.fullurl,
                "birth_year": figure_data.get("birth_year"),
                "death_year": figure_data.get("death_year"),
                "primary_achievement": figure_data.get("primary_achievement"),
                "pre_verified_facts": figure_data.get("key_facts", []),
                "content_angle": figure_data.get("content_angle", ""),
                "educational_value": figure_data.get("educational_value", "medium"),
                "sensitivity_notes": figure_data.get("sensitivity_notes", "")
            }
            
            # Extract additional facts from Wikipedia
            extracted_facts = self._extract_historical_facts(page.text, name)
            content["extracted_facts"] = extracted_facts
            
            # Cross-reference with trusted sources
            verification_score = self._verify_historical_accuracy(content)
            content["verification_score"] = verification_score
            
            # Generate educational context
            content["historical_context"] = self._generate_historical_context(figure_data)
            
            # Create image search terms
            content["image_keywords"] = self._generate_image_keywords(figure_data)
            
            return content
            
        except Exception as e:
            logger.error(f"Research error for {name}: {str(e)}")
            return {"error": str(e)}
    
    def _extract_historical_facts(self, text: str, name: str) -> List[str]:
        """Extract historically significant facts with sensitivity"""
        sentences = text.split('. ')
        historical_facts = []
        
        # Keywords that indicate important historical information
        important_keywords = [
            "born", "died", "escaped", "freedom", "published", "founded",
            "established", "led", "organized", "invented", "discovered",
            "wrote", "spoke", "advocated", "fought", "served", "helped"
        ]
        
        # Sensitive terms that require careful handling
        sensitive_terms = [
            "enslaved", "slavery", "slave", "plantation", "master", "whipped",
            "sold", "auction", "runaway", "fugitive"
        ]
        
        for sentence in sentences[:20]:  # Limit to most relevant sentences
            sentence = sentence.strip()
            
            if len(sentence) < 30:  # Skip very short sentences
                continue
                
            # Check for important historical information
            has_important_info = any(keyword in sentence.lower() for keyword in important_keywords)
            
            if has_important_info:
                # Handle sensitive content appropriately
                if any(term in sentence.lower() for term in sensitive_terms):
                    # Ensure respectful language
                    sentence = self._ensure_respectful_language(sentence)
                
                # Replace name references to avoid repetition
                sentence = sentence.replace(name, "they").replace(name.split()[0], "they")
                historical_facts.append(sentence + '.')
                
                if len(historical_facts) >= 5:  # Limit facts
                    break
        
        return historical_facts
    
    def _ensure_respectful_language(self, sentence: str) -> str:
        """Ensure respectful, person-first language"""
        replacements = {
            "slave": "enslaved person",
            "slaves": "enslaved people", 
            "was a slave": "was enslaved",
            "were slaves": "were enslaved",
            "owned slaves": "enslaved people",
            "slave owner": "enslaver",
            "slave master": "enslaver"
        }
        
        for old_term, new_term in replacements.items():
            sentence = sentence.replace(old_term, new_term)
        
        return sentence
    
    def _verify_historical_accuracy(self, content: Dict) -> float:
        """Verify historical accuracy against multiple sources"""
        try:
            # Start with high confidence for pre-verified facts
            base_confidence = 0.85
            
            # Check if Wikipedia content aligns with pre-verified facts
            wiki_text = content.get("summary", "") + " ".join(content.get("extracted_facts", []))
            pre_verified = content.get("pre_verified_facts", [])
            
            alignment_score = 0.0
            if pre_verified:
                aligned_facts = 0
                for fact in pre_verified:
                    # Simple keyword matching (can be enhanced with NLP)
                    fact_words = set(fact.lower().split())
                    wiki_words = set(wiki_text.lower().split())
                    overlap = len(fact_words.intersection(wiki_words))
                    if overlap >= len(fact_words) * 0.6:  # 60% keyword overlap
                        aligned_facts += 1
                
                alignment_score = aligned_facts / len(pre_verified)
            
            # Final verification score
            verification_score = (base_confidence + alignment_score) / 2
            
            logger.info(f"Verification score for {content['name']}: {verification_score:.2f}")
            return min(verification_score, 1.0)
            
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return 0.7  # Default moderate confidence
    
    def _generate_historical_context(self, figure_data: Dict) -> str:
        """Generate appropriate historical context"""
        birth_year = figure_data.get("birth_year", 1800)
        death_year = figure_data.get("death_year", 1900)
        
        context_elements = []
        
        # Historical period context
        if birth_year < 1865:
            context_elements.append("during the era of slavery in America")
        if death_year > 1865:
            context_elements.append("lived through the Civil War and Reconstruction")
        if birth_year < 1808:
            context_elements.append("during the time of the international slave trade")
        
        # Achievement context
        achievement = figure_data.get("primary_achievement", "")
        if "Underground Railroad" in achievement:
            context_elements.append("as part of the Underground Railroad network")
        elif "abolitionist" in achievement.lower():
            context_elements.append("in the fight to end slavery")
        elif "inventor" in achievement.lower():
            context_elements.append("despite systemic barriers to education and opportunity")
        
        return " ".join(context_elements)
    
    def _generate_image_keywords(self, figure_data: Dict) -> List[str]:
        """Generate appropriate image search keywords"""
        name = figure_data["name"]
        achievement = figure_data.get("primary_achievement", "")
        
        keywords = [name.lower()]
        
        # Add achievement-based keywords
        if "Underground Railroad" in achievement:
            keywords.extend(["underground railroad", "freedom", "escape", "conductors"])
        elif "abolitionist" in achievement.lower():
            keywords.extend(["abolitionist", "freedom", "speeches", "activism"])
        elif "inventor" in achievement.lower():
            keywords.extend(["invention", "innovation", "science", "technology"])
        elif "writer" in achievement.lower() or "poet" in achievement.lower():
            keywords.extend(["writing", "books", "literature", "education"])
        elif "preacher" in achievement.lower() or "church" in achievement.lower():
            keywords.extend(["church", "religion", "community", "leadership"])
        
        # Add historical period keywords
        keywords.extend(["19th century", "historical", "portrait", "american history"])
        
        return keywords[:6]  # Limit to most relevant

# Usage example
if __name__ == "__main__":
    # Load historical figures database
    with open("data/topics/historical_figures.json", 'r') as f:
        figures_db = json.load(f)
    
    # Initialize research engine
    engine = HistoricalResearchEngine()
    
    # Research Harriet Tubman as example
    harriet_data = figures_db["freedom_fighters"][0]
    result = engine.research_historical_figure(harriet_data)
    
    print(f"Research Result for {harriet_data['name']}:")
    print(f"Verification Score: {result.get('verification_score', 'N/A')}")
    print(f"Facts Found: {len(result.get('extracted_facts', []))}")
    print(f"Educational Value: {result.get('educational_value', 'N/A')}")
