import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';

// Registering required components
ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

export const getChartData1 = (original, predicted) => {
  return {
    labels: original.map((_, i) => i),
    datasets: [
      {
        label: 'Original Price',
        data: original,
        fill: false,
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.1)',
        borderWidth: 2,
        pointRadius: 1,
        tension: 0.4,
      },
      {
        label: 'Predicted Price',
        data: predicted,
        fill: false,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        borderWidth: 2,
        pointRadius: 1,
        tension: 0.4,
      },
    ],
  };
};

export function getChartData(original, predicted) {
  return {
    labels: [
      ...original.map(item => item.date),
      ...predicted.map(item => item.date)
    ],
    datasets: [
      {
        label: 'Original Price',
        data: original.map(item => item.price),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.4)',
        fill: false,
        tension: 0.3
      },
      {
        label: 'Predicted Price',
        data: [
          ...Array(original.length).fill(null), // Leave original dates empty for prediction
          ...predicted.map(item => item.price)
        ],
        borderColor: '#FF9800',
        backgroundColor: 'rgba(255, 152, 0, 0.4)',
        fill: false,
        borderDash: [5, 5],
        tension: 0.3
      }
    ]
  };
}

// Chart options configuration
export const getChartOptions = () => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(44, 62, 80, 0.9)',
        bodyFont: {
          family: "'Inter', sans-serif",
          size: 13,
        },
        titleFont: {
          family: "'Inter', sans-serif",
          size: 14,
          weight: 'bold',
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
    },
  };
};
