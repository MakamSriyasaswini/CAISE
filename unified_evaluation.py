import sys
import os

# Add CAISE project root to Python path
sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from policy_engine.policy_service import classify_all_objects
from cost_engine.cost_service import calculate_cost_for_all_objects
from decision_engine.decision import make_storage_decision
from decision_engine.migration_planner import plan_migration
from gateway.services.storage_action_service import execute_storage_action


def evaluate_all_objects():

    # Get policy information
    policy_results = classify_all_objects()

    # Get cost information
    cost_results = calculate_cost_for_all_objects()

    # Create cost lookup using object name
    cost_lookup = {}

    for obj in cost_results:
        cost_lookup[obj["object_name"]] = obj

    results = []

    for policy_obj in policy_results:

        object_name = policy_obj["object_name"]

        cost_obj = cost_lookup[object_name]

        # Get the object's ACTUAL current provider
        current_provider = policy_obj["storage_provider"]

        # Make storage decision
        decision, reason = make_storage_decision(
            classification=policy_obj["classification"],
            potential_savings=cost_obj["potential_savings"]
        )

        # Plan migration using the object's actual provider
        migration_plan = plan_migration(
            filename=object_name,
            current_classification=policy_obj["classification"],
            decision=decision,
            current_provider=current_provider
        )

        # Execute storage action
        storage_action = execute_storage_action(
            filename=object_name,
            current_provider=current_provider,
            target_provider=migration_plan["target_provider"],
            action=migration_plan["action"]
        )

        results.append({
            "object_name": object_name,
            "file_size": policy_obj["file_size"],
            "download_count": policy_obj["download_count"],
            "last_access": policy_obj["last_access"],
            "classification": policy_obj["classification"],
            "current_provider": current_provider,
            "monthly_cost": cost_obj["monthly_cost"],
            "cheaper_classification": cost_obj["cheaper_classification"],
            "potential_savings": cost_obj["potential_savings"],
            "decision": decision,
            "reason": reason,
            "target_provider": migration_plan["target_provider"],
            "migration_action": migration_plan["action"],
            "migration_reason": migration_plan["reason"],
            "action_status": storage_action["status"],
            "action_message": storage_action["message"]
        })

    return results


if __name__ == "__main__":

    print("=" * 80)
    print("CAISE UNIFIED STORAGE EVALUATION")
    print("=" * 80)

    results = evaluate_all_objects()

    total_cost = 0
    total_savings = 0

    for result in results:

        print()
        print("Object:", result["object_name"])
        print("Size:", result["file_size"], "bytes")
        print("Downloads:", result["download_count"])
        print("Last Access:", result["last_access"])
        print("Policy Classification:", result["classification"])

        print(
            f"Current Provider: "
            f"{result['current_provider']}"
        )

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

        print(
            f"Target Provider: "
            f"{result['target_provider']}"
        )

        print(
            f"Migration Action: "
            f"{result['migration_action']}"
        )

        print(
            f"Migration Reason: "
            f"{result['migration_reason']}"
        )

        print(
            f"Action Status: "
            f"{result['action_status']}"
        )

        print(
            f"Action Message: "
            f"{result['action_message']}"
        )

        total_cost += result["monthly_cost"]
        total_savings += result["potential_savings"]

        print("-" * 80)

    print()
    print(f"TOTAL CURRENT MONTHLY COST: ${total_cost:.6f}")
    print(
        f"TOTAL POTENTIAL MONTHLY SAVINGS: "
        f"${total_savings:.6f}"
    )
    print()
    print("Unified storage evaluation completed.")