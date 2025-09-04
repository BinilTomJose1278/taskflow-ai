#!/usr/bin/env python3
"""
Demo script to showcase the Document Analysis feature
"""

import asyncio
import json
from app.services.document_analysis_service import DocumentAnalysisService

async def demo_analysis():
    """Demonstrate the document analysis capabilities"""
    
    print("🔍 Document Analysis Demo")
    print("=" * 50)
    
    # Initialize the analysis service
    analysis_service = DocumentAnalysisService()
    
    # Sample document text (simulating a contract)
    sample_text = """
    CONTRACT AGREEMENT
    
    This agreement is entered into between Company A and Company B for the provision of software development services.
    
    TERMS AND CONDITIONS:
    1. The project duration shall be 6 months
    2. Payment terms: 50% upfront ($25,000), 50% on completion ($25,000)
    3. Intellectual property rights remain with Company A
    4. Confidentiality clause applies to all parties
    5. Liability is limited to the contract value
    
    SIGNATURES:
    Company A Representative: John Smith
    Company B Representative: Jane Doe
    Date: 2024-01-15
    Project Start: 2024-02-01
    Project End: 2024-07-31
    """
    
    print("📄 Sample Document Text:")
    print(sample_text)
    print("\n" + "=" * 50)
    
    # Create a mock document object
    class MockDocument:
        def __init__(self):
            self.id = "demo-doc-123"
            self.file_name = "contract_agreement.pdf"
            self.file_type = "pdf"
            self.file_size = 1024000
            self.created_at = "2024-01-15T10:00:00Z"
    
    mock_document = MockDocument()
    
    # Perform different types of analysis
    print("🔍 Performing Analysis...")
    print("-" * 30)
    
    # 1. Summary Analysis
    print("1. 📊 Summary Analysis:")
    summary = await analysis_service._generate_summary(sample_text, mock_document)
    print(f"   Document Type: {summary['document_type']}")
    print(f"   Word Count: {summary['word_count']}")
    print(f"   Confidence: {summary['confidence_score']:.1%}")
    print(f"   Key Points: {len(summary['key_points'])} identified")
    print()
    
    # 2. Categorization
    print("2. 🏷️  Categorization:")
    categorization = await analysis_service._categorize_document(sample_text, mock_document)
    print(f"   Primary Category: {categorization['primary_category']}")
    print(f"   Confidence: {categorization['confidence']:.1%}")
    print(f"   Subcategories: {', '.join(categorization['subcategories'])}")
    print()
    
    # 3. Insights Extraction
    print("3. 🔍 Insights Extraction:")
    insights = await analysis_service._extract_insights(sample_text, mock_document)
    print(f"   Dates Found: {insights['entities']['dates']}")
    print(f"   Amounts Found: {insights['entities']['amounts']}")
    print(f"   People Found: {insights['entities']['people']}")
    print(f"   Organizations: {insights['entities']['organizations']}")
    print(f"   Risk Factors: {len(insights['risk_factors'])} identified")
    print(f"   Action Items: {len(insights['action_items'])} identified")
    print()
    
    # 4. Full Analysis
    print("4. 📋 Full Analysis Report:")
    full_analysis = await analysis_service._full_analysis(sample_text, mock_document)
    
    # Generate complete report
    report = await analysis_service._generate_report(mock_document, full_analysis, sample_text)
    
    print(f"   Report ID: {report['report_id']}")
    print(f"   Executive Summary: {report['executive_summary']}")
    print(f"   Risk Level: {report['risk_assessment']['overall_risk']}")
    print(f"   Risk Score: {report['risk_assessment']['risk_score']:.1%}")
    print(f"   Recommendations: {len(report['recommendations'])} provided")
    print()
    
    # 5. Show detailed recommendations
    print("5. 💡 Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"   {i}. {rec}")
    print()
    
    # 6. Show risk factors
    print("6. ⚠️  Risk Factors:")
    for i, risk in enumerate(report['risk_assessment']['risk_factors'], 1):
        print(f"   {i}. {risk}")
    print()
    
    print("=" * 50)
    print("✅ Analysis Complete!")
    print("\n🎯 This demonstrates the platform's ability to:")
    print("   • Extract and analyze document content")
    print("   • Categorize documents automatically")
    print("   • Identify key entities and insights")
    print("   • Assess risks and provide recommendations")
    print("   • Generate comprehensive reports")
    print("\n🚀 Ready for production use with real AI models!")

if __name__ == "__main__":
    asyncio.run(demo_analysis())
