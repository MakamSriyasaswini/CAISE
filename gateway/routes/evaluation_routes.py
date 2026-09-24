from fastapi import APIRouter

from unified_evaluation import evaluate_all_objects


router = APIRouter()


@router.get("/evaluation")
def get_storage_evaluation():

    results = evaluate_all_objects()

    return {
        "status": "success",
        "total_objects": len(results),
        "objects": results
    }


@router.get("/evaluation/summary")
def get_evaluation_summary():

    results = evaluate_all_objects()

    hot_count = 0
    warm_count = 0
    cold_count = 0

    no_migration_count = 0
    migration_required_count = 0

    skipped_action_count = 0
    not_implemented_action_count = 0

    total_cost = 0
    total_savings = 0

    for result in results:

        classification = result["classification"]

        if classification == "HOT":
            hot_count += 1

        elif classification == "WARM":
            warm_count += 1

        elif classification == "COLD":
            cold_count += 1

        migration_action = result["migration_action"]

        if migration_action == "NO MIGRATION":
            no_migration_count += 1
        else:
            migration_required_count += 1

        action_status = result["action_status"]

        if action_status == "SKIPPED":
            skipped_action_count += 1

        elif action_status == "NOT_IMPLEMENTED":
            not_implemented_action_count += 1

        total_cost += result["monthly_cost"]
        total_savings += result["potential_savings"]

    return {
        "status": "success",
        "total_objects": len(results),
        "hot_objects": hot_count,
        "warm_objects": warm_count,
        "cold_objects": cold_count,
        "no_migration_required": no_migration_count,
        "migration_required": migration_required_count,
        "skipped_actions": skipped_action_count,
        "not_implemented_actions": not_implemented_action_count,
        "total_current_monthly_cost": total_cost,
        "total_potential_monthly_savings": total_savings
    }