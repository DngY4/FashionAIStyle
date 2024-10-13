import React, { useState } from 'react';
import axios from 'axios';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6200ea',
    },
    secondary: {
      main: '#03dac6',
    },
  },
});

const styleQuizQuestions = [
  "What's your go-to outfit for a casual day?",
  "How would you describe your ideal evening wear?",
  "What's your favorite accessory?",
  "Which color palette do you prefer?",
  "How do you feel about following fashion trends?",
];

function App() {
  const [occasion, setOccasion] = useState('');
  const [preferredColor, setPreferredColor] = useState('');
  const [bodyType, setBodyType] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [trends, setTrends] = useState<string[]>([]);
  const [quizOpen, setQuizOpen] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState<string[]>(Array(styleQuizQuestions.length).fill(''));
  const [quizResult, setQuizResult] = useState('');
  const [newDataOpen, setNewDataOpen] = useState(false);
  const [newData, setNewData] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const getStyleRecommendation = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/style_recommendation', {
        occasion,
        preferred_color: preferredColor,
        body_type: bodyType,
      });
      setRecommendation(response.data.message);
    } catch (error) {
      console.error('Error fetching style recommendation:', error);
    }
  };

  const getTrendAnalysis = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/trend_analysis');
      setTrends(response.data.current_trends);
    } catch (error) {
      console.error('Error fetching trend analysis:', error);
    }
  };

  const handleQuizSubmit = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/style_quiz', {
        answers: quizAnswers,
      });
      setQuizResult(`Your dominant style is ${response.data.dominant_style}: ${response.data.description}`);
      setQuizOpen(false);
    } catch (error) {
      console.error('Error submitting style quiz:', error);
    }
  };

  const handleNewDataSubmit = async () => {
    try {
      const parsedData = JSON.parse(newData);
      const response = await axios.post('http://localhost:5000/api/train_ai', {
        new_data: parsedData,
      });
      setSnackbarMessage(response.data.message);
      setSnackbarOpen(true);
      setNewDataOpen(false);
    } catch (error) {
      console.error('Error submitting new data:', error);
      setSnackbarMessage('Error submitting new data. Please check the format and try again.');
      setSnackbarOpen(true);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h2" component="h1" gutterBottom>
            FashionStyleAI
          </Typography>
          <Box sx={{ mb: 2 }}>
            <TextField
              label="Occasion"
              value={occasion}
              onChange={(e) => setOccasion(e.target.value)}
              fullWidth
              margin="normal"
            />
            <TextField
              label="Preferred Color"
              value={preferredColor}
              onChange={(e) => setPreferredColor(e.target.value)}
              fullWidth
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Body Type</InputLabel>
              <Select
                value={bodyType}
                label="Body Type"
                onChange={(e) => setBodyType(e.target.value)}
              >
                <MenuItem value="hourglass">Hourglass</MenuItem>
                <MenuItem value="pear">Pear</MenuItem>
                <MenuItem value="apple">Apple</MenuItem>
                <MenuItem value="rectangle">Rectangle</MenuItem>
                <MenuItem value="inverted triangle">Inverted Triangle</MenuItem>
              </Select>
            </FormControl>
            <Button variant="contained" onClick={getStyleRecommendation} sx={{ mr: 1 }}>
              Get Style Recommendation
            </Button>
            <Button variant="outlined" onClick={getTrendAnalysis} sx={{ mr: 1 }}>
              Get Trend Analysis
            </Button>
            <Button variant="outlined" onClick={() => setQuizOpen(true)} sx={{ mr: 1 }}>
              Take Style Quiz
            </Button>
            <Button variant="outlined" onClick={() => setNewDataOpen(true)}>
              Add New Data
            </Button>
          </Box>
          {recommendation && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h5" component="div">
                  Style Recommendation:
                </Typography>
                <Typography variant="body1">{recommendation}</Typography>
              </CardContent>
            </Card>
          )}
          {trends.length > 0 && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h5" component="div">
                  Current Trends:
                </Typography>
                <List>
                  {trends.map((trend, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={trend} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
          {quizResult && (
            <Card>
              <CardContent>
                <Typography variant="h5" component="div">
                  Your Style Personality:
                </Typography>
                <Typography variant="body1">{quizResult}</Typography>
              </CardContent>
            </Card>
          )}
        </Box>
      </Container>
      <Dialog open={quizOpen} onClose={() => setQuizOpen(false)}>
        <DialogTitle>Style Personality Quiz</DialogTitle>
        <DialogContent>
          {styleQuizQuestions.map((question, index) => (
            <FormControl component="fieldset" key={index} sx={{ mt: 2 }}>
              <Typography variant="subtitle1">{question}</Typography>
              <RadioGroup
                value={quizAnswers[index]}
                onChange={(e) => {
                  const newAnswers = [...quizAnswers];
                  newAnswers[index] = e.target.value;
                  setQuizAnswers(newAnswers);
                }}
              >
                <FormControlLabel value="classic" control={<Radio />} label="Classic" />
                <FormControlLabel value="bohemian" control={<Radio />} label="Bohemian" />
                <FormControlLabel value="minimalist" control={<Radio />} label="Minimalist" />
                <FormControlLabel value="preppy" control={<Radio />} label="Preppy" />
                <FormControlLabel value="edgy" control={<Radio />} label="Edgy" />
                <FormControlLabel value="romantic" control={<Radio />} label="Romantic" />
              </RadioGroup>
            </FormControl>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQuizOpen(false)}>Cancel</Button>
          <Button onClick={handleQuizSubmit} variant="contained">Submit</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={newDataOpen} onClose={() => setNewDataOpen(false)}>
        <DialogTitle>Add New Fashion Data</DialogTitle>
        <DialogContent>
          <TextField
            label="New Data (JSON format)"
            multiline
            rows={4}
            value={newData}
            onChange={(e) => setNewData(e.target.value)}
            fullWidth
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewDataOpen(false)}>Cancel</Button>
          <Button onClick={handleNewDataSubmit} variant="contained">Submit</Button>
        </DialogActions>
      </Dialog>
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={() => setSnackbarOpen(false)}>
        <Alert onClose={() => setSnackbarOpen(false)} severity="success" sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;