import React, { useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import { getChartData, getChartOptions } from '../utils/chartConfig';
import ChartJS from 'chart.js/auto';

function ChartDisplay({ original, predicted }) {
  const chartRef = useRef(null); // Reference for the chart

  useEffect(() => {
    // Clean up the previous chart before rendering a new one
    const chartInstance = chartRef.current.chartInstance;
    if (chartInstance) {
      chartInstance.destroy();
    }
  }, [original, predicted]); // Re-run the cleanup when data changes

  const chartData = getChartData(original, predicted);
  const chartOptions = getChartOptions();

  return (
    <>
      <div className="chart-container">
        <Line ref={chartRef} data={chartData} options={chartOptions} />
      </div>
      <div className="chart-legend">
        <div className="legend-item">
          <div className="legend-color color-original"></div>
          <span>Original Price</span>
        </div>
        <div className="legend-item">
          <div className="legend-color color-predicted"></div>
          <span>Predicted Price</span>
        </div>
      </div>
    </>
  );
}

export default ChartDisplay;
