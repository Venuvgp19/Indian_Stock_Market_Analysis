"""
Advanced ML Models
Enhanced ensemble methods for stock prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AdvancedMLPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        
    def prepare_features(self, data):
        """Enhanced feature preparation"""
        features = pd.DataFrame(index=data.index)
        
        # Price-based features
        features['returns'] = data['Close'].pct_change()
        features['log_returns'] = np.log(data['Close'] / data['Close'].shift(1))
        
        # Moving averages
        for window in [5, 10, 20, 50]:
            features[f'sma_{window}'] = data['Close'].rolling(window=window).mean()
            features[f'ema_{window}'] = data['Close'].ewm(span=window, adjust=False).mean()
            features[f'distance_sma_{window}'] = (data['Close'] - features[f'sma_{window}']) / features[f'sma_{window}']
        
        # Volatility
        features['volatility_20'] = data['Close'].rolling(window=20).std()
        features['volatility_50'] = data['Close'].rolling(window=50).std()
        
        # Price momentum
        for period in [1, 3, 5, 10, 20]:
            features[f'momentum_{period}'] = data['Close'].shift(period) / data['Close'] - 1
        
        # Volume features
        features['volume_sma_20'] = data['Volume'].rolling(window=20).mean()
        features['volume_ratio'] = data['Volume'] / features['volume_sma_20']
        features['price_volume_trend'] = (data['Close'] - data['Close'].shift(1)) * data['Volume']
        
        # High-Low features
        features['high_low_ratio'] = data['High'] / data['Low']
        features['high_close_ratio'] = data['High'] / data['Close']
        features['low_close_ratio'] = data['Low'] / data['Close']
        
        # Candlestick features
        features['body_size'] = abs(data['Close'] - data['Open']) / data['Open']
        features['upper_shadow'] = (data['High'] - data[['Close', 'Open']].max(axis=1)) / data['Open']
        features['lower_shadow'] = (data[['Close', 'Open']].min(axis=1) - data['Low']) / data['Open']
        
        # Lagged features
        for lag in [1, 2, 3, 5]:
            features[f'close_lag_{lag}'] = data['Close'].shift(lag)
            features[f'volume_lag_{lag}'] = data['Volume'].shift(lag)
        
        # Target: next day return
        features['target'] = data['Close'].shift(-1) / data['Close'] - 1
        
        # Clean infinite values
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        return features
    
    def train_ensemble(self, data):
        """Train ensemble of models"""
        features = self.prepare_features(data)
        
        # Remove rows with NaN targets
        features = features.dropna(subset=['target'])
        
        if len(features) < 50:
            return None
        
        X = features.drop('target', axis=1)
        y = features['target']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['ensemble'] = scaler
        
        # Train multiple models
        models = {
            'rf': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
            'ada': AdaBoostRegressor(n_estimators=100, random_state=42),
            'extra': ExtraTreesRegressor(n_estimators=100, max_depth=10, random_state=42),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.01),
            'elastic': ElasticNet(alpha=0.01, l1_ratio=0.5),
            'svr': SVR(kernel='rbf', C=1.0, epsilon=0.1)
        }
        
        # Train each model
        for name, model in models.items():
            try:
                model.fit(X_scaled, y)
                self.models[name] = model
            except Exception as e:
                print(f"Error training {name}: {e}")
        
        return len(self.models)
    
    def predict_ensemble(self, data):
        """Make predictions using ensemble"""
        if not self.models:
            return None
        
        features = self.prepare_features(data)
        X = features.drop('target', axis=1).iloc[-1:]
        
        if 'ensemble' not in self.scalers:
            return None
        
        X_scaled = self.scalers['ensemble'].transform(X)
        
        predictions = []
        weights = {
            'rf': 0.20,
            'gb': 0.20,
            'extra': 0.15,
            'ridge': 0.10,
            'svr': 0.15,
            'lasso': 0.10,
            'elastic': 0.05,
            'ada': 0.05
        }
        
        for name, model in self.models.items():
            try:
                pred = model.predict(X_scaled)[0]
                predictions.append(pred * weights.get(name, 0.1))
            except:
                pass
        
        if not predictions:
            return None
        
        return sum(predictions)
    
    def get_ml_signals(self, data):
        """Get ML-based trading signals"""
        # Train models
        num_models = self.train_ensemble(data)
        
        if num_models is None or num_models == 0:
            return {'error': 'Could not train models'}
        
        # Get ensemble prediction
        ensemble_pred = self.predict_ensemble(data)
        
        # Combine predictions
        predictions = {}
        if ensemble_pred is not None:
            predictions['ensemble'] = round(ensemble_pred * 100, 2)
        
        # Determine signal
        if ensemble_pred is not None:
            if ensemble_pred > 0.01:
                signal = 'STRONG_BUY'
                confidence = min(95, 50 + ensemble_pred * 5000)
            elif ensemble_pred > 0.005:
                signal = 'BUY'
                confidence = min(85, 50 + ensemble_pred * 5000)
            elif ensemble_pred > -0.005:
                signal = 'HOLD'
                confidence = 50
            elif ensemble_pred > -0.01:
                signal = 'SELL'
                confidence = min(85, 50 - ensemble_pred * 5000)
            else:
                signal = 'STRONG_SELL'
                confidence = min(95, 50 - ensemble_pred * 5000)
        else:
            signal = 'UNKNOWN'
            confidence = 0
        
        return {
            'signal': signal,
            'confidence': round(confidence, 2),
            'predicted_return': predictions.get('ensemble', 0),
            'models_trained': num_models,
            'prediction_type': 'Ensemble'
        }
