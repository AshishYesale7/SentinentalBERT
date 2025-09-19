import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { CheckCircle, Error, Memory, Speed } from '@mui/icons-material';
import { apiService, HealthResponse } from '../services/api';

const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const healthData = await apiService.getHealth();
        setHealth(healthData);
        setError(null);
      } catch (err) {
        setError('Failed to connect to NLP service');
        console.error('Health check failed:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        SentinelBERT Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Service Status */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                {health?.status === 'healthy' ? (
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                ) : (
                  <Error color="error" sx={{ mr: 1 }} />
                )}
                <Typography variant="h6">Service Status</Typography>
              </Box>
              <Chip
                label={health?.status || 'Unknown'}
                color={health?.status === 'healthy' ? 'success' : 'error'}
                variant="outlined"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Model Status */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Memory color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Model Status</Typography>
              </Box>
              <Chip
                label={health?.model_loaded ? 'Loaded' : 'Not Loaded'}
                color={health?.model_loaded ? 'success' : 'warning'}
                variant="outlined"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* GPU Status */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Speed color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6">GPU Status</Typography>
              </Box>
              <Chip
                label={health?.gpu_available ? 'Available' : 'CPU Only'}
                color={health?.gpu_available ? 'success' : 'default'}
                variant="outlined"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Active Requests */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Requests
              </Typography>
              <Typography variant="h3" color="primary">
                {health?.active_requests || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Usage */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Memory Usage
            </Typography>
            <Typography variant="h4" color="secondary">
              {health?.memory_usage_mb?.toFixed(1) || '0.0'} MB
            </Typography>
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <Typography variant="body2" color="text.secondary">
                • Navigate to Analysis page to test sentiment analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Check model performance and metrics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Monitor system health and resource usage
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* System Information */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Service Status
                </Typography>
                <Typography variant="body1">
                  {health?.status || 'Unknown'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Model Loaded
                </Typography>
                <Typography variant="body1">
                  {health?.model_loaded ? 'Yes' : 'No'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  GPU Available
                </Typography>
                <Typography variant="body1">
                  {health?.gpu_available ? 'Yes' : 'No'}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Memory Usage
                </Typography>
                <Typography variant="body1">
                  {health?.memory_usage_mb?.toFixed(1) || '0.0'} MB
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;