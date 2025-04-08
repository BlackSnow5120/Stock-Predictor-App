from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
import yfinance as yf
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
CORS(app)

model = load_model('StockModel.keras')

@app.route('/predict', methods=['POST'])
def predict_stock():
    try:
        data = request.get_json()
        stock_symbol = data.get('stock', 'GOOG')

        start = '2012-01-01'
        end = '2022-12-31'

        df = yf.download(stock_symbol, start, end)
        if df.empty:
            return jsonify({"error": "Invalid stock symbol"}), 400

        data_train = pd.DataFrame(df.Close[0:int(len(df)*0.80)])
        data_test = pd.DataFrame(df.Close[int(len(df)*0.80):])

        scaler = MinMaxScaler(feature_range=(0, 1))
        pas_100_days = data_train.tail(100)
        data_test_full = pd.concat([pas_100_days, data_test], ignore_index=True)
        data_test_scaled = scaler.fit_transform(data_test_full)

        x_test = []
        y_test = []

        for i in range(100, data_test_scaled.shape[0]):
            x_test.append(data_test_scaled[i-100:i])
            y_test.append(data_test_scaled[i, 0])

        x_test, y_test = np.array(x_test), np.array(y_test)

        predicted = model.predict(x_test)

        scale = 1 / scaler.scale_[0]
        predicted = predicted * scale
        y_test = y_test * scale

        return jsonify({
            "predicted": predicted.flatten().tolist(),
            "original": y_test.tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)