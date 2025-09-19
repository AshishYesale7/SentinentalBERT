import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box, Button } from '@mui/material';
import Dashboard from './pages/Dashboard';
import AnalysisPage from './pages/AnalysisPage';

const Navigation = () => {
  const location = useLocation();
  
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          SentinelBERT Dashboard
        </Typography>
        <Button 
          color="inherit" 
          component={Link} 
          to="/"
          variant={location.pathname === '/' ? 'outlined' : 'text'}
        >
          Dashboard
        </Button>
        <Button 
          color="inherit" 
          component={Link} 
          to="/analysis"
          variant={location.pathname === '/analysis' ? 'outlined' : 'text'}
          sx={{ ml: 1 }}
        >
          Analysis
        </Button>
      </Toolbar>
    </AppBar>
  );
};

function App() {
  return (
    <Router>
      <Box sx={{ flexGrow: 1 }}>
        <Navigation />
        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<AnalysisPage />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
}

export default App;