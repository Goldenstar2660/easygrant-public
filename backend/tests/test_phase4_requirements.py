"""Test requirements extraction (Phase 4)"""

import pytest
from pathlib import Path
from backend.src.agents.requirements_extractor import RequirementsExtractor


@pytest.fixture
def sample_funding_text():
    """Sample funding call text with sections and limits"""
    return """
    GRANT FUNDING CALL - Community Development
    
    APPLICATION SECTIONS:
    
    1. Project Summary (REQUIRED)
       Provide a brief overview of your project in up to 500 words.
       Scoring: 20 points
    
    2. Project Description (REQUIRED)
       Detailed narrative not to exceed 1000 words.
       Scoring: 40 points
    
    3. Budget Narrative (REQUIRED)
       Maximum 500 words explaining budget items.
       Scoring: 15 points
    
    4. Letters of Support (OPTIONAL)
       Up to 3 letters from community partners.
    
    ELIGIBILITY:
    - Must be registered 501(c)(3) organization
    - Operating for at least 2 years
    - Serving population under 50,000
    
    DEADLINE: December 31, 2024
    """


def test_word_limit_extraction(sample_funding_text):
    """Test regex-based word limit extraction"""
    extractor = RequirementsExtractor()
    limits = extractor._extract_word_limits(sample_funding_text)
    
    # Should find word limits
    assert len(limits) > 0
    # Check if 500 or 1000 appear in any limit values
    limit_values = list(limits.values())
    assert any(v == 500 for v in limit_values) or any(v == 1000 for v in limit_values)


def test_blueprint_validation():
    """Test blueprint validation logic"""
    extractor = RequirementsExtractor()
    
    # Valid blueprint
    valid_blueprint = {
        "sections": [
            {
                "name": "Project Summary",
                "required": True,
                "word_limit": 500,
                "char_limit": None,
                "format": "narrative",
                "scoring_weight": 20.0
            }
        ],
        "eligibility": ["Must be 501(c)(3)"],
        "total_sections": 1
    }
    assert extractor._validate_blueprint(valid_blueprint) is True
    
    # Invalid - no sections
    invalid_blueprint = {
        "sections": [],
        "eligibility": [],
        "total_sections": 0
    }
    assert extractor._validate_blueprint(invalid_blueprint) is False
    
    # Invalid - missing required field
    invalid_blueprint2 = {
        "sections": [
            {"name": "Summary"}  # Missing 'required' and 'format'
        ],
        "eligibility": [],
        "total_sections": 1
    }
    assert extractor._validate_blueprint(invalid_blueprint2) is False


def test_fallback_blueprint(sample_funding_text):
    """Test fallback blueprint creation"""
    extractor = RequirementsExtractor()
    blueprint = extractor._create_fallback_blueprint(sample_funding_text, {})
    
    # Should have basic structure
    assert "sections" in blueprint
    assert "eligibility" in blueprint
    assert "total_sections" in blueprint
    assert len(blueprint["sections"]) > 0


def test_blueprint_summary():
    """Test summary generation"""
    extractor = RequirementsExtractor()
    
    blueprint = {
        "sections": [
            {
                "name": "Project Summary",
                "required": True,
                "word_limit": 500,
                "char_limit": None,
                "format": "narrative",
                "scoring_weight": None
            },
            {
                "name": "Letters",
                "required": False,
                "word_limit": None,
                "char_limit": None,
                "format": "other",
                "scoring_weight": None
            }
        ],
        "eligibility": ["501(c)(3)", "2+ years"],
        "total_sections": 2
    }
    
    summary = extractor.get_blueprint_summary(blueprint)
    
    assert "Total Sections: 2" in summary
    assert "1 required" in summary
    assert "1 optional" in summary
    assert "Project Summary" in summary
    assert "500 words max" in summary


def test_invalid_word_limit():
    """Test that invalid word limits are rejected"""
    extractor = RequirementsExtractor()
    
    # Negative word limit
    invalid_blueprint = {
        "sections": [
            {
                "name": "Test",
                "required": True,
                "word_limit": -100,  # Invalid
                "char_limit": None,
                "format": "narrative"
            }
        ],
        "eligibility": [],
        "total_sections": 1
    }
    assert extractor._validate_blueprint(invalid_blueprint) is False
    
    # Zero word limit
    invalid_blueprint2 = {
        "sections": [
            {
                "name": "Test",
                "required": True,
                "word_limit": 0,  # Invalid
                "char_limit": None,
                "format": "narrative"
            }
        ],
        "eligibility": [],
        "total_sections": 1
    }
    assert extractor._validate_blueprint(invalid_blueprint2) is False
