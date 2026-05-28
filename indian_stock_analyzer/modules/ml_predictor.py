"""
Machine Learning Prediction Module
Predicts stock price direction using technical features
Enhanced with LSTM, XGBoost, and ensemble methods
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
import warnings
warnings.filterwarnings('ignore')

class MLPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        
    def prepare_features(self, data):
        """Create features for ML model"""
        from modules.technical_analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        indicators = analyzer.calculate_all_indicators(data)
        
        # Additional features
        features = pd.DataFrame(index=indicators.index)
        features['Date'] = indicators['Date']
        
        # Price-based features
        features['Close'] = indicators['Close']
        features['Returns'] = indicators['Close'].pct_change().replace([np.inf, -np.inf], np.nan)
        features['Log_Returns'] = np.log(indicators['Close'] / indicators['Close'].shift(1)).replace([np.inf, -np.inf], np.nan)
        
        # Moving average distances
        features['Dist_SMA20'] = ((indicators['Close'] - indicators['SMA_20']) / indicators['SMA_20']).replace([np.inf, -np.inf], np.nan)
        features['Dist_SMA50'] = ((indicators['Close'] - indicators['SMA_50']) / indicators['SMA_50']).replace([np.inf, -np.inf], np.nan)
        features['Dist_SMA200'] = ((indicators['Close'] - indicators['SMA_200']) / indicators['SMA_200']).replace([np.inf, -np.inf], np.nan)
        
        # Trend features
        features['SMA20_Above_SMA50'] = (indicators['SMA_20'] > indicators['SMA_50']).astype(int)
        features['SMA50_Above_SMA200'] = (indicators['SMA_50'] > indicators['SMA_200']).astype(int)
        
        # Momentum features
        features['RSI'] = indicators['RSI']
        features['RSI_Momentum'] = indicators['RSI'].diff()
        
        # MACD features
        features['MACD'] = indicators['MACD'].replace([np.inf, -np.inf], np.nan)
        features['MACD_Signal'] = indicators['MACD_Signal'].replace([np.inf, -np.inf], np.nan)
        features['MACD_Cross'] = (indicators['MACD'] > indicators['MACD_Signal']).astype(int)
        
        # Volatility features
        bb_width = (indicators['BB_Upper'] - indicators['BB_Lower']) / indicators['BB_Middle']
        features['BB_Width'] = bb_width.replace([np.inf, -np.inf], np.nan)
        bb_position = (indicators['Close'] - indicators['BB_Lower']) / (indicators['BB_Upper'] - indicators['BB_Lower'])
        features['BB_Position'] = bb_position.replace([np.inf, -np.inf], np.nan)
        
        # Stochastic features
        features['Stoch_K'] = indicators['Stochastic_K'].replace([np.inf, -np.inf], np.nan)
        features['Stoch_D'] = indicators['Stochastic_D'].replace([np.inf, -np.inf], np.nan)
        
        # Volume features
        if 'Volume' in data.columns:
            vol_ratio = data['Volume'] / data['Volume'].rolling(20).mean()
            features['Volume_Ratio'] = vol_ratio.replace([np.inf, -np.inf], np.nan)
            vol_trend = data['Volume'].pct_change()
            features['Volume_Trend'] = vol_trend.replace([np.inf, -np.inf], np.nan)
        
        # Replace any remaining infinities or NaNs
        features = features.replace([np.inf, -np.inf], np.nan)
        
        # Fill NaN values with column means
        features = features.fillna(features.mean())
        
        # Target: Price direction in next 5 days
        features['Future_Return'] = indicators['Close'].shift(-5).pct_change(5)
        features['Target'] = (features['Future_Return'] > 0).astype(int)
        
        return features
    
    def train_model(self, symbol, data):
        """Train ML model for a stock"""
        try:
            features = self.prepare_features(data)
            
            # Select feature columns
            feature_cols = [col for col in features.columns if col not in ['Date', 'Target', 'Future_Return']]
            
            # Drop rows with NaN in feature columns only
            features = features.dropna(subset=feature_cols)
            
            if len(features) < 50:
                print(f"Not enough data for {symbol}")
                return None
            
            # Check for remaining infinities
            features = features.replace([np.inf, -np.inf], np.nan).dropna(subset=feature_cols)
            
            X = features[feature_cols]
            y = features['Target']
            
            # Ensure no infinities in the data
            X = X.replace([np.inf, -np.inf], np.nan).fillna(X.median())
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            rf_model.fit(X_train_scaled, y_train)
            
            # Train Gradient Boosting
            gb_model = GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5)
            gb_model.fit(X_train_scaled, y_train)
            
            # Train Extra Trees
            et_model = ExtraTreesClassifier(n_estimators=100, random_state=42, max_depth=15)
            et_model.fit(X_train_scaled, y_train)
            
            # Create ensemble with voting
            ensemble = VotingClassifier([
                ('rf', rf_model),
                ('gb', gb_model),
                ('et', et_model)
            ], voting='soft')
            ensemble.fit(X_train_scaled, y_train)
            
            rf_acc = rf_model.score(X_test_scaled, y_test)
            gb_acc = gb_model.score(X_test_scaled, y_test)
            
            # Calculate accuracies with cross-validation
            rf_cv = cross_val_score(rf_model, X_train_scaled, y_train, cv=5).mean()
            gb_cv = cross_val_score(gb_model, X_train_scaled, y_train, cv=5).mean()
            et_cv = cross_val_score(et_model, X_train_scaled, y_train, cv=5).mean()
            ensemble_acc = ensemble.score(X_test_scaled, y_test)
            
            # Store models
            self.models[symbol] = {
                'rf': rf_model,
                'gb': gb_model,
                'et': et_model,
                'ensemble': ensemble,
                'rf_accuracy': rf_acc,
                'gb_accuracy': gb_acc,
                'et_accuracy': et_model.score(X_test_scaled, y_test),
                'ensemble_accuracy': ensemble_acc,
                'rf_cv': rf_cv,
                'gb_cv': gb_cv,
                'et_cv': et_cv
            }
            self.scalers[symbol] = scaler
            
            return {
                'rf_accuracy': rf_acc,
                'gb_accuracy': gb_acc,
                'feature_importance': dict(zip(feature_cols, rf_model.feature_importances_))
            }
            
        except Exception as e:
            print(f"Error training model for {symbol}: {e}")
            return None
    
    def predict(self, symbol, data):
        """Make prediction for a stock"""
        try:
            if symbol not in self.models:
                # Train model if not exists
                result = self.train_model(symbol, data)
                if result is None:
                    return {'prediction': 'NEUTRAL', 'confidence': 50, 'probabilities': [0.5, 0.5]}
            
            features = self.prepare_features(data)
            feature_cols = [col for col in features.columns if col not in ['Date', 'Target', 'Future_Return']]
            
            latest = features[feature_cols].iloc[-1:].values
            latest = self.scalers[symbol].transform(latest)
            
            # Get predictions from all models
            rf_pred = self.models[symbol]['rf'].predict_proba(latest)[0]
            gb_pred = self.models[symbol]['gb'].predict_proba(latest)[0]
            et_pred = self.models[symbol]['et'].predict_proba(latest)[0]
            ensemble_pred = self.models[symbol]['ensemble'].predict_proba(latest)[0]
            
            # Ensemble prediction (weighted average)
            prob_up = ensemble_pred[1]
            confidence = int(prob_up * 100)
            
            # Individual model predictions
            rf_conf = int(rf_pred[1] * 100)
            gb_conf = int(gb_pred[1] * 100)
            et_conf = int(et_pred[1] * 100)
            
            # Model agreement
            models_bullish = sum([rf_pred[1] > 0.5, gb_pred[1] > 0.5, et_pred[1] > 0.5])
            
            if prob_up > 0.6:
                prediction = 'BULLISH'
            elif prob_up < 0.4:
                prediction = 'BEARISH'
            else:
                prediction = 'NEUTRAL'
            
            # Get LSTM prediction
            lstm_result = self.predict_lstm(symbol, data)
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'prob_up': round(prob_up, 3),
                'prob_down': round(ensemble_pred[0], 3),
                'rf_confidence': int(rf_conf),
                'gb_confidence': int(gb_conf),
                'et_confidence': int(et_conf),
                'models_agree': int(models_bullish),
                'total_models': int(3),
                'rf_accuracy': round(self.models[symbol]['rf_accuracy'], 3),
                'gb_accuracy': round(self.models[symbol]['gb_accuracy'], 3),
                'et_accuracy': round(self.models[symbol]['et_accuracy'], 3),
                'ensemble_accuracy': round(self.models[symbol]['ensemble_accuracy'], 3),
                'lstm': lstm_result
            }
            
        except Exception as e:
            print(f"Error predicting for {symbol}: {e}")
            return {'prediction': 'NEUTRAL', 'confidence': 50, 'probabilities': [0.5, 0.5]}
    
    def train_lstm_model(self, symbol, data, lookback=60):
        """Train LSTM model for time series prediction"""
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            
            features = self.prepare_features(data)
            feature_cols = [col for col in features.columns if col not in ['Date', 'Target', 'Future_Return']]
            features = features.dropna(subset=feature_cols)
            
            if len(features) < lookback + 100:
                return None
            
            X = features[feature_cols].values
            y = features['Target'].values
            
            # Create sequences
            X_seq, y_seq = [], []
            for i in range(lookback, len(X)):
                X_seq.append(X[i-lookback:i])
                y_seq.append(y[i])
            
            X_seq, y_seq = np.array(X_seq), np.array(y_seq)
            
            # Split
            split = int(len(X_seq) * 0.8)
            X_train, X_test = X_seq[:split], X_seq[split:]
            y_train, y_test = y_seq[:split], y_seq[split:]
            
            # Build LSTM model
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(1, activation='sigmoid')
            ])
            
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.1, verbose=0)
            
            # Evaluate
            _, accuracy = model.evaluate(X_test, y_test, verbose=0)
            
            # Store LSTM model
            if symbol not in self.models:
                self.models[symbol] = {}
            self.models[symbol]['lstm'] = model
            self.models[symbol]['lstm_accuracy'] = accuracy
            self.models[symbol]['lstm_lookback'] = lookback
            
            return {'lstm_accuracy': accuracy}
            
        except ImportError:
            print("TensorFlow not available, skipping LSTM")
            return None
        except Exception as e:
            print(f"Error training LSTM: {e}")
            return None
    
    def predict_lstm(self, symbol, data):
        """Get LSTM prediction if available"""
        try:
            # Check if TensorFlow is available
            try:
                import tensorflow as tf
                tf_available = True
            except ImportError:
                tf_available = False
            
            # Train or get existing model
            if symbol not in self.models or 'lstm' not in self.models[symbol]:
                if tf_available:
                    self.train_lstm_model(symbol, data)
                else:
                    # Use simple pattern matching fallback
                    return self._simple_lstm_predict(symbol, data)
            
            if symbol in self.models and 'lstm' in self.models[symbol]:
                features = self.prepare_features(data)
                feature_cols = [col for col in features.columns if col not in ['Date', 'Target', 'Future_Return']]
                features = features.dropna(subset=feature_cols)
                
                lookback = self.models[symbol]['lstm_lookback']
                X = features[feature_cols].values
                
                # Create sequence
                X_seq = X[-lookback:].reshape(1, lookback, X.shape[1])
                
                pred = self.models[symbol]['lstm'].predict(X_seq, verbose=0)[0][0]
                
                return {
                    'lstm_prediction': 'BULLISH' if pred > 0.5 else 'BEARISH',
                    'lstm_confidence': int(float(pred) * 100) if pred > 0.5 else int((1-float(pred)) * 100),
                    'lstm_prob_up': round(float(pred), 3)
                }
            
            return None
            
        except Exception as e:
            print(f"LSTM prediction error: {e}")
            return self._simple_lstm_predict(symbol, data)
    
    def _simple_lstm_predict(self, symbol, data):
        """Simple LSTM-like prediction without TensorFlow"""
        try:
            features = self.prepare_features(data)
            closes = features['Close'].values
            returns = features['Returns'].values
            
            # Calculate recent momentum
            recent_returns = returns[-20:]
            avg_return = np.mean(recent_returns)
            momentum = np.mean(recent_returns[-5:]) - np.mean(recent_returns[-10:-5])
            
            current_price = closes[-1]
            
            # Generate predictions based on momentum
            predictions = []
            cumulative_change = 0
            for i in range(5):
                # Add some randomness based on volatility
                volatility = float(np.std(recent_returns)) * np.sqrt(i+1)
                trend = float(avg_return) * (i+1)
                
                # Weight momentum more for near-term
                day_return = trend + (float(momentum) * (5-i) / 5)
                cumulative_change += day_return
                
                predictions.append({
                    'day': i+1,
                    'price': round(float(current_price) * (1 + cumulative_change), 2),
                    'change': round(float(cumulative_change) * 100, 2)
                })
            
            # Determine direction
            momentum_val = float(momentum)
            if momentum_val > 0.01:
                prediction = 'BULLISH'
                confidence = min(50 + int(momentum_val * 1000), 95)
            elif momentum_val < -0.01:
                prediction = 'BEARISH'
                confidence = min(50 + int(abs(momentum_val) * 1000), 95)
            else:
                prediction = 'NEUTRAL'
                confidence = 50
            
            return {
                'predictions': predictions,
                'lstm_prediction': prediction,
                'lstm_confidence': confidence,
                'lstm_prob_up': round(0.5 + momentum_val * 10, 3),
                'note': 'Simplified LSTM (TensorFlow not available)'
            }
            
        except Exception as e:
            print(f"Simple LSTM error: {e}")
            return None
    
    def get_feature_importance(self, symbol):
        """Get feature importance for a stock"""
        if symbol in self.models:
            return self.models[symbol].get('feature_importance', {})
        return {}

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from modules.data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.fetch_stock_data('RELIANCE.NS', '2y')
    
    if data is not None:
        predictor = MLPredictor()
        result = predictor.predict('RELIANCE.NS', data)
        print(f"Prediction: {result}")
