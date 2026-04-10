"""Visualizer module for demo - all matplotlib/seaborn visualization code."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class DemoVisualizer:
    """All matplotlib/seaborn visualization code for demo."""
    
    def __init__(self):
        """Initialize visualizer."""
        self.fig = None
        self.axes = None
        
    def setup_plots(self):
        """Set up visualization plots."""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        ax_main = fig.add_subplot(gs[0, :])
        ax_recon = fig.add_subplot(gs[1, 0])
        ax_class = fig.add_subplot(gs[1, 1])
        ax_shap = fig.add_subplot(gs[1, 2])
        ax_timeline = fig.add_subplot(gs[2, :])
        
        self.fig = fig
        self.axes = {
            'main': ax_main,
            'recon': ax_recon,
            'class': ax_class,
            'shap': ax_shap,
            'timeline': ax_timeline
        }
        
        self._setup_initial_plots()
        
    def _setup_initial_plots(self):
        """Set up initial plot state."""
        ax = self.axes['main']
        ax.set_title('Power Systems IDS - Real-Time Monitoring', fontsize=16, fontweight='bold')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('System Status')
        ax.set_ylim(-0.5, 2.5)
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['Normal', 'Benign Anomaly', 'Malicious Attack'])
        ax.grid(True, alpha=0.3)
        
        # Initialize empty plots
        self.axes['recon'].set_title('Reconstruction Error')
        self.axes['recon'].set_xlabel('Sample')
        self.axes['recon'].set_ylabel('Error')
        
        self.axes['class'].set_title('Classifier Output')
        self.axes['class'].set_xlabel('Malicious Probability')
        self.axes['class'].set_ylabel('Count')
        
        self.axes['shap'].set_title('Feature Importance (SHAP)')
        self.axes['shap'].set_xlabel('Feature Index')
        self.axes['shap'].set_ylabel('Importance')
        
        self.axes['timeline'].set_title('Detection Timeline')
        self.axes['timeline'].set_xlabel('Time')
        self.axes['timeline'].set_ylabel('Detection')
        
    def update_visualization(self, scenario_name: str, result: Dict[str, Any], shap_values: Dict[str, float]):
        """Update visualization with prediction results."""
        self.axes['main'].set_title(f'Current Scenario: {scenario_name}', fontsize=14, fontweight='bold')
        
        # Update reconstruction error plot
        self.axes['recon'].clear()
        self.axes['recon'].set_title('Reconstruction Error')
        self.axes['recon'].bar(['Current', 'Threshold'], 
                               [result['reconstruction_error'], result['threshold']],
                               color=['red' if result['is_anomaly'] else 'green', 'blue'])
        self.axes['recon'].set_ylabel('Error')
        
        # Update classifier output plot
        self.axes['class'].clear()
        self.axes['class'].set_title('Classifier Output')
        self.axes['class'].bar(['Benign', 'Malicious'], 
                               [1 - result['malicious_prob'], result['malicious_prob']],
                               color=['green', 'red'])
        self.axes['class'].set_ylabel('Probability')
        
        # Update SHAP plot
        self.axes['shap'].clear()
        self.axes['shap'].set_title('Top 10 Feature Importance (SHAP)')
        if shap_values:
            sorted_features = sorted(shap_values.items(), key=lambda x: x[1], reverse=True)[:10]
            features, importance = zip(*sorted_features)
            self.axes['shap'].barh(range(len(features)), importance)
            self.axes['shap'].set_yticks(range(len(features)))
            self.axes['shap'].set_yticklabels([f'F{f}' for f in features])
            self.axes['shap'].set_xlabel('Importance')
        
        plt.tight_layout()
        
    def show(self):
        """Display the visualization."""
        if self.fig is not None:
            plt.show()
    
    def save(self, path):
        """Save the visualization to a file."""
        if self.fig is not None:
            self.fig.savefig(path, dpi=150, bbox_inches='tight')
            print(f"  Visualization saved to {path}")
    
    def close(self):
        """Close the visualization."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.axes = None
