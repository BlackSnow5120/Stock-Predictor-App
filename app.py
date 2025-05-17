import json
import os
import time
import traceback
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yfinance as yf
from flask import Flask, request, jsonify
from flask_cors import CORS
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
# Download VADER lexicon if not already downloaded

nltk.download('vader_lexicon')
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
analyzer = SentimentIntensityAnalyzer()
def get_model_paths(model_type):
    return {
        "model": f"Stock_LSTM_{model_type}.keras",
        "metrics": f"metrics.json"
    }
def build_lstm_model(input_shape=(100, 1)):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model
def create_dataset(dataset, time_step=100):
    dataX, dataY = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i + time_step), 0]
        dataX.append(a)
        dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)
def read_previous_metrics(metrics_path):
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as file:
            return json.load(file)
    return None
def save_metrics_to_file(metrics, metrics_path):
    with open(metrics_path, 'w') as file:
        json.dump(metrics, file, indent=4)
@app.route('/sentiment', methods=['POST'])
def get_news_and_sentiment():
    """
    Fetches latest news articles for a stock symbol from Yahoo Finance,
    calculates the sentiment score for each article, and returns the article
    title along with a binary sentiment label (0 for negative, 1 for positive)
    and the source URL.
    """
    try:
        data = request.get_json()
        stock_symbol = data.get('stock', 'GOOG')
        url = f"https://finance.yahoo.com/quote/{stock_symbol}/news?p={stock_symbol}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        news_items = soup.find_all('li', class_='stream-item story-item yf-1drgw5l')

        if not news_items:
            print(f"No news found for {stock_symbol}")
            return []
        good_news_count = 0
        bad_news_count = 0
        analyzer = SentimentIntensityAnalyzer()
        news_with_sentiment = []
        for item in news_items:
            headline_element = item.get_text(strip=True) # More specific class for headline
            link_element = item.find('a', class_='subtle-link fin-size-small titles noUnderline yf-bwm9iy') # More specific class for link
            if headline_element and link_element:
                headline = headline_element
                source_url = link_element.get('href')
                if source_url and not source_url.startswith('http'):
                    source_url = f"https://finance.yahoo.com{source_url}" # Ensure absolute URL
                try:
                    sentiment_score = analyzer.polarity_scores(headline)['compound']
                    sentiment_label = 1 if sentiment_score > 0 else 0
                    news_with_sentiment.append({
                        "headline": headline,
                        "sentiment": sentiment_label,
                        "compound_score": sentiment_score, # Include the compound score
                        "source_url": source_url
                    })
                    if sentiment_label == 1:
                        good_news_count += 1
                    elif sentiment_label == 0:
                        bad_news_count += 1
                except Exception as e:
                    print(f"Error analyzing sentiment for headline: {headline}. Error: {e}")
                    pass
        return {"news":news_with_sentiment,"g_score":good_news_count,"b_score":bad_news_count}
    except Exception as e:
        print(f"Error fetching or analyzing news for {stock_symbol}: {e}")
        return []
def train_stock():
    try:
        data = request.get_json()
        stock_symbol = data.get('stock', 'GOOG')
        start = data.get('start', '2012-01-01')
        end = data.get('end', '2022-12-31')
        epochs = int(data.get('epochs', 50))
        model_type = data.get('model_type', '100d')
        time_step = int(model_type.replace('d', ''))
        paths = get_model_paths(model_type)
        MODEL_PATH = paths["model"]
        METRICS_FILE_PATH = paths["metrics"]
        df = yf.download(stock_symbol, start=start, end=end)
        if df.empty:
            return jsonify({"error": "Invalid or unavailable stock data."}), 400
        df_close = df[['Close']]
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_df = scaler.fit_transform(np.array(df_close))
        training_size = int(len(scaled_df) * 0.65)
        train_data = scaled_df[:training_size]
        test_data = scaled_df[training_size:]
        X_train, y_train = create_dataset(train_data, time_step)
        X_test, y_test = create_dataset(test_data, time_step)
        X_train = X_train.reshape(X_train.shape[0], time_step, 1)
        X_test = X_test.reshape(X_test.shape[0], time_step, 1)
        model = build_lstm_model(input_shape=(time_step, 1))
        if os.path.exists(MODEL_PATH):
            model = load_model(MODEL_PATH)
        start_time = time.time()
        history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs, batch_size=64, verbose=1)
        training_time = time.time() - start_time
        model.save(MODEL_PATH)
        predicted = model.predict(X_train).flatten()
        rmse = np.sqrt(mean_squared_error(y_train, predicted))
        mae = mean_absolute_error(y_train, predicted)
        accuracy = 100 - rmse * 100
        metrics = {
            "Accuracy": f"{accuracy:.2f}",
            "RMSE": f"{rmse:.4f}",
            "MAE": f"{mae:.4f}",
            "Training Time": int(training_time)
        }
        previous_metrics = read_previous_metrics(METRICS_FILE_PATH)
        changes = {}
        if previous_metrics:
            prev = previous_metrics.get('current_metrics', {})
            changes = {
                "Accuracy": f"{accuracy - float(prev.get('Accuracy', 0)):.2f}",
                "RMSE": f"{rmse - float(prev.get('RMSE', 0)):.4f}",
                "MAE": f"{mae - float(prev.get('MAE', 0)):.4f}",
                "Training Time": training_time - float(prev.get("Training Time", 0))
            }
        save_metrics_to_file({
            "previous_metrics": previous_metrics["current_metrics"] if previous_metrics else {},
            "current_metrics": metrics
        }, METRICS_FILE_PATH)
        return jsonify({
            "message": f"LSTM model ({model_type}) trained and saved successfully.",
            "metrics": metrics,
            "changes": changes,
            "training_details": {
                "loss": history.history.get('loss', []),
                "epochs": epochs
            }
        })
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
@app.route('/predictf', methods=['POST'])
def predict_future_stock():
    try:
        data = request.get_json()
        stock_symbol = data.get('stock', 'AAPL')
        days_to_predict = int(data.get('days', 10))
        model_type = data.get('model_type', '100d')
        time_step = int(model_type.replace('d', ''))
        paths = get_model_paths(model_type)
        MODEL_PATH = paths["model"]
        if not os.path.exists(MODEL_PATH):
            return jsonify({"error": f"{model_type} model not trained yet. Please train it first."}), 400
        model = load_model(MODEL_PATH)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=200 + time_step)
        df = yf.download(stock_symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        if df.empty:
            return jsonify({"error": "Invalid or unavailable stock data."}), 400
        close_data = df[['Close']]
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(np.array(close_data))
        x_input = scaled_data[-time_step:].reshape(1, time_step, 1)
        temp_input = scaled_data[-time_step:].tolist()
        lst_output = []
        for _ in range(days_to_predict):
            x_input = np.array(temp_input[-time_step:]).reshape(1, time_step, 1)
            yhat = model.predict(x_input, verbose=0)
            temp_input.append(yhat[0].tolist())
            lst_output.extend(yhat.tolist())
        original_dates = [(end_date - timedelta(days=time_step - i)).strftime('%Y-%m-%d') for i in range(time_step)]
        future_dates = [(end_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days_to_predict)]
        original_prices = scaled_data[-time_step:]
        original_prices_rescaled = scaler.inverse_transform(original_prices)
        future_prices_rescaled = scaler.inverse_transform(np.array(lst_output).reshape(-1, 1))
        return jsonify({
            "stock": stock_symbol,
            "model_type": model_type,
            "original": [{"date": date, "price": float(price[0])} for date, price in zip(original_dates[-30:], original_prices_rescaled[-30:])],
            "predicted": [{"date": date, "price": float(price[0])} for date, price in zip(future_dates, future_prices_rescaled)]
        })
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
@app.route('/metrics', methods=['GET'])
def get_metrics():
    try:
        model_type = request.args.get("model_type", "100d")
        paths = get_model_paths(model_type)
        METRICS_FILE_PATH = paths["metrics"]
        previous_metrics = read_previous_metrics('metrics.json')
        if previous_metrics:
            return jsonify({
                "message": f"{model_type} metrics fetched successfully",
                "metrics": previous_metrics
            })
        else:
            return jsonify({"error": f"No metrics found for {model_type}. Please train a model first."}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
     app.run(debug=True)