// Calculate changes between current and previous metrics
export const calculateChanges = (previous, current) => {
    if (!previous || !current) return {};
    
    return {
      "Accuracy": parseFloat(current.Accuracy) > parseFloat(previous.Accuracy) ? "positive" : "negative",
      "RMSE": parseFloat(current.RMSE) < parseFloat(previous.RMSE) ? "positive" : "negative",
      "MAE": parseFloat(current.MAE) < parseFloat(previous.MAE) ? "positive" : "negative",
      "Training Time": parseFloat(current["Training Time"]) < parseFloat(previous["Training Time"]) ? "positive" : "negative"
    };
  };