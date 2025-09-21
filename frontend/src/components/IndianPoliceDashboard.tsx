import React, { useState, useContext, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  AppBar,
  Toolbar,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  LocationOn as LocationIcon,
  Timeline as TimelineIcon,
  Security as SecurityIcon,
  Language as LanguageIcon,
  AccountCircle as AccountIcon,
  Notifications as NotificationsIcon,
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  Gavel as GavelIcon,
  Map as MapIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

// Indian Government Theme
const indianGovTheme = createTheme({
  palette: {
    primary: {
      main: '#FF6600', // Saffron
      light: '#FF9933',
      dark: '#CC5200'
    },
    secondary: {
      main: '#138808', // Green
      light: '#4CAF50',
      dark: '#0F5D06'
    },
    background: {
      default: '#F5F5F5',
      paper: '#FFFFFF'
    },
    text: {
      primary: '#1A1A1A',
      secondary: '#666666'
    }
  },
  typography: {
    fontFamily: '"Noto Sans Devanagari", "Roboto", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: '#1A1A1A'
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      color: '#1A1A1A'
    },
    h6: {
      fontWeight: 600
    }
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(90deg, #FF6600 0%, #FFFFFF 50%, #138808 100%)',
          color: '#1A1A1A',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }
      }
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: '8px'
        }
      }
    }
  }
});

// Language Context
interface LanguageContextType {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
}

const LanguageContext = React.createContext<LanguageContextType | null>(null);

// Translations
const translations = {
  'hi': {
    'dashboard.title': 'इनसाइडआउट डैशबोर्ड',
    'search.placeholder': 'खोजने के लिए कीवर्ड दर्ज करें',
    'viral.content': 'वायरल सामग्री',
    'evidence.management': 'साक्ष्य प्रबंधन',
    'case.details': 'मामले का विवरण',
    'geographic.distribution': 'भौगोलिक वितरण',
    'influence.network': 'प्रभाव नेटवर्क',
    'timeline.analysis': 'समयरेखा विश्लेषण',
    'search.button': 'खोजें',
    'filter.platform': 'प्लेटफॉर्म',
    'filter.daterange': 'दिनांक सीमा',
    'filter.location': 'स्थान',
    'viral.score': 'वायरल स्कोर',
    'original.source': 'मूल स्रोत',
    'propagation.chain': 'प्रसार श्रृंखला',
    'evidence.collected': 'साक्ष्य एकत्रित',
    'warrant.required': 'वारंट आवश्यक',
    'officer.name': 'अधिकारी का नाम',
    'case.number': 'मामला संख्या',
    'collect.evidence': 'साक्ष्य एकत्रित करें',
    'view.details': 'विवरण देखें',
    'high.priority': 'उच्च प्राथमिकता',
    'medium.priority': 'मध्यम प्राथमिकता',
    'low.priority': 'कम प्राथमिकता'
  },
  'en': {
    'dashboard.title': 'InsideOut Dashboard',
    'search.placeholder': 'Enter keywords to search',
    'viral.content': 'Viral Content',
    'evidence.management': 'Evidence Management',
    'case.details': 'Case Details',
    'geographic.distribution': 'Geographic Distribution',
    'influence.network': 'Influence Network',
    'timeline.analysis': 'Timeline Analysis',
    'search.button': 'Search',
    'filter.platform': 'Platform',
    'filter.daterange': 'Date Range',
    'filter.location': 'Location',
    'viral.score': 'Viral Score',
    'original.source': 'Original Source',
    'propagation.chain': 'Propagation Chain',
    'evidence.collected': 'Evidence Collected',
    'warrant.required': 'Warrant Required',
    'officer.name': 'Officer Name',
    'case.number': 'Case Number',
    'collect.evidence': 'Collect Evidence',
    'view.details': 'View Details',
    'high.priority': 'High Priority',
    'medium.priority': 'Medium Priority',
    'low.priority': 'Low Priority'
  },
  'ta': {
    'dashboard.title': 'இன்சைட்அவுட் டாஷ்போர்டு',
    'search.placeholder': 'தேடுவதற்கு முக்கிய வார்த்தைகளை உள்ளிடவும்',
    'viral.content': 'வைரல் உள்ளடக்கம்',
    'evidence.management': 'சாட்சிய மேலாண்மை',
    'case.details': 'வழக்கு விவரங்கள்',
    'geographic.distribution': 'புவியியல் விநியோகம்',
    'influence.network': 'செல்வாக்கு வலையமைப்பு',
    'timeline.analysis': 'காலவரிசை பகுப்பாய்வு',
    'search.button': 'தேடு',
    'filter.platform': 'தளம்',
    'filter.daterange': 'தேதி வரம்பு',
    'filter.location': 'இடம்',
    'viral.score': 'வைரல் மதிப்பெண்',
    'original.source': 'அசல் மூலம்',
    'propagation.chain': 'பரவல் சங்கிலி',
    'evidence.collected': 'சாட்சியம் சேகரிக்கப்பட்டது',
    'warrant.required': 'வாரண்ட் தேவை',
    'officer.name': 'அதிகாரி பெயர்',
    'case.number': 'வழக்கு எண்',
    'collect.evidence': 'சாட்சியம் சேகரிக்கவும்',
    'view.details': 'விவரங்களைப் பார்க்கவும்',
    'high.priority': 'அதிக முன்னுரிமை',
    'medium.priority': 'நடுத்தர முன்னுரிமை',
    'low.priority': 'குறைந்த முன்னுரிமை'
  }
};

// Language Provider Component
export const LanguageProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [language, setLanguage] = useState('hi'); // Default to Hindi
  
  const t = (key: string): string => {
    return translations[language]?.[key] || key;
  };
  
  return (
    <LanguageContext.Provider value={{language, setLanguage, t}}>
      {children}
    </LanguageContext.Provider>
  );
};

// Language Selector Component
const LanguageSelector: React.FC = () => {
  const {language, setLanguage} = useContext(LanguageContext)!;
  
  return (
    <FormControl size="small" sx={{minWidth: 120, mr: 2}}>
      <Select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        sx={{color: 'inherit'}}
      >
        <MenuItem value="hi">हिंदी</MenuItem>
        <MenuItem value="en">English</MenuItem>
        <MenuItem value="ta">தமிழ்</MenuItem>
      </Select>
    </FormControl>
  );
};

// Officer Profile Component
const OfficerProfile: React.FC = () => {
  const {t} = useContext(LanguageContext)!;
  
  return (
    <Box sx={{display: 'flex', alignItems: 'center'}}>
      <IconButton color="inherit">
        <Badge badgeContent={3} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>
      <Avatar sx={{ml: 1, bgcolor: 'primary.main'}}>
        <AccountIcon />
      </Avatar>
      <Typography variant="body2" sx={{ml: 1}}>
        Inspector Sharma
      </Typography>
    </Box>
  );
};

// Search and Filters Component
const SearchAndFilters: React.FC = () => {
  const {t} = useContext(LanguageContext)!;
  const [searchQuery, setSearchQuery] = useState('');
  const [platform, setPlatform] = useState('all');
  const [dateRange, setDateRange] = useState('7d');
  const [location, setLocation] = useState('all');
  
  return (
    <Box>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            placeholder={t('search.placeholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{mr: 1, color: 'text.secondary'}} />
            }}
          />
        </Grid>
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>{t('filter.platform')}</InputLabel>
            <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
              <MenuItem value="all">All Platforms</MenuItem>
              <MenuItem value="twitter">Twitter/X</MenuItem>
              <MenuItem value="facebook">Facebook</MenuItem>
              <MenuItem value="instagram">Instagram</MenuItem>
              <MenuItem value="youtube">YouTube</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>{t('filter.daterange')}</InputLabel>
            <Select value={dateRange} onChange={(e) => setDateRange(e.target.value)}>
              <MenuItem value="1d">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>{t('filter.location')}</InputLabel>
            <Select value={location} onChange={(e) => setLocation(e.target.value)}>
              <MenuItem value="all">All India</MenuItem>
              <MenuItem value="delhi">Delhi</MenuItem>
              <MenuItem value="mumbai">Mumbai</MenuItem>
              <MenuItem value="bangalore">Bangalore</MenuItem>
              <MenuItem value="chennai">Chennai</MenuItem>
              <MenuItem value="kolkata">Kolkata</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={2}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<SearchIcon />}
            sx={{height: '56px'}}
          >
            {t('search.button')}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

// Viral Content Timeline Component
const ViralContentTimeline: React.FC<{content: any[]}> = ({content}) => {
  const {t} = useContext(LanguageContext)!;
  
  // Mock data for demonstration
  const mockViralContent = [
    {
      id: '1',
      content: 'Breaking: Major political announcement creates social media storm',
      originalSource: '@news_channel',
      viralScore: 8.5,
      propagationCount: 15420,
      platforms: ['Twitter', 'Facebook', 'Instagram'],
      timestamp: '2024-01-15T10:30:00Z',
      priority: 'high',
      evidenceCollected: false
    },
    {
      id: '2',
      content: 'Viral video of traffic incident spreads across platforms',
      originalSource: '@citizen_reporter',
      viralScore: 6.2,
      propagationCount: 8930,
      platforms: ['Instagram', 'YouTube', 'Twitter'],
      timestamp: '2024-01-15T08:15:00Z',
      priority: 'medium',
      evidenceCollected: true
    },
    {
      id: '3',
      content: 'Misinformation about government policy circulating',
      originalSource: '@anonymous_account',
      viralScore: 7.8,
      propagationCount: 12340,
      platforms: ['Facebook', 'WhatsApp', 'Twitter'],
      timestamp: '2024-01-15T06:45:00Z',
      priority: 'high',
      evidenceCollected: false
    }
  ];
  
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };
  
  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return t('high.priority');
      case 'medium': return t('medium.priority');
      case 'low': return t('low.priority');
      default: return priority;
    }
  };
  
  return (
    <Box sx={{height: '100%', overflow: 'auto'}}>
      <List>
        {mockViralContent.map((item, index) => (
          <React.Fragment key={item.id}>
            <ListItem alignItems="flex-start">
              <ListItemAvatar>
                <Avatar sx={{bgcolor: getPriorityColor(item.priority) + '.main'}}>
                  <TrendingUpIcon />
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{display: 'flex', alignItems: 'center', mb: 1}}>
                    <Typography variant="subtitle1" sx={{flexGrow: 1}}>
                      {item.content}
                    </Typography>
                    <Chip
                      label={getPriorityText(item.priority)}
                      color={getPriorityColor(item.priority)}
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {t('original.source')}: {item.originalSource}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {t('viral.score')}: {item.viralScore}/10 | {t('propagation.chain')}: {item.propagationCount.toLocaleString()}
                    </Typography>
                    <Box sx={{display: 'flex', alignItems: 'center', mt: 1}}>
                      {item.platforms.map((platform) => (
                        <Chip
                          key={platform}
                          label={platform}
                          size="small"
                          variant="outlined"
                          sx={{mr: 0.5}}
                        />
                      ))}
                      {item.evidenceCollected ? (
                        <Chip
                          icon={<CheckCircleIcon />}
                          label={t('evidence.collected')}
                          color="success"
                          size="small"
                          sx={{ml: 1}}
                        />
                      ) : (
                        <Chip
                          icon={<WarningIcon />}
                          label={t('warrant.required')}
                          color="warning"
                          size="small"
                          sx={{ml: 1}}
                        />
                      )}
                    </Box>
                    <Box sx={{mt: 1}}>
                      <Button size="small" startIcon={<GavelIcon />}>
                        {t('collect.evidence')}
                      </Button>
                      <Button size="small" sx={{ml: 1}}>
                        {t('view.details')}
                      </Button>
                    </Box>
                  </Box>
                }
              />
            </ListItem>
            {index < mockViralContent.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );
};

// Evidence Management Panel Component
const EvidenceManagementPanel: React.FC = () => {
  const {t} = useContext(LanguageContext)!;
  const [openDialog, setOpenDialog] = useState(false);
  
  // Mock evidence data
  const evidenceData = [
    {
      id: 'EC-20240115-001',
      caseNumber: 'FIR-2024-001',
      officerName: 'Inspector Sharma',
      collectionDate: '2024-01-15',
      itemCount: 15,
      status: 'collected',
      warrantId: 'WRT-2024-001'
    },
    {
      id: 'EC-20240114-002',
      caseNumber: 'FIR-2024-002',
      officerName: 'Sub-Inspector Patel',
      collectionDate: '2024-01-14',
      itemCount: 8,
      status: 'analyzed',
      warrantId: 'WRT-2024-002'
    }
  ];
  
  return (
    <Box>
      <Grid container spacing={2}>
        {evidenceData.map((evidence) => (
          <Grid item xs={12} md={6} key={evidence.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {evidence.id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('case.number')}: {evidence.caseNumber}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('officer.name')}: {evidence.officerName}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Items: {evidence.itemCount}
                </Typography>
                <Chip
                  label={evidence.status}
                  color={evidence.status === 'collected' ? 'primary' : 'success'}
                  size="small"
                  sx={{mt: 1}}
                />
              </CardContent>
              <CardActions>
                <Button size="small">{t('view.details')}</Button>
                <Button size="small" startIcon={<SecurityIcon />}>
                  Verify Chain
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      <Button
        variant="contained"
        startIcon={<GavelIcon />}
        sx={{mt: 2}}
        onClick={() => setOpenDialog(true)}
      >
        {t('collect.evidence')}
      </Button>
      
      {/* Evidence Collection Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{t('collect.evidence')}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{mt: 1}}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Warrant ID"
                placeholder="WRT-2024-XXX"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('case.number')}
                placeholder="FIR-2024-XXX"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Content IDs (comma separated)"
                placeholder="post_123, post_456, post_789"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<SecurityIcon />}>
            Collect with Legal Authority
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Main Dashboard Component
export const IndianPoliceDashboard: React.FC = () => {
  const {t} = useContext(LanguageContext)!;
  const [selectedCase, setSelectedCase] = useState<string | null>(null);
  const [viralContent, setViralContent] = useState<any[]>([]);
  
  return (
    <ThemeProvider theme={indianGovTheme}>
      <Box sx={{display: 'flex', flexDirection: 'column', minHeight: '100vh'}}>
        {/* Government Header */}
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <Box sx={{display: 'flex', alignItems: 'center', flexGrow: 1}}>
              <Typography variant="h6" sx={{fontWeight: 600}}>
                {t('dashboard.title')}
              </Typography>
              <Chip
                label="भारत सरकार | Government of India"
                sx={{ml: 2, bgcolor: 'rgba(255,255,255,0.2)'}}
              />
            </Box>
            <LanguageSelector />
            <OfficerProfile />
          </Toolbar>
        </AppBar>
        
        {/* Main Content */}
        <Container maxWidth="xl" sx={{mt: 3, flexGrow: 1}}>
          <Grid container spacing={3}>
            {/* Search and Filters */}
            <Grid item xs={12}>
              <Paper sx={{p: 3, mb: 3}}>
                <SearchAndFilters />
              </Paper>
            </Grid>
            
            {/* Statistics Cards */}
            <Grid item xs={12} md={3}>
              <Card sx={{bgcolor: 'primary.main', color: 'white'}}>
                <CardContent>
                  <Typography variant="h4">1,247</Typography>
                  <Typography variant="body2">Active Viral Clusters</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card sx={{bgcolor: 'secondary.main', color: 'white'}}>
                <CardContent>
                  <Typography variant="h4">89</Typography>
                  <Typography variant="body2">Evidence Packages</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card sx={{bgcolor: 'warning.main', color: 'white'}}>
                <CardContent>
                  <Typography variant="h4">23</Typography>
                  <Typography variant="body2">High Priority Cases</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card sx={{bgcolor: 'info.main', color: 'white'}}>
                <CardContent>
                  <Typography variant="h4">156</Typography>
                  <Typography variant="body2">Officers Active</Typography>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Viral Content Timeline */}
            <Grid item xs={12} md={8}>
              <Paper sx={{p: 3, height: '600px'}}>
                <Typography variant="h6" gutterBottom>
                  {t('viral.content')}
                </Typography>
                <ViralContentTimeline content={viralContent} />
              </Paper>
            </Grid>
            
            {/* India Map Placeholder */}
            <Grid item xs={12} md={4}>
              <Paper sx={{p: 3, height: '600px'}}>
                <Typography variant="h6" gutterBottom>
                  {t('geographic.distribution')}
                </Typography>
                <Box sx={{
                  height: '500px',
                  bgcolor: 'grey.100',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: 1
                }}>
                  <Typography variant="body1" color="text.secondary">
                    India Map Component
                  </Typography>
                </Box>
              </Paper>
            </Grid>
            
            {/* Evidence Management */}
            <Grid item xs={12}>
              <Paper sx={{p: 3}}>
                <Typography variant="h6" gutterBottom>
                  {t('evidence.management')}
                </Typography>
                <EvidenceManagementPanel />
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default IndianPoliceDashboard;