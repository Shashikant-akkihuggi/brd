import sys
sys.path.insert(0, '../backend')

from app.services.extractor import InformationExtractor
from app.models import RequirementType, SentimentType

def test_extract_functional_requirements():
    extractor = InformationExtractor()
    
    text = "The system shall allow users to login with email and password. The application must support two-factor authentication."
    
    results = extractor.extract_requirements(text)
    
    assert len(results) > 0
    assert any(r['type'] == RequirementType.FUNCTIONAL for r in results)
    print("✓ Functional requirements extraction works")

def test_extract_business_objectives():
    extractor = InformationExtractor()
    
    text = "Our goal is to increase user engagement by 50%. We need to improve the checkout conversion rate."
    
    results = extractor.extract_requirements(text)
    
    assert len(results) > 0
    assert any(r['type'] == RequirementType.BUSINESS_OBJECTIVE for r in results)
    print("✓ Business objectives extraction works")

def test_sentiment_analysis():
    extractor = InformationExtractor()
    
    positive_text = "This is a great feature and I'm excited about it"
    negative_text = "I'm concerned about the security risks and potential problems"
    
    pos_sentiment = extractor._analyze_sentiment(positive_text)
    neg_sentiment = extractor._analyze_sentiment(negative_text)
    
    assert pos_sentiment == SentimentType.POSITIVE
    assert neg_sentiment == SentimentType.NEGATIVE
    print("✓ Sentiment analysis works")

def test_conflict_detection():
    extractor = InformationExtractor()
    
    items = [
        {"content": "The system must support offline mode"},
        {"content": "The system cannot work without internet connection"},
    ]
    
    conflicts = extractor.detect_conflicts(items)
    
    assert len(conflicts) > 0
    print("✓ Conflict detection works")

def test_keyword_filtering():
    extractor = InformationExtractor()
    
    text = "We need to implement payment processing"
    keywords = ["payment", "checkout"]
    
    assert extractor._is_relevant(text, keywords)
    
    irrelevant_text = "The weather is nice today"
    assert not extractor._is_relevant(irrelevant_text, keywords)
    print("✓ Keyword filtering works")

if __name__ == "__main__":
    test_extract_functional_requirements()
    test_extract_business_objectives()
    test_sentiment_analysis()
    test_conflict_detection()
    test_keyword_filtering()
    print("\n✅ All tests passed!")
