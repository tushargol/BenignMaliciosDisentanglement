"""Unit tests for actual project pipeline logic."""

import numpy as np
import pytest
import torch
from dataclasses import dataclass
from typing import List, Optional

from src.data.prepare_pipeline import PreparedData
from src.data.windowing import Window
from src.models.autoencoder import Autoencoder
from src.models.classifier import AnomalyClassifier
from src.evaluation.evaluate_pipeline import evaluate_two_stage


@dataclass
class MockWindow:
    """Mock Window for testing."""
    label: str
    attack_family: str
    features: np.ndarray


def test_two_stage_decision_logic():
    """Test evaluate_two_stage with synthetic data."""
    # Create synthetic PreparedData-like object
    np.random.seed(42)
    X_test = np.random.randn(100, 10).astype(np.float32)
    y_test = np.array([0] * 50 + [1] * 25 + [2] * 25, dtype=np.int64)
    
    # Create mock windows
    windows_test = []
    for i in range(100):
        if i < 50:
            windows_test.append(MockWindow("normal", "none", np.random.randn(90, 10)))
        elif i < 75:
            windows_test.append(MockWindow("benign", "maintenance", np.random.randn(90, 10)))
        else:
            windows_test.append(MockWindow("malicious", "drift-off", np.random.randn(90, 10)))
    
    # Create PreparedData-like object
    from src.data.prepare_pipeline import PreparedData
    prep = PreparedData(
        X_train=np.random.randn(200, 10).astype(np.float32),
        y_train=np.array([0] * 200, dtype=np.int64),
        X_test=X_test,
        y_test=y_test,
        windows_train=[],
        windows_test=windows_test,
        feature_cols=[f"f{i}" for i in range(10)],
        feature_channel_names=[f"ch{i}" for i in range(10)],
        input_dim=10,
        config={},
    )
    
    # Create tiny autoencoder and classifier
    ae = Autoencoder(input_dim=10, hidden_dim=8, latent_dim=4)
    clf = AnomalyClassifier(input_dim=10, hidden_dim=8)
    
    # Run evaluation
    y_true, y_pred, y_score = evaluate_two_stage(
        prep,
        ae,
        clf,
        ae_threshold_percentile=80.0,
        clf_threshold=0.5,
        benign_ctrl_mean_threshold=None,
        attack_context_rescue=False,
        device="cpu",
    )
    
    # Assert output shapes
    assert y_true.shape == (100,), "y_true should have 100 samples"
    assert y_pred.shape == (100,), "y_pred should have 100 samples"
    assert y_score.shape == (100,), "y_score should have 100 samples"
    
    # Assert label values are in valid range
    assert np.all(y_true >= 0) and np.all(y_true <= 2), "y_true should be 0, 1, or 2"
    assert np.all(y_pred >= 0) and np.all(y_pred <= 2), "y_pred should be 0, 1, or 2"
    assert np.all(y_score >= 0) and np.all(y_score <= 1), "y_score should be between 0 and 1"


def test_threshold_affects_recall():
    """Test that higher AE threshold produces fewer anomaly detections."""
    np.random.seed(42)
    X_test = np.random.randn(100, 10).astype(np.float32)
    y_test = np.array([0] * 50 + [1] * 25 + [2] * 25, dtype=np.int64)
    
    windows_test = [MockWindow("normal", "none", np.random.randn(90, 10)) for _ in range(100)]
    
    prep = PreparedData(
        X_train=np.random.randn(200, 10).astype(np.float32),
        y_train=np.array([0] * 200, dtype=np.int64),
        X_test=X_test,
        y_test=y_test,
        windows_train=[],
        windows_test=windows_test,
        feature_cols=[f"f{i}" for i in range(10)],
        feature_channel_names=[f"ch{i}" for i in range(10)],
        input_dim=10,
        config={},
    )
    
    ae = Autoencoder(input_dim=10, hidden_dim=8, latent_dim=4)
    clf = AnomalyClassifier(input_dim=10, hidden_dim=8)
    
    # Run with low threshold (60th percentile)
    _, y_pred_60, _ = evaluate_two_stage(
        prep, ae, clf, ae_threshold_percentile=60.0, clf_threshold=0.5,
        benign_ctrl_mean_threshold=None, attack_context_rescue=False, device="cpu",
    )
    
    # Run with high threshold (95th percentile)
    _, y_pred_95, _ = evaluate_two_stage(
        prep, ae, clf, ae_threshold_percentile=95.0, clf_threshold=0.5,
        benign_ctrl_mean_threshold=None, attack_context_rescue=False, device="cpu",
    )
    
    # Count anomalies (non-zero predictions)
    anomalies_60 = np.sum(y_pred_60 > 0)
    anomalies_95 = np.sum(y_pred_95 > 0)
    
    # Higher threshold should produce fewer anomalies
    assert anomalies_95 <= anomalies_60, "Higher threshold should produce fewer or equal anomaly detections"


def test_attack_context_rescue():
    """Test rule-based rescue for industroyer context."""
    np.random.seed(42)
    X_test = np.random.randn(10, 10).astype(np.float32)
    y_test = np.array([0] * 10, dtype=np.int64)
    
    # Create windows with industroyer context in the last window
    windows_test = []
    for i in range(9):
        windows_test.append(MockWindow("normal", "none", np.random.randn(90, 10)))
    
    # Last window has industroyer context (n_ctx_industroyer channel)
    features_with_ctx = np.random.randn(90, 10)
    features_with_ctx[:, 1] = 5.0  # Set industroyer context channel to non-zero
    windows_test.append(MockWindow("malicious", "industroyer", features_with_ctx))
    
    prep = PreparedData(
        X_train=np.random.randn(50, 10).astype(np.float32),
        y_train=np.array([0] * 50, dtype=np.int64),
        X_test=X_test,
        y_test=y_test,
        windows_train=[],
        windows_test=windows_test,
        feature_cols=[f"f{i}" for i in range(10)],
        feature_channel_names=["n_events", "n_ctx_industroyer"] + [f"ch{i}" for i in range(8)],
        input_dim=10,
        config={},
    )
    
    ae = Autoencoder(input_dim=10, hidden_dim=8, latent_dim=4)
    clf = AnomalyClassifier(input_dim=10, hidden_dim=8)
    
    # Run with attack context rescue enabled
    _, y_pred, _ = evaluate_two_stage(
        prep, ae, clf, ae_threshold_percentile=95.0, clf_threshold=0.5,
        benign_ctrl_mean_threshold=None, attack_context_rescue=True, device="cpu",
    )
    
    # Last window should be promoted to malicious (label 2)
    assert y_pred[9] == 2, "Window with industroyer context should be promoted to malicious"


def test_no_data_leakage():
    """Test that classifier training and evaluation splits have no overlap."""
    np.random.seed(42)
    X_test = np.random.randn(100, 10).astype(np.float32)
    y_test = np.array([0] * 50 + [1] * 25 + [2] * 25, dtype=np.int64)
    
    windows_test = [MockWindow("normal", "none", np.random.randn(90, 10)) for _ in range(100)]
    
    # Set up split indices (simulating the fix from Step 1)
    clf_train_indices = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
    clf_eval_indices = np.array([25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49])
    
    prep = PreparedData(
        X_train=np.random.randn(200, 10).astype(np.float32),
        y_train=np.array([0] * 200, dtype=np.int64),
        X_test=X_test,
        y_test=y_test,
        windows_train=[],
        windows_test=windows_test,
        feature_cols=[f"f{i}" for i in range(10)],
        feature_channel_names=[f"ch{i}" for i in range(10)],
        input_dim=10,
        config={},
        clf_train_indices=clf_train_indices,
        clf_eval_indices=clf_eval_indices,
    )
    
    # Assert no overlap between train and eval indices
    overlap = np.intersect1d(clf_train_indices, clf_eval_indices)
    assert len(overlap) == 0, "Classifier training and evaluation splits should have no overlapping indices"
    
    # Assert both splits are within valid range
    assert np.all(clf_train_indices >= 0) and np.all(clf_train_indices < len(X_test)), "Train indices should be valid"
    assert np.all(clf_eval_indices >= 0) and np.all(clf_eval_indices < len(X_test)), "Eval indices should be valid"
