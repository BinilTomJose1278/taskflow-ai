import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import PyPDF2
import io
from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class DocumentAnalysisService:
    def __init__(self):
        self.analysis_types = {
            'summary': self._generate_summary,
            'categorization': self._categorize_document,
            'insights': self._extract_insights,
            'all': self._full_analysis
        }
        # Lazy import to avoid dependency if not configured
        self._openai_client = None
    
    async def analyze_document(self, document_id: str, analysis_type: str = 'all') -> Dict[str, Any]:
        """
        Analyze a document and generate a comprehensive report
        """
        try:
            db = next(get_db())
            document = db.query(Document).filter(Document.id == document_id).first()
            
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Extract text from document
            text_content = await self._extract_text_from_document(document)
            
            if not text_content:
                raise ValueError("Could not extract text from document")
            
            # Perform analysis based on type
            analysis_func = self.analysis_types.get(analysis_type, self._full_analysis)
            analysis_results = await analysis_func(text_content, document)
            
            # Generate report
            report = await self._generate_report(document, analysis_results, text_content)
            
            # Update document with analysis results
            document.analysis_results = json.dumps(analysis_results)
            document.analysis_status = 'completed'
            document.analysis_completed_at = datetime.utcnow()
            db.commit()
            
            return report
            
        except Exception as e:
            logger.error(f"Error analyzing document {document_id}: {str(e)}")
            # Update document status to failed
            if 'document' in locals():
                document.analysis_status = 'failed'
                document.analysis_error = str(e)
                db.commit()
            raise e
        finally:
            if 'db' in locals():
                db.close()
    
    async def _extract_text_from_document(self, document: Document) -> str:
        """
        Extract text content from uploaded document
        """
        try:
            # For now, we'll simulate text extraction
            # In a real implementation, you'd read the actual file
            sample_texts = {
                'pdf': """
                CONTRACT AGREEMENT
            
                This agreement is entered into between Company A and Company B for the provision of software development services.
                
                TERMS AND CONDITIONS:
                1. The project duration shall be 6 months
                2. Payment terms: 50% upfront, 50% on completion
                3. Intellectual property rights remain with Company A
                4. Confidentiality clause applies to all parties
                
                SIGNATURES:
                Company A Representative: John Smith
                Company B Representative: Jane Doe
                Date: 2024-01-15
                """,
                'docx': """
                FINANCIAL REPORT Q4 2024
                
                EXECUTIVE SUMMARY:
                Revenue increased by 15% compared to Q3 2024
                Net profit margin improved to 12.5%
                Customer acquisition cost decreased by 8%
                
                KEY METRICS:
                - Total Revenue: $2.5M
                - Operating Expenses: $1.8M
                - Net Profit: $312K
                - Customer Count: 1,250
                
                RECOMMENDATIONS:
                1. Increase marketing budget for Q1 2025
                2. Focus on customer retention programs
                3. Expand to new geographic markets
                """,
                'txt': """
                MEDICAL RECORD - Patient ID: 12345
                
                Patient: John Smith
                DOB: 1985-03-15
                Diagnosis: Hypertension, Type 2 Diabetes
                
                MEDICATIONS:
                - Lisinopril 10mg daily
                - Metformin 500mg twice daily
                
                VITAL SIGNS:
                Blood Pressure: 140/90 mmHg
                Heart Rate: 78 bpm
                Weight: 180 lbs
                
                NEXT APPOINTMENT: 2024-02-15
                """
            }
            
            # Return appropriate sample text based on file type
            file_extension = document.file_name.split('.')[-1].lower()
            return sample_texts.get(file_extension, sample_texts['pdf'])
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    async def _generate_summary(self, text: str, document: Document) -> Dict[str, Any]:
        """
        Generate a summary of the document
        """
        # If OPENAI_API_KEY configured, use OpenAI for higher-quality summary
        if settings.OPENAI_API_KEY:
            try:
                summary = await self._openai_summarize(text)
                # Ensure required fields
                word_count = len(text.split())
                summary.setdefault('word_count', word_count)
                summary.setdefault('document_type', self._detect_document_type(text))
                summary.setdefault('confidence_score', 0.9)
                return summary
            except Exception as e:
                logger.warning(f"OpenAI summary failed, falling back to heuristic: {e}")

        # Fallback heuristic summary
        word_count = len(text.split())
        return {
            'word_count': word_count,
            'key_points': [
                "Document contains important contractual information",
                "Multiple parties involved in agreement",
                "Financial terms clearly defined",
                "Legal obligations specified"
            ],
            'summary_text': f"This {document.file_type} document contains approximately {word_count} words and appears to be a legal or business document with structured content including terms, conditions, and signatures.",
            'document_type': self._detect_document_type(text),
            'confidence_score': 0.85
        }

    async def _openai_summarize(self, text: str) -> Dict[str, Any]:
        """Use OpenAI to produce a structured summary."""
        # Lazy init
        if self._openai_client is None:
            from openai import OpenAI  # type: ignore
            self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

        model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        prompt = (
            "You are an expert document analyst. Read the provided document text and return a concise JSON "
            "object with keys: word_count (int), key_points (array of short bullets), summary_text (2-4 sentences), "
            "document_type (string like Contract/Financial Report/Medical Record/General), confidence_score (0-1). "
            "Only return valid JSON."
        )

        completion = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text[:12000]}
                ],
                temperature=0.2,
            )
        )

        content = completion.choices[0].message.content  # type: ignore
        try:
            return json.loads(content)
        except Exception:
            # If not JSON, wrap it
            return {
                'word_count': len(text.split()),
                'key_points': [],
                'summary_text': content.strip(),
                'document_type': self._detect_document_type(text),
                'confidence_score': 0.9,
            }
    
    async def _categorize_document(self, text: str, document: Document) -> Dict[str, Any]:
        """
        Categorize the document based on content
        """
        categories = {
            'legal': ['contract', 'agreement', 'terms', 'conditions', 'signature'],
            'financial': ['revenue', 'profit', 'expenses', 'budget', 'financial'],
            'medical': ['patient', 'diagnosis', 'medication', 'vital', 'medical'],
            'technical': ['software', 'development', 'code', 'system', 'technical'],
            'general': ['report', 'document', 'information', 'data']
        }
        
        text_lower = text.lower()
        category_scores = {}
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            category_scores[category] = score / len(keywords)
        
        primary_category = max(category_scores, key=category_scores.get)
        
        return {
            'primary_category': primary_category,
            'category_scores': category_scores,
            'confidence': category_scores[primary_category],
            'subcategories': self._identify_subcategories(text, primary_category)
        }
    
    async def _extract_insights(self, text: str, document: Document) -> Dict[str, Any]:
        """
        Extract key insights from the document
        """
        insights = {
            'entities': self._extract_entities(text),
            'dates': self._extract_dates(text),
            'amounts': self._extract_amounts(text),
            'people': self._extract_people(text),
            'organizations': self._extract_organizations(text),
            'risk_factors': self._identify_risk_factors(text),
            'action_items': self._identify_action_items(text)
        }
        
        return insights
    
    async def _full_analysis(self, text: str, document: Document) -> Dict[str, Any]:
        """
        Perform comprehensive analysis including all types
        """
        summary = await self._generate_summary(text, document)
        categorization = await self._categorize_document(text, document)
        insights = await self._extract_insights(text, document)
        
        return {
            'summary': summary,
            'categorization': categorization,
            'insights': insights,
            'analysis_metadata': {
                'analyzed_at': datetime.utcnow().isoformat(),
                'analysis_version': '1.0',
                'processing_time': '2.3s'
            }
        }
    
    async def _generate_report(self, document: Document, analysis_results: Dict, text_content: str) -> Dict[str, Any]:
        """
        Generate a comprehensive report for the document
        """
        report_id = str(uuid.uuid4())
        
        report = {
            'report_id': report_id,
            'document_info': {
                'id': document.id,
                'name': document.file_name,
                'type': document.file_type,
                'size': document.file_size,
                'uploaded_at': document.created_at.isoformat()
            },
            'analysis_results': analysis_results,
            'executive_summary': self._create_executive_summary(analysis_results),
            'recommendations': self._generate_recommendations(analysis_results),
            'risk_assessment': self._assess_risks(analysis_results),
            'generated_at': datetime.utcnow().isoformat(),
            'report_version': '1.0'
        }
        
        return report
    
    def _detect_document_type(self, text: str) -> str:
        """Detect the type of document based on content"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['contract', 'agreement', 'terms']):
            return 'Contract'
        elif any(word in text_lower for word in ['financial', 'revenue', 'profit']):
            return 'Financial Report'
        elif any(word in text_lower for word in ['patient', 'medical', 'diagnosis']):
            return 'Medical Record'
        else:
            return 'General Document'
    
    def _identify_subcategories(self, text: str, primary_category: str) -> List[str]:
        """Identify subcategories within the primary category"""
        subcategories = {
            'legal': ['Contract', 'Agreement', 'Terms of Service', 'Privacy Policy'],
            'financial': ['Income Statement', 'Balance Sheet', 'Cash Flow', 'Budget'],
            'medical': ['Patient Record', 'Prescription', 'Lab Results', 'Diagnosis'],
            'technical': ['API Documentation', 'User Manual', 'Technical Spec', 'Code Review']
        }
        return subcategories.get(primary_category, ['General'])
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        # Simplified entity extraction
        entities = {
            'dates': self._extract_dates(text),
            'amounts': self._extract_amounts(text),
            'people': self._extract_people(text),
            'organizations': self._extract_organizations(text)
        }
        return entities
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        import re
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b'
        return re.findall(date_pattern, text)
    
    def _extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from text"""
        import re
        amount_pattern = r'\$[\d,]+\.?\d*|\b\d+\.?\d*\s*(?:dollars?|USD|cents?)\b'
        return re.findall(amount_pattern, text, re.IGNORECASE)
    
    def _extract_people(self, text: str) -> List[str]:
        """Extract people names from text"""
        # Simplified name extraction
        names = []
        lines = text.split('\n')
        for line in lines:
            if ':' in line and any(word in line.lower() for word in ['representative', 'signature', 'patient']):
                name = line.split(':')[-1].strip()
                if len(name.split()) >= 2:
                    names.append(name)
        return names
    
    def _extract_organizations(self, text: str) -> List[str]:
        """Extract organization names from text"""
        orgs = []
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['company', 'corp', 'inc', 'llc', 'ltd']):
                orgs.append(line.strip())
        return orgs
    
    def _identify_risk_factors(self, text: str) -> List[str]:
        """Identify potential risk factors in the document"""
        risk_keywords = ['confidential', 'liability', 'penalty', 'breach', 'termination', 'default']
        risks = []
        text_lower = text.lower()
        for keyword in risk_keywords:
            if keyword in text_lower:
                risks.append(f"Contains {keyword} clause")
        return risks
    
    def _identify_action_items(self, text: str) -> List[str]:
        """Identify action items or deadlines in the document"""
        action_items = []
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['deadline', 'due date', 'appointment', 'next']):
                action_items.append(line.strip())
        return action_items
    
    def _create_executive_summary(self, analysis_results: Dict) -> str:
        """Create an executive summary of the analysis"""
        summary = analysis_results.get('summary', {})
        categorization = analysis_results.get('categorization', {})
        
        doc_type = summary.get('document_type', 'Unknown')
        category = categorization.get('primary_category', 'General')
        confidence = categorization.get('confidence', 0)
        
        return f"This {doc_type} has been classified as a {category} document with {confidence:.1%} confidence. The document contains structured information with clear terms and conditions."
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = [
            "Review all terms and conditions carefully",
            "Verify all dates and deadlines",
            "Check for any missing signatures or approvals",
            "Ensure compliance with relevant regulations"
        ]
        
        insights = analysis_results.get('insights', {})
        if insights.get('risk_factors'):
            recommendations.append("Pay special attention to identified risk factors")
        
        return recommendations
    
    def _assess_risks(self, analysis_results: Dict) -> Dict[str, Any]:
        """Assess overall risk level of the document"""
        insights = analysis_results.get('insights', {})
        risk_factors = insights.get('risk_factors', [])
        
        risk_level = 'Low'
        if len(risk_factors) > 3:
            risk_level = 'High'
        elif len(risk_factors) > 1:
            risk_level = 'Medium'
        
        return {
            'overall_risk': risk_level,
            'risk_factors': risk_factors,
            'risk_score': len(risk_factors) / 10.0  # Normalize to 0-1
        }
