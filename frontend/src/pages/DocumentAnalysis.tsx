import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
} from '@mui/material';
import {
  Description as DocumentIcon,
  Analytics as AnalyticsIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Assessment as ReportIcon,
  Category as CategoryIcon,
  Insights as InsightsIcon,
  Article as SummaryIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { documentApi } from '../services/api';

interface AnalysisResults {
  summary?: {
    word_count: number;
    key_points: string[];
    summary_text: string;
    document_type: string;
    confidence_score: number;
  };
  categorization?: {
    primary_category: string;
    category_scores: Record<string, number>;
    confidence: number;
    subcategories: string[];
  };
  insights?: {
    entities: {
      dates: string[];
      amounts: string[];
      people: string[];
      organizations: string[];
    };
    risk_factors: string[];
    action_items: string[];
  };
  analysis_metadata?: {
    analyzed_at: string;
    analysis_version: string;
    processing_time: string;
  };
}

interface DocumentReport {
  report_id: string;
  document_info: {
    id: string;
    name: string;
    type: string;
    size: number;
    uploaded_at: string;
  };
  analysis_results: AnalysisResults;
  executive_summary: string;
  recommendations: string[];
  risk_assessment: {
    overall_risk: string;
    risk_factors: string[];
    risk_score: number;
  };
  generated_at: string;
  report_version: string;
}

const DocumentAnalysis: React.FC = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const [document, setDocument] = useState<any>(null);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [report, setReport] = useState<DocumentReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (documentId) {
      fetchDocumentAnalysis();
    }
  }, [documentId]);

  const fetchDocumentAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const docId = parseInt(documentId!);
      if (isNaN(docId)) {
        throw new Error('Invalid document ID');
      }
      
      // Fetch document details
      const docResponse = await documentApi.getDocument(docId);
      setDocument(docResponse);
      
      // Fetch analysis results if available
      try {
        const analysisResponse = await documentApi.getDocumentAnalysis(docId);
        setAnalysisResults(analysisResponse.analysis_results);
        
        // Fetch full report
        const reportResponse = await documentApi.getDocumentReport(docId);
        setReport(reportResponse);
      } catch (analysisError) {
        // Analysis not available yet
        console.log('Analysis not available:', analysisError);
      }
    } catch (err) {
      setError('Failed to load document analysis');
      console.error('Error fetching document analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeDocument = async (analysisType: string = 'all') => {
    try {
      setAnalyzing(true);
      setError(null);
      
      const docId = parseInt(documentId!);
      if (isNaN(docId)) {
        throw new Error('Invalid document ID');
      }
      
      const response = await documentApi.analyzeDocument(docId.toString(), analysisType);
      
      if (response.success) {
        setReport(response.report);
        setAnalysisResults(response.report.analysis_results);
        // Refresh the page to show updated status
        await fetchDocumentAnalysis();
      }
    } catch (err) {
      setError('Failed to analyze document');
      console.error('Error analyzing document:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDownloadReport = async () => {
    try {
      const docId = parseInt(documentId!);
      if (isNaN(docId)) {
        throw new Error('Invalid document ID');
      }
      
      const response = await documentApi.getDocumentReport(docId, 'json');
      const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document-analysis-${documentId}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to download report');
      console.error('Error downloading report:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchDocumentAnalysis}>
          <RefreshIcon sx={{ mr: 1 }} />
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Document Analysis
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          AI-powered analysis and insights for your document
        </Typography>
      </Box>

      {/* Document Info */}
      {document && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <DocumentIcon sx={{ mr: 2, color: 'primary.main' }} />
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6" component="div">
                  {document.file_name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {document.file_type} • {Math.round(document.file_size / 1024)} KB
                </Typography>
              </Box>
              <Chip
                label={document.analysis_status || 'Not Analyzed'}
                color={getStatusColor(document.analysis_status || 'pending')}
                variant="outlined"
              />
            </Box>
            
            {!analysisResults && (
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  onClick={() => handleAnalyzeDocument('all')}
                  disabled={analyzing}
                  startIcon={analyzing ? <CircularProgress size={20} /> : <AnalyticsIcon />}
                >
                  {analyzing ? 'Analyzing...' : 'Analyze Document'}
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysisResults && (
        <>
          {/* Executive Summary */}
          {report && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ReportIcon sx={{ mr: 2, color: 'primary.main' }} />
                  <Typography variant="h6" component="div">
                    Executive Summary
                  </Typography>
                </Box>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {report.executive_summary}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <Chip
                    label={`Risk: ${report.risk_assessment.overall_risk}`}
                    color={getRiskColor(report.risk_assessment.overall_risk)}
                    variant="outlined"
                  />
                  <Chip
                    label={`Score: ${(report.risk_assessment.risk_score * 100).toFixed(0)}%`}
                    color="default"
                    variant="outlined"
                  />
                </Box>
                
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleDownloadReport}
                  sx={{ mt: 1 }}
                >
                  Download Report
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Analysis Sections */}
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {/* Summary */}
            {analysisResults.summary && (
              <Box sx={{ width: { xs: '100%', md: '50%' }, p: 1 }}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <SummaryIcon sx={{ mr: 2, color: 'primary.main' }} />
                      <Typography variant="h6" component="div">
                        Document Summary
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {analysisResults.summary.summary_text}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip label={`${analysisResults.summary.word_count} words`} size="small" />
                      <Chip label={analysisResults.summary.document_type} size="small" />
                      <Chip 
                        label={`${(analysisResults.summary.confidence_score * 100).toFixed(0)}% confidence`} 
                        size="small" 
                        color="success"
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            )}

            {/* Categorization */}
            {analysisResults.categorization && (
              <Box sx={{ width: { xs: '100%', md: '50%' }, p: 1 }}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <CategoryIcon sx={{ mr: 2, color: 'primary.main' }} />
                      <Typography variant="h6" component="div">
                        Document Category
                      </Typography>
                    </Box>
                    <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
                      {analysisResults.categorization.primary_category}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Confidence: {(analysisResults.categorization.confidence * 100).toFixed(0)}%
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {analysisResults.categorization.subcategories.map((sub, index) => (
                        <Chip key={index} label={sub} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            )}
          </Box>

          {/* Detailed Analysis */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                Detailed Analysis
              </Typography>
              
              {/* Key Points */}
              {analysisResults.summary?.key_points && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">Key Points</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List>
                      {analysisResults.summary.key_points.map((point, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <CheckIcon color="success" />
                          </ListItemIcon>
                          <ListItemText primary={point} />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Insights */}
              {analysisResults.insights && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">Extracted Insights</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                      {analysisResults.insights.entities.dates.length > 0 && (
                        <Box sx={{ width: { xs: '100%', sm: '48%' } }}>
                          <Typography variant="subtitle2" gutterBottom>Dates Found:</Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {analysisResults.insights.entities.dates.map((date, index) => (
                              <Chip key={index} label={date} size="small" />
                            ))}
                          </Box>
                        </Box>
                      )}
                      
                      {analysisResults.insights.entities.amounts.length > 0 && (
                        <Box sx={{ width: { xs: '100%', sm: '48%' } }}>
                          <Typography variant="subtitle2" gutterBottom>Amounts Found:</Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {analysisResults.insights.entities.amounts.map((amount, index) => (
                              <Chip key={index} label={amount} size="small" color="primary" />
                            ))}
                          </Box>
                        </Box>
                      )}

                      {analysisResults.insights.entities.people.length > 0 && (
                        <Box sx={{ width: { xs: '100%', sm: '48%' } }}>
                          <Typography variant="subtitle2" gutterBottom>People:</Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {analysisResults.insights.entities.people.map((person, index) => (
                              <Chip key={index} label={person} size="small" color="secondary" />
                            ))}
                          </Box>
                        </Box>
                      )}

                      {analysisResults.insights.entities.organizations.length > 0 && (
                        <Box sx={{ width: { xs: '100%', sm: '48%' } }}>
                          <Typography variant="subtitle2" gutterBottom>Organizations:</Typography>
                          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                            {analysisResults.insights.entities.organizations.map((org, index) => (
                              <Chip key={index} label={org} size="small" color="info" />
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Risk Factors */}
              {analysisResults.insights?.risk_factors && analysisResults.insights.risk_factors.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">Risk Factors</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List>
                      {analysisResults.insights.risk_factors.map((risk, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <ErrorIcon color="error" />
                          </ListItemIcon>
                          <ListItemText primary={risk} />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Action Items */}
              {analysisResults.insights?.action_items && analysisResults.insights.action_items.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">Action Items</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List>
                      {analysisResults.insights.action_items.map((item, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <CheckIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={item} />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              )}
            </CardContent>
          </Card>

          {/* Recommendations */}
          {report?.recommendations && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                  Recommendations
                </Typography>
                <List>
                  {report.recommendations.map((recommendation, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckIcon color="success" />
                      </ListItemIcon>
                      <ListItemText primary={recommendation} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {/* Back Button */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="outlined"
          onClick={() => navigate('/documents')}
          sx={{ mr: 2 }}
        >
          Back to Documents
        </Button>
        {analysisResults && (
          <Button
            variant="contained"
            onClick={() => handleAnalyzeDocument('all')}
            disabled={analyzing}
            startIcon={analyzing ? <CircularProgress size={20} /> : <RefreshIcon />}
          >
            {analyzing ? 'Re-analyzing...' : 'Re-analyze Document'}
          </Button>
        )}
      </Box>
    </Container>
  );
};

export default DocumentAnalysis;
