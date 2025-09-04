import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Button,
  Chip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckIcon,
  Description as DocumentIcon,
} from '@mui/icons-material';
import { documentApi, AnalyticsResponse } from '../services/api';

const Analytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await documentApi.getAnalytics();
      setAnalytics(data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    subtitle: string;
    icon: React.ReactNode;
    color: string;
    trend?: string;
  }> = ({ title, value, subtitle, icon, color, trend }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: 2,
              p: 1.5,
              mr: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 'medium' }}>
              {title}
            </Typography>
            {trend && (
              <Chip
                label={trend}
                size="small"
                color="success"
                variant="outlined"
                sx={{ mt: 0.5 }}
              />
            )}
          </Box>
        </Box>
        <Typography variant="h3" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      </CardContent>
    </Card>
  );

  const PerformanceCard: React.FC<{
    title: string;
    value: number;
    max: number;
    unit: string;
    color: string;
  }> = ({ title, value, max, unit, color }) => (
    <Card>
      <CardContent>
        <Typography variant="h6" component="div" gutterBottom>
          {title}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mr: 1 }}>
            {value}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {unit}
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={(value / max) * 100}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: 'rgba(0,0,0,0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: color,
            },
          }}
        />
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          {((value / max) * 100).toFixed(1)}% of target
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <LinearProgress />
          <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
            Loading analytics...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error" action={
            <Button color="inherit" size="small" onClick={fetchAnalytics}>
              Retry
            </Button>
          }>
            {error}
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            📊 Analytics
          </Typography>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchAnalytics}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
        <Typography variant="subtitle1" color="text.secondary">
          Monitor your document processing performance and insights
        </Typography>
      </Box>

      {/* Key Metrics */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <MetricCard
            title="Total Documents"
            value={analytics?.total_documents || 0}
            subtitle="Documents processed"
            icon={<DocumentIcon sx={{ color: 'white' }} />}
            color="#1976d2"
            trend="+12% this month"
          />
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <MetricCard
            title="Success Rate"
            value={`${analytics?.processing_rate || 0}%`}
            subtitle="Processing efficiency"
            icon={<CheckIcon sx={{ color: 'white' }} />}
            color="#2e7d32"
            trend="Excellent"
          />
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <MetricCard
            title="Avg. Processing Time"
            value={`${analytics?.average_processing_time || 0}s`}
            subtitle="Speed performance"
            icon={<SpeedIcon sx={{ color: 'white' }} />}
            color="#ed6c02"
            trend="Fast"
          />
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <MetricCard
            title="System Status"
            value={analytics?.status || 'Unknown'}
            subtitle="Platform health"
            icon={<TrendingUpIcon sx={{ color: 'white' }} />}
            color={analytics?.status === 'operational' ? '#2e7d32' : '#d32f2f'}
          />
        </Box>
      </Box>

      {/* Performance Charts */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
          <PerformanceCard
            title="Processing Success Rate"
            value={analytics?.processing_rate || 0}
            max={100}
            unit="%"
            color="#2e7d32"
          />
        </Box>
        <Box sx={{ flex: '1 1 400px', minWidth: '400px' }}>
          <PerformanceCard
            title="Average Processing Speed"
            value={analytics?.average_processing_time || 0}
            max={10}
            unit="seconds"
            color="#1976d2"
          />
        </Box>
      </Box>

      {/* System Status */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" component="div" gutterBottom>
            🚀 System Performance
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Document Processing</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                  {analytics?.processed_documents || 0} / {analytics?.total_documents || 0}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={analytics?.total_documents ? (analytics.processed_documents / analytics.total_documents) * 100 : 0}
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>
            <Box sx={{ flex: '1 1 300px', minWidth: '300px' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">System Health</Typography>
                <Chip
                  label={analytics?.status || 'Unknown'}
                  color={analytics?.status === 'operational' ? 'success' : 'error'}
                  size="small"
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                All systems operational and ready for document processing
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Insights */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" component="div" gutterBottom>
            💡 Insights & Recommendations
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ p: 2, backgroundColor: '#e3f2fd', borderRadius: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 'medium', mb: 1 }}>
                📈 Performance Summary
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Your document processing platform is performing excellently with a {analytics?.processing_rate || 0}% success rate 
                and an average processing time of {analytics?.average_processing_time || 0} seconds.
              </Typography>
            </Box>
            <Box sx={{ p: 2, backgroundColor: '#f3e5f5', borderRadius: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 'medium', mb: 1 }}>
                🎯 Optimization Tips
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Consider batch processing for multiple documents to improve efficiency
                • Monitor file sizes to optimize processing times
                • Regular system maintenance ensures consistent performance
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default Analytics;
