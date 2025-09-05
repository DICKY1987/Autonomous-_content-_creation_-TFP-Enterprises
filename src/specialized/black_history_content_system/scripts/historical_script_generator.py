#!/usr/bin/env python3
"""
Historical Script Generator
Creates respectful, educational scripts about Black American history
"""

import json
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class HistoricalScriptGenerator:
    """Generates educational scripts with historical sensitivity"""
    
    def __init__(self):
        self.script_templates = {
            "freedom_fighter": {
                "hook": "Meet {name}, a hero whose courage changed American history forever.",
                "structure": [
                    "Early life and background",
                    "Major accomplishments", 
                    "Impact on freedom movement",
                    "Legacy and inspiration"
                ],
                "tone": "inspirational_respectful"
            },
            "intellectual": {
                "hook": "In an era when education was denied to most Black Americans, {name} broke every barrier.",
                "structure": [
                    "Overcoming educational barriers",
                    "Intellectual achievements",
                    "Challenging stereotypes",
                    "Lasting contributions"
                ],
                "tone": "educational_empowering"
            },
            "inventor": {
                "hook": "While facing systemic oppression, {name} created innovations that changed the world.",
                "structure": [
                    "Background and challenges",
                    "Revolutionary inventions",
                    "Impact on society",
                    "Recognition and legacy"
                ],
                "tone": "achievement_focused"
            },
            "religious_leader": {
                "hook": "{name} didn't just lead a congregation - they built a movement for freedom and dignity.",
                "structure": [
                    "Call to ministry",
                    "Community building",
                    "Social justice work",
                    "Institutional legacy"
                ],
                "tone": "community_inspiring"
            }
        }
        
        self.transition_phrases = [
            "But their story doesn't end there.",
            "Here's what makes their legacy extraordinary.",
            "Against all odds, they achieved something remarkable.",
            "Their courage opened doors for generations.",
            "This is why their story matters today."
        ]
        
        self.respectful_language_guidelines = {
            "person_first": True,
            "avoid_terms": ["slave", "owned", "belonged to"],
            "preferred_terms": {
                "slave": "enslaved person",
                "slaves": "enslaved people",
                "was a slave": "was enslaved",
                "slave owner": "enslaver",
                "plantation owner": "enslaver"
            }
        }
    
    def generate_script(self, research_data: Dict) -> str:
        """Generate educational script from research data"""
        try:
            name = research_data["name"]
            achievement = research_data.get("primary_achievement", "")
            content_angle = research_data.get("content_angle", "")
            facts = research_data.get("pre_verified_facts", []) + research_data.get("extracted_facts", [])
            
            # Determine script template based on achievement
            template_type = self._determine_template_type(achievement)
            template = self.script_templates.get(template_type, self.script_templates["freedom_fighter"])
            
            # Generate script sections
            hook = template["hook"].format(name=name)
            
            # Select and organize key facts
            selected_facts = self._select_key_facts(facts, max_facts=3)
            
            # Build script narrative
            script_parts = [hook]
            
            # Add fact-based content with respectful framing
            for i, fact in enumerate(selected_facts, 1):
                # Clean and frame the fact
                framed_fact = self._frame_fact_respectfully(fact, name)
                
                # Add transition if needed
                if i > 1 and i <= len(self.transition_phrases):
                    transition = self.transition_phrases[i-2]
                    script_parts.append(transition)
                
                script_parts.append(framed_fact)
            
            # Add educational conclusion
            conclusion = self._generate_conclusion(name, content_angle)
            script_parts.append(conclusion)
            
            # Join script and apply final checks
            script = " ".join(script_parts)
            script = self._apply_language_guidelines(script)
            script = self._ensure_appropriate_length(script, target_seconds=45)
            
            logger.info(f"Generated script for {name}: {len(script)} characters")
            return script
            
        except Exception as e:
            logger.error(f"Script generation error: {str(e)}")
            return self._generate_fallback_script(research_data)
    
    def _determine_template_type(self, achievement: str) -> str:
        """Determine appropriate script template"""
        achievement_lower = achievement.lower()
        
        if any(term in achievement_lower for term in ["underground railroad", "conductor", "abolitionist", "freedom"]):
            return "freedom_fighter"
        elif any(term in achievement_lower for term in ["writer", "poet", "intellectual", "scholar"]):
            return "intellectual"
        elif any(term in achievement_lower for term in ["inventor", "scientist", "engineer"]):
            return "inventor"
        elif any(term in achievement_lower for term in ["preacher", "minister", "church", "bishop"]):
            return "religious_leader"
        else:
            return "freedom_fighter"  # Default
    
    def _select_key_facts(self, facts: List[str], max_facts: int = 3) -> List[str]:
        """Select most impactful facts for the script"""
        if not facts:
            return []
        
        # Score facts by educational value and impact
        scored_facts = []
        
        high_impact_keywords = [
            "first", "founded", "established", "invented", "published", "led", 
            "escaped", "saved", "helped", "taught", "advocated", "fought"
        ]
        
        for fact in facts:
            score = 0
            fact_lower = fact.lower()
            
            # Boost score for high-impact keywords
            for keyword in high_impact_keywords:
                if keyword in fact_lower:
                    score += 2
            
            # Boost for specific achievements
            if any(term in fact_lower for term in ["freedom", "education", "rights", "equality"]):
                score += 1
            
            # Prefer facts with numbers (concrete achievements)
            if any(char.isdigit() for char in fact):
                score += 1
            
            # Prefer appropriate length facts
            if 50 <= len(fact) <= 200:
                score += 1
            
            scored_facts.append((score, fact))
        
        # Sort by score and select top facts
        scored_facts.sort(reverse=True, key=lambda x: x[0])
        return [fact for _, fact in scored_facts[:max_facts]]
    
    def _frame_fact_respectfully(self, fact: str, name: str) -> str:
        """Frame historical fact with appropriate context and respect"""
        # Apply respectful language guidelines
        fact = self._apply_language_guidelines(fact)
        
        # Add contextual framing for sensitive topics
        if any(term in fact.lower() for term in ["enslaved", "slavery", "plantation"]):
            if not any(term in fact.lower() for term in ["despite", "although", "even though"]):
                fact = f"Despite the brutal system of slavery, {fact.lower()}"
        
        # Ensure person-first language
        fact = fact.replace(f"{name} was a slave", f"{name} was enslaved")
        fact = fact.replace(f"{name} was born a slave", f"{name} was born into slavery")
        
        return fact.strip()
    
    def _apply_language_guidelines(self, text: str) -> str:
        """Apply respectful language guidelines"""
        for old_term, new_term in self.respectful_language_guidelines["preferred_terms"].items():
            text = text.replace(old_term, new_term)
            text = text.replace(old_term.capitalize(), new_term.capitalize())
        
        return text
    
    def _generate_conclusion(self, name: str, content_angle: str) -> str:
        """Generate inspiring educational conclusion"""
        conclusions = [
            f"{name}'s legacy continues to inspire us today. Their courage reminds us that one person can change history.",
            f"The story of {name} shows us the power of determination and the fight for justice. Their impact lives on.",
            f"{name} didn't just overcome impossible odds - they opened doors for future generations. That's true heroism.",
            f"Remember {name} not just for what they accomplished, but for showing us what's possible when we refuse to give up.",
            f"Today, we honor {name} and all who fought for freedom and equality. Their sacrifice made our progress possible."
        ]
        
        # Select conclusion based on content angle
        if content_angle:
            return f"{content_angle.replace('The ', '').capitalize()}. {conclusions[0]}"
        else:
            # Use name hash to select consistent but varied conclusion
            conclusion_index = hash(name) % len(conclusions)
            return conclusions[conclusion_index]
    
    def _ensure_appropriate_length(self, script: str, target_seconds: int = 45) -> str:
        """Ensure script fits target duration (approximately 150 words per minute)"""
        target_words = int(target_seconds * 2.5)  # ~150 words per minute
        words = script.split()
        
        if len(words) > target_words:
            # Trim while maintaining narrative flow
            trimmed_words = words[:target_words]
            # Try to end at a complete sentence
            script = " ".join(trimmed_words)
            if not script.endswith(('.', '!', '?')):
                # Find last complete sentence
                sentences = script.split('. ')
                if len(sentences) > 1:
                    script = '. '.join(sentences[:-1]) + '.'
        
        return script
    
    def _generate_fallback_script(self, research_data: Dict) -> str:
        """Generate basic fallback script if main generation fails"""
        name = research_data.get("name", "This person")
        achievement = research_data.get("primary_achievement", "made important contributions")
        
        return f"Meet {name}, whose {achievement.lower()} helped shape American history. Despite facing incredible challenges, they persevered and made a lasting impact. Their story reminds us of the courage and determination that built our nation. We honor their legacy and the path they created for future generations."

# Usage example and testing
if __name__ == "__main__":
    # Test with sample research data
    sample_data = {
        "name": "Harriet Tubman",
        "primary_achievement": "Underground Railroad Conductor",
        "content_angle": "The woman who never lost a passenger",
        "pre_verified_facts": [
            "Led over 300 enslaved people to freedom",
            "Never lost a single person on Underground Railroad missions", 
            "Served as spy for Union Army during Civil War"
        ],
        "extracted_facts": [
            "She was born into slavery around 1822 in Maryland",
            "She escaped slavery in 1849 and immediately began helping others"
        ]
    }
    
    generator = HistoricalScriptGenerator()
    script = generator.generate_script(sample_data)
    
    print("Generated Script:")
    print("=" * 50)
    print(script)
    print("=" * 50)
    print(f"Word count: {len(script.split())}")
    print(f"Character count: {len(script)}")
