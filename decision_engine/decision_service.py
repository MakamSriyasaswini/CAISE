import sys
import os

# Add CAISE project root to Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from cost_engine.cost_service import calculate_cost_for_all_objects
from decision_engine.decision import make_storage_decision


def evaluate_storage_decisions():

    cost_results = calculate_cost_for_all_objects()

    results = []

    for obj in cost_results:

        decision, reason = make_storage_decision(
            classification=obj["classification"],
            potential_savings=obj["potential_savings"]
        )

        results.append({
            "object_name": obj["object_name"],
            "file_size": obj["file_size"],
            "classification": obj["classification"],
            "monthly_cost": obj["monthly_cost"],
            "cheaper_classification": obj["cheaper_classification"],
            "potential_savings": obj["potential_savings"],
            "decision": decision,
            "reason": reason
        })

    return results


if __name__ == "__main__":

    print("=" * 70)
    print("CAISE STORAGE DECISION ENGINE")
    print("=" * 70)

    results = evaluate_storage_decisions()

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
            f"Potential Monthly Savings: "
            f"${result['potential_savings']:.6f}"
        )

        print(
            f"Storage Decision: "
            f"{result['decision']}"
        )

        print(
            f"Decision Reason: "
            f"{result['reason']}"
        )

        print("-" * 70)

    print()
    print("Storage decision evaluation completed.")