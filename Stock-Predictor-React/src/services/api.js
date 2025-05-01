import axios from 'axios';
import { toast } from 'react-toastify';
import { calculateChanges } from '../utils/metrics';

const API_BASE_URL = 'http://localhost:5000';

// Fetch metrics from the API
export const fetchMetricsData = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/metrics`);
    
    const currentMetrics = response.data.metrics.current_metrics;
    const previousMetrics = response.data.metrics.previous_metrics;
    const changes = calculateChanges(previousMetrics, currentMetrics);
    
    const metrics = {
      current: currentMetrics,
      previous: previousMetrics,
      changes: changes
    };
    
    // Format metrics data for display
    const metricsData = [
      {
        label: 'Accuracy',
        value: currentMetrics.Accuracy,
        isPositive: changes.Accuracy === "positive",
        changeval: parseFloat(currentMetrics.Accuracy) - parseFloat(previousMetrics.Accuracy)
      },
      {
        label: 'RMSE',
        value: currentMetrics.RMSE,
        isPositive: changes.RMSE === "positive",
        changeval: parseFloat(currentMetrics.RMSE) - parseFloat(previousMetrics.RMSE)
      },
      {
        label: 'MAE',
        value: currentMetrics.MAE,
        isPositive: changes.MAE === "positive",
        changeval: parseFloat(currentMetrics.MAE) - parseFloat(previousMetrics.MAE)
      },
      {
        label: 'Training Time',
        value: currentMetrics["Training Time"],
        isPositive: changes["Training Time"] === "positive",
        changeval: parseFloat(currentMetrics["Training Time"]) - parseFloat(previousMetrics["Training Time"])
      }
    ];
    
    return { metrics, metricsData };
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return {
      metrics: {
        current: {
          "Accuracy": "0.00%",
          "RMSE": "0.0000",
          "MAE": "0.0000",
          "Training Time": "0m 0s"
        },
        previous: {},
        changes: {}
      },
      metricsData: []
    };
  }
};

// Fetch stock prediction
export const fetchPrediction = async (stock, modelType) => {
  const toastId = toast.loading('Fetching prediction...', { autoClose: false });
  
  try {
    const response = await axios.post(`${API_BASE_URL}/predictf`, { 
      stock, 
      model_type: modelType 
    });
    
    toast.update(toastId, {
      render: 'Prediction fetched successfully!',
      type: 'success',
      isLoading: false,
      autoClose: 3000
    });
    
    return {
      original: response.data.original,
      predicted: response.data.predicted
    };
  } catch (error) {
    console.error('Error fetching prediction:', error);
    
    toast.update(toastId, {
      render: error.response?.data?.error || 'Something went wrong. Please try again.',
      type: 'error',
      isLoading: false,
      autoClose: 3000
    });
    
    throw new Error(error.response?.data?.error || 'Failed to fetch prediction');
  }
};

// Train model
export const trainModel = async (params) => {
  const toastId = toast.loading('Starting model training...', { autoClose: false });
  
  try {
    const response = await axios.post(`${API_BASE_URL}/train`, params);
    
    toast.update(toastId, {
      render: 'Model training completed successfully!',
      type: 'success',
      isLoading: false,
      autoClose: 5000
    });
    
    return {
      metrics: response.data.metrics,
      changes: response.data.changes
    };
  } catch (error) {
    console.error('Error training model:', error);
    
    toast.update(toastId, {
      render: error.response?.data?.error || 'Error during model training.',
      type: 'error',
      isLoading: false,
      autoClose: 5000
    });
    
    throw new Error(error.response?.data?.error || 'Failed to train model');
  }
};