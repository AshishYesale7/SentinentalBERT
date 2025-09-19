import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { ExpandMore, Send, Psychology, TrendingUp } from '@mui/icons-material';
import { apiService, AnalysisResult, SentimentResult } from '../services/api';

const AnalysisPage: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const texts = inputText.split('\n').filter(text => text.trim());
      const response = await apiService.analyzeTexts(texts);
      setResults(response.results);
    } catch (err) {
      setError('Failed to analyze text. Please check if the NLP service is running.');
      console.error('Analysis failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: SentimentResult) => {
    if (sentiment.positive > sentiment.negative && sentiment.positive > sentiment.neutral) {
      return 'success';
    } else if (sentiment.negative > sentiment.positive && sentiment.negative > sentiment.neutral) {
      return 'error';
    } else {
      return 'default';
    }
  };

  const getSentimentLabel = (sentiment: SentimentResult) => {
    if (sentiment.positive > sentiment.negative && sentiment.positive > sentiment.neutral) {
      return 'Positive';
    } else if (sentiment.negative > sentiment.positive && sentiment.negative > sentiment.neutral) {
      return 'Negative';
    } else {
      return 'Neutral';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Text Analysis
      </Typography>

      {/* Input Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Enter Text for Analysis
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={6}
          variant="outlined"
          placeholder="Enter text to analyze (one text per line for batch analysis)..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Button
          variant="contained"
          startIcon={<Send />}
          onClick={handleAnalyze}
          disabled={loading || !inputText.trim()}
        >
          {loading ? 'Analyzing...' : 'Analyze Text'}
        </Button>
      </Paper>

      {/* Loading */}
      {loading && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            Analyzing text...
          </Typography>
          <LinearProgress />
        </Paper>
      )}

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {results.length > 0 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Analysis Results
          </Typography>
          
          {results.map((result, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Grid container spacing={2}>
                  {/* Sentiment Analysis */}
                  <Grid item xs={12} md={6}>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Psychology color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">Sentiment Analysis</Typography>
                    </Box>
                    
                    <Chip
                      label={getSentimentLabel(result.sentiment)}
                      color={getSentimentColor(result.sentiment) as any}
                      sx={{ mb: 2 }}
                    />
                    
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Positive: {(result.sentiment.positive * 100).toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={result.sentiment.positive * 100}
                        color="success"
                        sx={{ mb: 1 }}
                      />
                      
                      <Typography variant="body2" color="text.secondary">
                        Negative: {(result.sentiment.negative * 100).toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={result.sentiment.negative * 100}
                        color="error"
                        sx={{ mb: 1 }}
                      />
                      
                      <Typography variant="body2" color="text.secondary">
                        Neutral: {(result.sentiment.neutral * 100).toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={result.sentiment.neutral * 100}
                        sx={{ mb: 1 }}
                      />
                      
                      <Typography variant="body2" color="text.secondary">
                        Confidence: {(result.sentiment.confidence * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </Grid>

                  {/* Behavioral Patterns & Influence */}
                  <Grid item xs={12} md={6}>
                    <Box display="flex" alignItems="center" mb={2}>
                      <TrendingUp color="secondary" sx={{ mr: 1 }} />
                      <Typography variant="h6">Behavioral Analysis</Typography>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Influence Score: {result.influence_score.toFixed(3)}
                    </Typography>
                    
                    {result.behavioral_patterns.length > 0 ? (
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography>
                            Detected Patterns ({result.behavioral_patterns.length})
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <List dense>
                            {result.behavioral_patterns.map((pattern, patternIndex) => (
                              <ListItem key={patternIndex}>
                                <ListItemText
                                  primary={pattern.pattern_type}
                                  secondary={
                                    <Box>
                                      <Typography variant="body2">
                                        Score: {pattern.score.toFixed(3)} | 
                                        Confidence: {pattern.confidence.toFixed(3)}
                                      </Typography>
                                      <Typography variant="body2">
                                        Indicators: {pattern.indicators.join(', ')}
                                      </Typography>
                                    </Box>
                                  }
                                />
                              </ListItem>
                            ))}
                          </List>
                        </AccordionDetails>
                      </Accordion>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No behavioral patterns detected
                      </Typography>
                    )}
                  </Grid>

                  {/* Metadata */}
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Language: {result.language} | 
                      Processing Time: {result.processing_time_ms.toFixed(1)}ms
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default AnalysisPage;