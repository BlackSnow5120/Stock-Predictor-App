"""
Streamlit Dashboard for Stock Prediction - Works with FastAPI backend.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Stock Prediction Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Stock Prediction Dashboard (FastAPI)")

# Sidebar configuration
st.sidebar.header("Configuration")

stock_symbol = st.sidebar.text_input("Stock Symbol", value="AAPL", help="Enter stock symbol (e.g., AAPL, GOOGL, TSLA)").upper()

model_type = st.sidebar.selectbox(
    "Select Model",
    ["lstm", "chronos", "chronos-t5"],
    help="Choose which prediction model to use"
)

date_range = st.sidebar.selectbox(
    "Date Range",
    ["1mo", "3mo", "6mo", "1y", "max"],
    help="Historical data range to fetch"
)

prediction_days = st.sidebar.slider(
    "Days to Predict",
    min_value=1,
    max_value=30,
    value=7,
    help="Number of future days to predict"
)

training_epochs = st.sidebar.slider(
    "Training Epochs (LSTM only)",
    min_value=10,
    max_value=100,
    value=50,
    step=10,
    help="Number of epochs for LSTM training"
)

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Stock Data", "🔮 Predictions", "📰 News & Sentiment"])

# Tab 1: Stock Data
with tab1:
    st.header("Historical Stock Data")

    if st.button("Fetch Data", key="fetch_data"):
        with st.spinner("Fetching data..."):
            try:
                response = requests.post(f"{API_URL}/data", json={
                    "symbol": stock_symbol,
                    "range": date_range,
                    "interval": "1d"
                })
                data = response.json()

                if data.get("status") == "error":
                    st.error(data.get("message", "Unknown error"))
                else:
                    df = pd.DataFrame(data["data"])
                    # Convert Timestamp string back to datetime
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                    df = df.sort_values('Timestamp')

                    # Display info
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Data Points", data["data_points"])
                    col2.metric("Latest Close", f"${df['Close'].iloc[-1]:.2f}")
                    col3.metric("Date Range", f"{df['Timestamp'].iloc[0].strftime('%Y-%m-%d')} to {df['Timestamp'].iloc[-1].strftime('%Y-%m-%d')}")

                    # Display chart
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=df['Timestamp'],
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name='OHLC'
                    ))
                    fig.update_layout(
                        title=f"{stock_symbol} Stock Price",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Display dataframe
                    st.subheader("Recent Data")
                    st.dataframe(df.tail(10), use_container_width=True)

                    # Store in session state
                    st.session_state['stock_data'] = df

            except Exception as e:
                st.error(f"Error fetching data: {e}")

# Tab 2: Predictions
with tab2:
    st.header("Price Predictions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Train Model", key="train_model"):
            if model_type != 'lstm':
                st.info(f"{model_type.upper()} is pre-trained. No training required.")
            else:
                with st.spinner(f"Training LSTM model for {stock_symbol}..."):
                    try:
                        response = requests.post(f"{API_URL}/train", json={
                            "symbol": stock_symbol,
                            "epochs": training_epochs,
                            "model_type": model_type,
                            "batch_size": 32
                        })
                        result = response.json()

                        if result.get("status") == "error":
                            st.error(result.get("message", "Unknown error"))
                        else:
                            st.success(f"✅ {result.get('symbol')} model trained successfully!")
                            st.json(result.get("metrics"))

                    except Exception as e:
                        st.error(f"Error training model: {e}")

    with col2:
        if st.button("Predict Prices", key="predict_prices"):
            with st.spinner("Generating predictions..."):
                try:
                    response = requests.post(f"{API_URL}/predict", json={
                        "symbol": stock_symbol,
                        "days": prediction_days,
                        "model_type": model_type
                    })
                    result = response.json()

                    if result.get("status") == "error":
                        st.error(result.get("message", "Unknown error"))
                    else:
                        st.success(f"✅ Predictions generated for {prediction_days} days")

                        predictions = result["predictions"]
                        pred_df = pd.DataFrame(predictions)
                        # Convert date string to datetime
                        pred_df['date'] = pd.to_datetime(pred_df['date'])

                        # Display predictions table
                        st.subheader("Predicted Prices")
                        st.dataframe(pred_df, use_container_width=True)

                        # Store in session state
                        st.session_state['predictions'] = pred_df

                        # Plot predictions if we have historical data
                        if 'stock_data' in st.session_state:
                            hist_df = st.session_state['stock_data'].tail(30)

                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=hist_df['Timestamp'],
                                y=hist_df['Close'],
                                mode='lines+markers',
                                name='Historical',
                                line=dict(color='blue')
                            ))

                            # Add predictions using date from the API response
                            fig.add_trace(go.Scatter(
                                x=pred_df['date'],
                                y=pred_df['price'],
                                mode='lines+markers',
                                name='Predicted',
                                line=dict(color='red', dash='dash')
                            ))

                            fig.update_layout(
                                title=f"{stock_symbol} - Historical vs Predicted",
                                xaxis_title="Date",
                                yaxis_title="Price (USD)",
                                height=500
                            )
                            st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"Error predicting prices: {e}")

# Tab 3: News & Sentiment
with tab3:
    st.header("News & Sentiment Analysis")

    snippet_count = st.slider("Number of News Articles", 1, 20, 10)

    if st.button("Fetch News", key="fetch_news"):
        with st.spinner("Fetching news..."):
            try:
                response = requests.post(f"{API_URL}/sentiment", json={
                    "symbol": stock_symbol,
                    "snippet_count": snippet_count
                })
                result = response.json()

                if result.get("status") == "error":
                    st.error(result.get("message", "Unknown error"))
                else:
                    summary = result.get("summary", "")
                    
                    # Handle both old format (with count) and new format
                    if "overall_sentiment" not in summary:
                        summary = {
                            "positive": summary.get("positive", 0),
                            "negative": summary.get("negative", 0),
                            "neutral": summary.get("neutral", 0),
                            "total": result.get("count", len(result.get("articles", []))),
                            "overall_sentiment": result.get("overall_sentiment", "Unknown"),
                            "average_score": result.get("average_score", 0.0)
                        }

                    # Display sentiment summary
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total", summary["total"], delta="Articles")
                    col2.metric("Positive", summary["positive"], delta="😊", delta_color="normal")
                    col3.metric("Negative", summary["negative"], delta="😔", delta_color="inverse")
                    col4.metric("Neutral", summary["neutral"], delta="😐")

                    # Overall sentiment
                    if summary["total"] > 0:
                        positive_ratio = summary["positive"] / summary["total"]
                        if positive_ratio > 0.6:
                            st.success("📈 Overall Sentiment: POSITIVE")
                        elif positive_ratio < 0.4:
                            st.error("📉 Overall Sentiment: NEGATIVE")
                        else:
                            st.info("➡️ Overall Sentiment: NEUTRAL")

                    # Display articles
                    articles = result.get("articles", [])
                    if articles:
                        st.subheader("Recent News (Last 30 Days)")
                        for article in articles:
                            sentiment_color = {
                                "Positive": "green",
                                "Negative": "red",
                                "Neutral": "blue"
                            }

                            with st.container():
                                st.markdown(f"**{article['Headline']}**")
                                col1, col2 = st.columns([1, 4])
                                col1.markdown(
                                    f"<span style='color:{sentiment_color.get(article['Sentiment'], 'black')}'>"
                                    f":label: {article['Sentiment']}</span>",
                                    unsafe_allow_html=True
                                )
                                col2.caption(f"Published: {article['Date']} | Score: {article['SentimentScore']:.2f}")
                                if article.get('Summary'):
                                    st.caption(article['Summary'])
                                st.markdown("---")
                    else:
                        st.info("No news articles available for this stock.")

            except Exception as e:
                st.error(f"Error fetching news: {e}")
                st.caption(f"Error details: {str(type(e).__name__)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Built with Streamlit + FastAPI")
st.sidebar.caption("Models: LSTM, Chronos, Chronos-T5")
st.sidebar.markdown(f"API: {API_URL}")
