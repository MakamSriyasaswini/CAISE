from gateway.services.minio_provider import MinIOProvider
from gateway.services.minio_b_provider import MinIOBProvider
from gateway.services.metadata_service import update_storage_provider


def get_provider(provider_name):

    if provider_name == "MinIO-A":
        return MinIOProvider()

    elif provider_name == "MinIO-B":
        return MinIOBProvider()

    raise ValueError(
        f"Unsupported provider: {provider_name}"
    )


def execute_storage_action(
    filename,
    current_provider,
    target_provider,
    action
):

    if action == "NO MIGRATION":

        return {
            "filename": filename,
            "current_provider": current_provider,
            "target_provider": target_provider,
            "action": "NO MIGRATION",
            "status": "SKIPPED",
            "message": "Object is already on the target provider."
        }

    if action == "MIGRATE":

        try:

            source = get_provider(current_provider)
            target = get_provider(target_provider)

            # Find the source object
            source_files = source.list_files()

            source_object = None

            for obj in source_files:

                if obj["filename"] == filename:
                    source_object = obj
                    break

            if source_object is None:

                return {
                    "filename": filename,
                    "current_provider": current_provider,
                    "target_provider": target_provider,
                    "action": "MIGRATE",
                    "status": "FAILED",
                    "message": "Source object was not found."
                }

            source_size = source_object["size"]

            # Copy object to target
            migration_result = source.migrate_object_to(
                filename,
                target
            )

            # Verify target object
            target_files = target.list_files()

            target_object = None

            for obj in target_files:

                if obj["filename"] == filename:
                    target_object = obj
                    break

            if target_object is None:

                return {
                    "filename": filename,
                    "current_provider": current_provider,
                    "target_provider": target_provider,
                    "action": "MIGRATE",
                    "status": "FAILED",
                    "message": (
                        "Object was copied but could not be verified "
                        "on the target provider."
                    )
                }

            target_size = target_object["size"]

            # Verify size
                      
            if source_size != target_size:

                return {
                    "filename": filename,
                    "current_provider": current_provider,
                    "target_provider": target_provider,
                    "action": "MIGRATE",
                    "status": "FAILED",
                    "message": (
                        f"Verification failed: source size is "
                        f"{source_size} bytes but target size is "
                        f"{target_size} bytes."
                    )
                }

            # Delete source only after target verification succeeds
            source.delete_file(filename)

            # Verify source object was actually deleted
            source_files_after_delete = source.list_files()

            source_still_exists = any(
                obj["filename"] == filename
                for obj in source_files_after_delete
            )

            if source_still_exists:

                return {
                    "filename": filename,
                    "current_provider": current_provider,
                    "target_provider": target_provider,
                    "action": "MIGRATE",
                    "status": "FAILED",
                    "message": (
                        "Target object was verified, but the source "
                        "object could not be removed."
                    )
                }

            # Update PostgreSQL only after complete migration
            update_storage_provider(
                object_key=filename,
                storage_provider=target_provider
            )

            return {
                "filename": filename,
                "current_provider": current_provider,
                "target_provider": target_provider,
                "action": "MIGRATE",
                "status": "VERIFIED",
                "message": (
                    "Object copied and verified on target provider. "
                    "Metadata updated successfully."
                )
            }

        except Exception as e:

            return {
                "filename": filename,
                "current_provider": current_provider,
                "target_provider": target_provider,
                "action": "MIGRATE",
                "status": "FAILED",
                "message": str(e)
            }

    return {
        "filename": filename,
        "current_provider": current_provider,
        "target_provider": target_provider,
        "action": action,
        "status": "NOT_IMPLEMENTED",
        "message": "Storage action is not implemented."
    }