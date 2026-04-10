#!/usr/bin/env python3
"""
Power Systems IDS - Improved Demo with Real Sherlock Data
Benign vs. Malicious Anomaly Disentanglement in Industrial Control Systems

Refactored to use modular structure in src/demo/
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Paths
from src.demo import SherlockDemoDataLoader, DemoPredictor, DemoVisualizer, DemoReporter


def run_interactive_demo(data_loader, predictor, visualizer, reporter):
    """Run interactive demo with user scenario selection."""
    scenarios = data_loader.get_scenarios()
    print(f"\nAvailable Scenarios: {', '.join(scenarios.keys())}")
    
    while True:
        scenario_name = input("\nEnter scenario name (or 'quit' to exit): ").strip()
        if scenario_name.lower() == 'quit':
            break
        
        if scenario_name not in scenarios:
            print(f"Invalid scenario. Available: {', '.join(scenarios.keys())}")
            continue
        
        run_scenario(scenario_name, scenarios[scenario_name], predictor, visualizer, reporter)
        time.sleep(1)


def run_automated_demo(data_loader, predictor, visualizer, reporter):
    """Run automated demo through all scenarios."""
    scenarios = data_loader.get_scenarios()
    for scenario_name, scenario_data in scenarios.items():
        run_scenario(scenario_name, scenario_data, predictor, visualizer, reporter)
        time.sleep(1)


def run_scenario(scenario_name, scenario_data, predictor, visualizer, reporter):
    """Run a single scenario."""
    print(f"\nRunning: {scenario_name}")
    print(f"Description: {scenario_data['description']}")
    
    result = predictor.predict_anomaly(scenario_data['features'])
    shap_values = predictor.calculate_shap_values(scenario_data['features'], result['prediction'])
    
    visualizer.update_visualization(scenario_name, result, shap_values)
    visualizer.show()
    
    reporter.add_result(scenario_name, result, scenario_data['expected_label'])
    
    print(f"Prediction: {result['prediction']}")
    print(f"Expected: {scenario_data['expected_label']}")
    print(f"Reconstruction Error: {result['reconstruction_error']:.3f}")
    print(f"Malicious Probability: {result['malicious_prob']:.3f}")


def main():
    """Main demo function using modular structure."""
    print("Enhanced Power Systems Industrial IDS - Interactive Demo")
    print("=" * 70)
    print("Featuring Real Sherlock Operational Data & Improved Analytics")
    print("Benign vs. Malicious Anomaly Disentanglement in Industrial Control Systems")
    print("=" * 70)
    
    try:
        # Initialize components
        paths = Paths.auto()
        data_loader = SherlockDemoDataLoader(paths)
        predictor = DemoPredictor(paths)
        visualizer = DemoVisualizer()
        reporter = DemoReporter()
        
        # Load data and models
        data_loader.load_real_sherlock_data()
        predictor.setup_models()
        visualizer.setup_plots()
        
        # Choose demo mode
        print("\n🎮 Select Enhanced Demo Mode:")
        print("   1. Interactive Demo (user selects scenarios with real data)")
        print("   2. Automated Demo (runs all scenarios including real Sherlock data)")
        print("   3. Quick Demo (runs 3 key scenarios with mixed data sources)")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            run_interactive_demo(data_loader, predictor, visualizer, reporter)
        elif choice == '2':
            run_automated_demo(data_loader, predictor, visualizer, reporter)
        elif choice == '3':
            scenarios = data_loader.get_scenarios()
            quick_scenarios = ['normal_operation', 'maintenance_procedure', 'relay_trip_attack']
            for scenario in quick_scenarios:
                if scenario in scenarios:
                    run_scenario(scenario, scenarios[scenario], predictor, visualizer, reporter)
                    time.sleep(1)
        else:
            print("❌ Invalid choice. Running automated demo...")
            run_automated_demo(data_loader, predictor, visualizer, reporter)
        
        # Generate reports
        report = reporter.generate_report()
        reporter.save_json_report(report)
        reporter.save_png_visualization(visualizer)
        reporter.print_summary(report)
        
        print("\nEnhanced demo completed successfully!")
        print("Check the outputs directory for detailed reports and visualizations.")
        print("This demo featured real Sherlock power systems operational data!")
        
        visualizer.close()
        
    except KeyboardInterrupt:
        print("\n\n👋 Enhanced demo interrupted by user.")
    except Exception as e:
        print(f"\nEnhanced demo error: {e}")
        print("Please check your installation and model files.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
