import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import 'chart.js/auto';

function App() {
  const [stock, setStock] = useState('GOOG');
  const [original, setOriginal] = useState([]);
  const [predicted, setPredicted] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:5000/predict', { stock });
      setOriginal(response.data.original);
      setPredicted(response.data.predicted);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Something went wrong. Please try again.');
    }
    setLoading(false);
  };

  const data = {
    labels: original.map((_, i) => i),
    datasets: [
      {
        label: 'Original Price',
        data: original,
        fill: false,
        borderColor: 'green',
        tension: 0.4,
      },
      {
        label: 'Predicted Price',
        data: predicted,
        fill: false,
        borderColor: 'red',
        tension: 0.4,
      },
    ],
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>📈 Stock Market Predictor</h1>
      <div style={styles.inputGroup}>
        <input
          type="text"
          value={stock}
          onChange={(e) => setStock(e.target.value.toUpperCase())}
          placeholder="Enter stock symbol (e.g., AAPL)"
          style={styles.input}
        />
        <button onClick={fetchData} style={styles.button} disabled={loading}>
          {loading ? 'Predicting...' : 'Predict'}
        </button>
      </div>

      {error && <p style={styles.error}>{error}</p>}

      {loading ? (
        <div style={styles.spinner}>🔄 Fetching prediction...</div>
      ) : (
        original.length > 0 && (
          <div style={styles.chartContainer}>
            <Line data={data} />
          </div>
        )
      )}
    </div>
  );
}

const styles = {
  container: {
    fontFamily: 'Arial, sans-serif',
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#f4f4f4',
    minHeight: '100vh',
  },
  title: {
    fontSize: '2.5rem',
    marginBottom: '20px',
    color: '#333',
  },
  inputGroup: {
    marginBottom: '30px',
    display: 'flex',
    justifyContent: 'center',
    gap: '10px',
  },
  input: {
    padding: '10px 20px',
    fontSize: '1rem',
    border: '1px solid #ccc',
    borderRadius: '8px',
    width: '300px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '1rem',
    backgroundColor: '#007bff',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
  },
  chartContainer: {
    width: '80%',
    maxWidth: '900px',
    margin: 'auto',
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '12px',
    boxShadow: '0 0 10px rgba(0,0,0,0.1)',
  },
  spinner: {
    fontSize: '1.2rem',
    color: '#555',
    marginTop: '20px',
  },
  error: {
    color: 'red',
    marginBottom: '20px',
    fontWeight: 'bold',
  },
};

export default App;
