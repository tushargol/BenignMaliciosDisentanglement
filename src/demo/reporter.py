"""Reporter module for demo - report generation and JSON/PNG saving."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class DemoReporter:
    """Report generation and JSON/PNG saving for demo."""
    
    def __init__(self, output_dir: str = "outputs/demo"):
        """Initialize reporter with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def add_result(self, scenario_name: str, result: Dict[str, Any], expected_label: str):
        """Add a result to the report."""
        self.results.append({
            'scenario': scenario_name,
            'prediction': result['prediction'],
            'expected': expected_label,
            'reconstruction_error': result['reconstruction_error'],
            'malicious_prob': result['malicious_prob'],
            'is_anomaly': result['is_anomaly'],
            'threshold': result['threshold'],
            'timestamp': datetime.now().isoformat()
        })
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive demo report."""
        total = len(self.results)
        correct = sum(1 for r in self.results if self._is_correct(r))
        
        predictions = [r['prediction'] for r in self.results]
        prediction_counts = {
            'Normal': predictions.count('Normal'),
            'Benign Anomaly': predictions.count('Benign Anomaly'),
            'Malicious Attack': predictions.count('Malicious Attack')
        }
        
        report = {
            'summary': {
                'total_scenarios': total,
                'correct_predictions': correct,
                'accuracy': correct / total if total > 0 else 0,
                'prediction_distribution': prediction_counts
            },
            'detailed_results': self.results,
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def _is_correct(self, result: Dict[str, Any]) -> bool:
        """Check if prediction matches expected label."""
        return result['prediction'] == result['expected']
    
    def save_json_report(self, report: Dict[str, Any], filename: str = "demo_report.json"):
        """Save report as JSON."""
        report_path = self.output_dir / filename
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  Report saved to {report_path}")
        
    def save_png_visualization(self, visualizer, filename: str = "demo_visualization.png"):
        """Save visualization as PNG."""
        viz_path = self.output_dir / filename
        visualizer.save(viz_path)
        
    def print_summary(self, report: Dict[str, Any]):
        """Print a summary of the demo results."""
        summary = report['summary']
        print("\n" + "="*60)
        print("DEMO RESULTS SUMMARY")
        print("="*60)
        print(f"Total Scenarios: {summary['total_scenarios']}")
        print(f"Correct Predictions: {summary['correct_predictions']}")
        print(f"Accuracy: {summary['accuracy']:.2%}")
        print("\nPrediction Distribution:")
        for label, count in summary['prediction_distribution'].items():
            print(f"  {label}: {count}")
        print("="*60 + "\n")
        
    def clear_results(self):
        """Clear all results."""
        self.results = []
