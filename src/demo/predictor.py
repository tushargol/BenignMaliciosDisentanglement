"""Predictor module for demo - model loading, calibration, and prediction."""

import numpy as np
import torch
import shap
from typing import Dict, Any

from src.models.autoencoder import Autoencoder
from src.models.classifier import AnomalyClassifier
from src.evaluation.evaluate_pipeline import _anomaly_scores_ae


class DemoPredictor:
    """Model loading, calibration, and prediction logic for demo."""
    
    def __init__(self, paths):
        """Initialize predictor with project paths."""
        self.paths = paths
        self.autoencoder = None
        self.classifier = None
        self.reconstruction_threshold = 0.5
        self.classifier_threshold = 0.5
        
    def setup_models(self):
        """Load and configure trained models with proper calibration."""
        print(" Loading Power Systems IDS Models with Calibration...")
        
        try:
            # Load autoencoder (Stage 1)
            self.autoencoder = Autoencoder(input_dim=196, hidden_dim=256, latent_dim=64)
            autoencoder_path = self.paths.outputs_dir / "models" / "autoencoder.pt"
            if autoencoder_path.exists():
                self.autoencoder.load_state_dict(torch.load(autoencoder_path, map_location='cpu'))
                self.autoencoder.eval()
                print(" Autoencoder loaded successfully")
                self.calibrate_thresholds()
            else:
                print("  Autoencoder model not found, using demo mode")
                self.autoencoder = None
                self.reconstruction_threshold = 0.5
            
            # Load classifier (Stage 2)
            self.classifier = AnomalyClassifier(input_dim=196, hidden_dim=128)
            classifier_path = self.paths.outputs_dir / "models" / "classifier.pt"
            if classifier_path.exists():
                self.classifier.load_state_dict(torch.load(classifier_path, map_location='cpu'))
                self.classifier.eval()
                print(" Classifier loaded successfully")
            else:
                print("  Classifier model not found, using demo mode")
                self.classifier = None
                
        except Exception as e:
            print(f"  Model loading failed: {e}")
            print(" Running in simulation mode...")
            self.autoencoder = None
            self.classifier = None
            self.reconstruction_threshold = 0.5
    
    def calibrate_thresholds(self):
        """Calibrate reconstruction error threshold using real data."""
        print(" Calibrating thresholds with real power systems data...")
        
        try:
            from src.data.prepare_pipeline import prepare
            prepared_data = prepare(self.paths)
            X_train = prepared_data.X_train
            
            train_errors = _anomaly_scores_ae(self.autoencoder, X_train)
            self.reconstruction_threshold = np.percentile(train_errors, 95)
            self.classifier_threshold = 0.5
            
            print(f" Reconstruction threshold calibrated: {self.reconstruction_threshold:.3f}")
            print(f" Classifier threshold set: {self.classifier_threshold:.3f}")
            
        except Exception as e:
            print(f"  Threshold calibration failed: {e}")
            self.reconstruction_threshold = 0.5
            self.classifier_threshold = 0.5
    
    def predict_anomaly(self, features: np.ndarray) -> Dict[str, Any]:
        """Predict anomaly using trained models."""
        if self.autoencoder is None or self.classifier is None:
            return self.simulate_prediction(features)
        
        try:
            # Stage 1: Autoencoder anomaly detection
            reconstruction_error = _anomaly_scores_ae(self.autoencoder, features.reshape(1, -1))[0]
            is_anomaly = reconstruction_error > self.reconstruction_threshold
            
            # Stage 2: Classifier for anomaly type
            if is_anomaly:
                features_tensor = torch.from_numpy(features.reshape(1, -1)).float()
                with torch.no_grad():
                    logits = self.classifier(features_tensor)
                    malicious_prob = torch.sigmoid(logits).item()
                
                if malicious_prob > self.classifier_threshold:
                    prediction = "Malicious Attack"
                else:
                    prediction = "Benign Anomaly"
            else:
                prediction = "Normal"
                malicious_prob = 0.0
            
            return {
                'prediction': prediction,
                'reconstruction_error': reconstruction_error,
                'malicious_prob': malicious_prob,
                'threshold': self.reconstruction_threshold,
                'is_anomaly': is_anomaly
            }
            
        except Exception as e:
            print(f"  Prediction failed: {e}")
            return self.simulate_prediction(features)
    
    def simulate_prediction(self, features: np.ndarray) -> Dict[str, Any]:
        """Simulate prediction when models not available."""
        reconstruction_error = np.random.uniform(0.1, 0.8)
        is_anomaly = reconstruction_error > self.reconstruction_threshold
        
        if is_anomaly:
            malicious_prob = np.random.uniform(0.3, 0.9)
            if malicious_prob > self.classifier_threshold:
                prediction = "Malicious Attack"
            else:
                prediction = "Benign Anomaly"
        else:
            prediction = "Normal"
            malicious_prob = 0.0
        
        return {
            'prediction': prediction,
            'reconstruction_error': reconstruction_error,
            'malicious_prob': malicious_prob,
            'threshold': self.reconstruction_threshold,
            'is_anomaly': is_anomaly
        }
    
    def calculate_shap_values(self, features: np.ndarray, prediction: str) -> Dict[str, float]:
        """Calculate SHAP values for feature importance."""
        try:
            if self.classifier is None:
                return self.simulate_shap_values(prediction)
            
            def predict_fn(x):
                self.classifier.eval()
                with torch.no_grad():
                    t = torch.from_numpy(x).float()
                    logits = self.classifier(t)
                    return torch.sigmoid(logits).numpy()
            
            # Use a subset of features as background
            background = features.reshape(1, -1)
            explainer = shap.KernelExplainer(predict_fn, background)
            shap_values = explainer.shap_values(features.reshape(1, -1), nsamples=50)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            mean_abs = np.abs(shap_values).mean(axis=0)
            feature_importance = dict(enumerate(mean_abs.flatten()))
            
            return feature_importance
            
        except Exception as e:
            print(f"  SHAP calculation failed: {e}")
            return self.simulate_shap_values(prediction)
    
    def simulate_shap_values(self, prediction: str) -> Dict[str, float]:
        """Simulate SHAP values when models not available."""
        importance = np.random.randn(196)
        importance = np.abs(importance)
        importance = importance / importance.sum() * 100
        return dict(enumerate(importance))
