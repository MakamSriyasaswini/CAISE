import sys
import os

# Add CAISE project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy_engine.policy_service import classify_all_objects

from cost_engine.cost import (
    calculate_monthly_cost,
    calculate_potential_savings
)


def calculate_cost_for_all_objects():

    policy_results = classify_all_objects()

    results = []

    for obj in policy_results:

        classification = obj["classification"]
        file_size = obj["file_size"]

        monthly_cost = calculate_monthly_cost(
            file_size=file_size,
            classification=classification
        )

        savings_info = calculate_potential_savings(
            file_size=file_size,
            current_classification=classification
        )

        results.append({
            "object_name": obj["object_name"],
            "file_size": file_size,
            "classification": classification,
            "monthly_cost": monthly_cost,
            "cheaper_classification": savings_info["cheaper_classification"],
            "cheaper_cost": savings_info["cheaper_cost"],
            "potential_savings": savings_info["potential_savings"]
        })

    return results


if __name__ == "__main__":

    print("=" * 70)
    print("CAISE COST ENGINE")
    print("=" * 70)

    results = calculate_cost_for_all_objects()

    total_cost = 0
    total_savings = 0

    for result in results:

        print()
        print("Object:", result["object_name"])
        print("Size:", result["file_size"], "bytes")
        print("Policy Classification:", result["classification"])

        print(
            f"Current Monthly Cost: "
            f"${result['monthly_cost']:.6f}"
        )

        print(
            f"Cheaper Storage Class: "
            f"{result['cheaper_classification']}"
        )

        print(
            f"Cost in Cheaper Class: "
            f"${result['cheaper_cost']:.6f}"
        )

        print(
            f"Potential Monthly Savings: "
            f"${result['potential_savings']:.6f}"
        )

        total_cost += result["monthly_cost"]
        total_savings += result["potential_savings"]

        print("-" * 70)

    print()
    print(f"Total Current Monthly Cost: ${total_cost:.6f}")
    print(f"Total Potential Monthly Savings: ${total_savings:.6f}")
    print()
    print("Cost evaluation completed.")