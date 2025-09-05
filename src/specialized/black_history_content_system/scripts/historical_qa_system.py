#!/usr/bin/env python3
"""
Historical Content Quality Assurance System
Specialized QA for sensitive historical content about Black American history
"""

import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class HistoricalQualityReport:
    """Quality report for historical content"""
    historical_accuracy: float
    cultural_sensitivity: float
    educational_value: float
    factual_verification: float
    language_appropriateness: float
    overall_score: float
    issues: List[str]
    recommendations: List[str]
    approved_for_publication: bool

class HistoricalQualityAssurance:
    """Quality assurance system for historical educational content"""
    
    def __init__(self, config_path: str = "config/black_history_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.quality_thresholds = self.config["content_standards"]
        
        # Problematic terms that should be flagged or avoided
        self.problematic_terms = {
            "avoid_completely": [
                "good slave", "happy slave", "loyal slave", "faithful slave",
                "slave master", "master and slave", "owned slaves"
            ],
            "requires_context": [
                "primitive", "savage", "uncivilized", "backward",
                "discovered", "found" # when referring to places where people already lived
            ],
            "outdated_language": [
                "negro", "colored", # unless in historical quotes with context
                "plantation owner", "slave owner"  # prefer "enslaver"
            ]
        }
        
        # Positive framing indicators
        self.positive_framings = [
            "despite", "overcome", "achieved", "persevered", "fought", "resisted",
            "dignity", "courage", "strength", "determination", "intelligence",
            "leadership", "community", "family", "culture", "heritage"
        ]
        
        # Required educational elements
        self.educational_requirements = {
            "historical_context": ["era", "period", "during", "time", "century"],
            "impact_description": ["impact", "influence", "changed", "affected", "legacy"],
            "human_agency": ["chose", "decided", "led", "organized", "created"],
            "systemic_understanding": ["system", "institution", "structure", "policy"]
        }
    
    def evaluate_content(self, research_data: Dict, script: str, 
                        metadata: Dict = None) -> HistoricalQualityReport:
        """Comprehensive quality evaluation of historical content"""
        try:
            logger.info(f"Evaluating content for {research_data.get('name', 'Unknown')}")
            
            # Individual quality assessments
            accuracy_score = self._assess_historical_accuracy(research_data, script)
            sensitivity_score = self._assess_cultural_sensitivity(script)
            educational_score = self._assess_educational_value(script, research_data)
            verification_score = research_data.get("verification_score", 0.7)
            language_score = self._assess_language_appropriateness(script)
            
            # Calculate overall score (weighted)
            weights = {
                "accuracy": 0.25,
                "sensitivity": 0.25, 
                "educational": 0.20,
                "verification": 0.20,
                "language": 0.10
            }
            
            overall_score = (
                accuracy_score * weights["accuracy"] +
                sensitivity_score * weights["sensitivity"] +
                educational_score * weights["educational"] +
                verification_score * weights["verification"] +
                language_score * weights["language"]
            )
            
            # Collect issues and recommendations
            issues = []
            recommendations = []
            
            issues.extend(self._check_for_issues(script))
            recommendations.extend(self._generate_recommendations(
                accuracy_score, sensitivity_score, educational_score, language_score
            ))
            
            # Determine approval status
            min_threshold = self.quality_thresholds["historical_accuracy_threshold"]
            approved = (
                overall_score >= min_threshold and
                sensitivity_score >= 0.90 and
                accuracy_score >= min_threshold and
                len(issues) == 0
            )
            
            return HistoricalQualityReport(
                historical_accuracy=accuracy_score,
                cultural_sensitivity=sensitivity_score,
                educational_value=educational_score,
                factual_verification=verification_score,
                language_appropriateness=language_score,
                overall_score=overall_score,
                issues=issues,
                recommendations=recommendations,
                approved_for_publication=approved
            )
            
        except Exception as e:
            logger.error(f"QA evaluation error: {str(e)}")
            return HistoricalQualityReport(
                historical_accuracy=0.0,
                cultural_sensitivity=0.0,
                educational_value=0.0,
                factual_verification=0.0,
                language_appropriateness=0.0,
                overall_score=0.0,
                issues=[f"QA system error: {str(e)}"],
                recommendations=["Manual review required"],
                approved_for_publication=False
            )
    
    def _assess_historical_accuracy(self, research_data: Dict, script: str) -> float:
        """Assess historical accuracy of content"""
        score = 0.8  # Base score
        
        # Check if script aligns with verified facts
        pre_verified_facts = research_data.get("pre_verified_facts", [])
        script_lower = script.lower()
        
        if pre_verified_facts:
            aligned_facts = 0
            for fact in pre_verified_facts:
                fact_keywords = [word for word in fact.lower().split() if len(word) > 3]
                keyword_matches = sum(1 for keyword in fact_keywords if keyword in script_lower)
                if keyword_matches >= len(fact_keywords) * 0.5:  # 50% keyword match
                    aligned_facts += 1
            
            alignment_ratio = aligned_facts / len(pre_verified_facts)
            score = score * (0.5 + 0.5 * alignment_ratio)  # Adjust based on alignment
        
        # Check for historical period consistency
        birth_year = research_data.get("birth_year")
        death_year = research_data.get("death_year")
        
        if birth_year and birth_year < 1865:
            if "civil war" in script_lower and birth_year > 1861:
                score += 0.05  # Bonus for appropriate historical context
            if "slavery" in script_lower or "enslaved" in script_lower:
                score += 0.05  # Bonus for acknowledging slavery context
        
        return min(score, 1.0)
    
    def _assess_cultural_sensitivity(self, script: str) -> float:
        """Assess cultural sensitivity and respectful representation"""
        score = 1.0  # Start with perfect score, deduct for issues
        issues_found = []
        
        script_lower = script.lower()
        
        # Check for completely inappropriate terms
        for term in self.problematic_terms["avoid_completely"]:
            if term.lower() in script_lower:
                score -= 0.3
                issues_found.append(f"Inappropriate term found: {term}")
        
        # Check for outdated language
        for term in self.problematic_terms["outdated_language"]:
            if term.lower() in script_lower:
                score -= 0.1
                issues_found.append(f"Outdated language: {term}")
        
        # Check for terms requiring context
        for term in self.problematic_terms["requires_context"]:
            if term.lower() in script_lower:
                # Look for contextual framing around the term
                context_found = any(frame in script_lower for frame in 
                                  ["despite", "although", "even though", "context of", "during the"])
                if not context_found:
                    score -= 0.15
                    issues_found.append(f"Term needs better context: {term}")
        
        # Bonus for positive framing
        positive_count = sum(1 for term in self.positive_framings if term in script_lower)
        if positive_count >= 3:
            score += 0.05  # Small bonus for positive framing
        
        # Check for person-first language
        if "enslaved person" in script_lower or "enslaved people" in script_lower:
            score += 0.05  # Bonus for person-first language
        
        return max(score, 0.0)
    
    def _assess_educational_value(self, script: str, research_data: Dict) -> float:
        """Assess educational value and learning outcomes"""
        score = 0.6  # Base score
        script_lower = script.lower()
        
        # Check for educational elements
        for category, keywords in self.educational_requirements.items():
            if any(keyword in script_lower for keyword in keywords):
                score += 0.1
        
        # Check for specific learning outcomes
        learning_indicators = [
            "learn", "discover", "understand", "shows us", "reminds us",
            "teaches us", "demonstrates", "reveals", "illustrates"
        ]
        
        learning_count = sum(1 for indicator in learning_indicators if indicator in script_lower)
        if learning_count >= 2:
            score += 0.1
        
        # Check for connection to broader themes
        broader_themes = [
            "freedom", "justice", "equality", "rights", "dignity", "courage",
            "leadership", "community", "education", "innovation", "legacy"
        ]
        
        theme_count = sum(1 for theme in broader_themes if theme in script_lower)
        if theme_count >= 3:
            score += 0.1
        
        # Check for contemporary relevance
        contemporary_terms = [
            "today", "still", "continues", "legacy", "inspiration", "remember",
            "honor", "impact lives on", "reminds us"
        ]
        
        if any(term in script_lower for term in contemporary_terms):
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_language_appropriateness(self, script: str) -> float:
        """Assess language appropriateness for educational content"""
        score = 0.9  # Start high
        
        # Check reading level (simple metric)
        words = script.split()
        long_words = [word for word in words if len(word) > 8]
        if len(long_words) / len(words) > 0.15:  # More than 15% long words
            score -= 0.1
        
        # Check sentence structure (avoid overly complex sentences)
        sentences = script.split('. ')
        long_sentences = [s for s in sentences if len(s.split()) > 25]
        if len(long_sentences) / len(sentences) > 0.3:  # More than 30% long sentences
            score -= 0.1
        
        # Bonus for clear, engaging language
        engaging_words = [
            "amazing", "incredible", "remarkable", "extraordinary", "inspiring",
            "powerful", "courageous", "determined", "brilliant", "heroic"
        ]
        
        engaging_count = sum(1 for word in engaging_words if word in script.lower())
        if engaging_count >= 2:
            score += 0.05
        
        return max(score, 0.0)
    
    def _check_for_issues(self, script: str) -> List[str]:
        """Check for specific issues requiring attention"""
        issues = []
        script_lower = script.lower()
        
        # Check for problematic terms
        for term in self.problematic_terms["avoid_completely"]:
            if term.lower() in script_lower:
                issues.append(f"CRITICAL: Inappropriate language detected - '{term}'")
        
        # Check for missing context on sensitive topics
        if any(term in script_lower for term in ["slavery", "enslaved", "plantation"]):
            if not any(frame in script_lower for frame in ["despite", "system of", "institution of"]):
                issues.append("Sensitive historical topic needs better contextual framing")
        
        # Check for overgeneralization
        overgeneralization_terms = ["all slaves", "every slave", "slaves were", "slaves did"]
        for term in overgeneralization_terms:
            if term in script_lower:
                issues.append(f"Overgeneralization detected: '{term}' - use specific examples instead")
        
        return issues
    
    def _generate_recommendations(self, accuracy: float, sensitivity: float, 
                                educational: float, language: float) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        if accuracy < 0.85:
            recommendations.append("Verify historical facts against multiple reputable sources")
            recommendations.append("Add more specific dates, locations, or quantitative details")
        
        if sensitivity < 0.90:
            recommendations.append("Review language for cultural sensitivity and person-first terminology")
            recommendations.append("Consider adding historical context for sensitive topics")
        
        if educational < 0.80:
            recommendations.append("Strengthen educational value by connecting to broader themes")
            recommendations.append("Add clear learning outcomes or contemporary relevance")
        
        if language < 0.85:
            recommendations.append("Simplify language for broader accessibility")
            recommendations.append("Use more engaging and inspiring descriptive words")
        
        return recommendations

# Usage example
if __name__ == "__main__":
    # Test with sample content
    sample_research = {
        "name": "Frederick Douglass",
        "verification_score": 0.92,
        "pre_verified_facts": [
            "Self-taught to read and write while enslaved",
            "Published three autobiographies",
            "Advised President Lincoln during Civil War"
        ],
        "birth_year": 1818,
        "death_year": 1895
    }
    
    sample_script = """Meet Frederick Douglass, a hero whose courage changed American history forever. Despite being enslaved, he secretly learned to read and write, proving the intellectual equality that slavery tried to deny. He escaped to freedom and became one of America's most powerful speakers against slavery. His autobiographies opened the world's eyes to the brutal reality of enslavement. During the Civil War, he advised President Lincoln and helped recruit Black soldiers. Frederick Douglass showed us that education and determination can overcome any obstacle. His legacy reminds us that one person's voice can change the world."""
    
    qa_system = HistoricalQualityAssurance()
    report = qa_system.evaluate_content(sample_research, sample_script)
    
    print("Quality Assessment Report:")
    print(f"Historical Accuracy: {report.historical_accuracy:.2f}")
    print(f"Cultural Sensitivity: {report.cultural_sensitivity:.2f}")
    print(f"Educational Value: {report.educational_value:.2f}")
    print(f"Overall Score: {report.overall_score:.2f}")
    print(f"Approved: {report.approved_for_publication}")
    
    if report.issues:
        print("\nIssues:")
        for issue in report.issues:
            print(f"- {issue}")
    
    if report.recommendations:
        print("\nRecommendations:")
        for rec in report.recommendations:
            print(f"- {rec}")
