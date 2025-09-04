"""
AI service for document analysis and insights
"""

import openai
from typing import Dict, Any, Optional
import json
import time
from datetime import datetime

from app.core.config import settings

class AIService:
    """Service for AI-powered document analysis"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            print("⚠️ OpenAI API key not configured. AI features will be limited.")
    
    async def analyze_document(
        self,
        document_id: int,
        analysis_type: str = "all",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a document using AI
        
        Args:
            document_id: ID of the document to analyze
            analysis_type: Type of analysis (summary, categorization, insights, all)
            custom_prompt: Custom prompt for analysis
        """
        
        # This would typically fetch the document from the database
        # For now, we'll simulate the analysis
        
        results = {
            "document_id": document_id,
            "analysis_type": analysis_type,
            "timestamp": datetime.utcnow().isoformat(),
            "results": {}
        }
        
        if analysis_type in ["summary", "all"]:
            results["results"]["summary"] = await self._generate_summary(document_id, custom_prompt)
        
        if analysis_type in ["categorization", "all"]:
            results["results"]["categorization"] = await self._categorize_document(document_id)
        
        if analysis_type in ["insights", "all"]:
            results["results"]["insights"] = await self._generate_insights(document_id)
        
        return results
    
    async def _generate_summary(self, document_id: int, custom_prompt: Optional[str] = None) -> str:
        """Generate a summary of the document"""
        
        if not settings.OPENAI_API_KEY:
            return "AI summary not available - OpenAI API key not configured"
        
        try:
            # This would fetch the extracted text from the database
            # For now, we'll simulate with a placeholder
            document_text = f"Document {document_id} content would be here..."
            
            prompt = custom_prompt or """
            Please provide a concise summary of the following document. 
            Focus on the main points, key information, and important details.
            Keep the summary under 200 words.
            
            Document content:
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
                    {"role": "user", "content": f"{prompt}\n\n{document_text}"}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    async def _categorize_document(self, document_id: int) -> Dict[str, Any]:
        """Categorize the document"""
        
        if not settings.OPENAI_API_KEY:
            return {
                "category": "Uncategorized",
                "confidence": 0.0,
                "reasoning": "AI categorization not available - OpenAI API key not configured"
            }
        
        try:
            # This would fetch the extracted text from the database
            document_text = f"Document {document_id} content would be here..."
            
            prompt = """
            Analyze the following document and categorize it. 
            Choose the most appropriate category from this list:
            - Business Document
            - Legal Document
            - Technical Document
            - Financial Document
            - Personal Document
            - Academic Document
            - Medical Document
            - Other
            
            Provide your response in JSON format with:
            - category: the chosen category
            - confidence: confidence score (0.0 to 1.0)
            - reasoning: brief explanation of why this category was chosen
            
            Document content:
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes documents. Always respond with valid JSON."},
                    {"role": "user", "content": f"{prompt}\n\n{document_text}"}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            return {
                "category": "Uncategorized",
                "confidence": 0.0,
                "reasoning": f"Error categorizing document: {str(e)}"
            }
    
    async def _generate_insights(self, document_id: int) -> Dict[str, Any]:
        """Generate insights about the document"""
        
        if not settings.OPENAI_API_KEY:
            return {
                "key_points": [],
                "sentiment": "neutral",
                "entities": [],
                "recommendations": ["AI insights not available - OpenAI API key not configured"]
            }
        
        try:
            # This would fetch the extracted text from the database
            document_text = f"Document {document_id} content would be here..."
            
            prompt = """
            Analyze the following document and provide insights in JSON format:
            - key_points: array of 3-5 most important points
            - sentiment: overall sentiment (positive, negative, neutral)
            - entities: array of important entities (people, organizations, locations, etc.)
            - recommendations: array of actionable recommendations based on the content
            
            Document content:
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes documents and provides insights. Always respond with valid JSON."},
                    {"role": "user", "content": f"{prompt}\n\n{document_text}"}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            return {
                "key_points": [],
                "sentiment": "neutral",
                "entities": [],
                "recommendations": [f"Error generating insights: {str(e)}"]
            }
    
    async def extract_entities(self, text: str) -> Dict[str, list]:
        """Extract named entities from text"""
        
        if not settings.OPENAI_API_KEY:
            return {"people": [], "organizations": [], "locations": [], "dates": []}
        
        try:
            prompt = f"""
            Extract named entities from the following text and return them in JSON format:
            - people: array of person names
            - organizations: array of organization names
            - locations: array of location names
            - dates: array of dates mentioned
            
            Text:
            {text}
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts named entities. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            return {
                "people": [],
                "organizations": [],
                "locations": [],
                "dates": []
            }
    
    async def generate_tags(self, text: str, max_tags: int = 10) -> list:
        """Generate relevant tags for the document"""
        
        if not settings.OPENAI_API_KEY:
            return ["ai-tags-not-available"]
        
        try:
            prompt = f"""
            Generate {max_tags} relevant tags for the following text.
            Return only a JSON array of tag strings, no other text.
            
            Text:
            {text[:1000]}  # Limit text length
            """
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates tags. Always respond with only a JSON array of strings."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result[:max_tags]
            
        except Exception as e:
            return ["error-generating-tags"]
