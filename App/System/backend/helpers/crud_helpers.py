
# ==================================================
# crud_helpers.py
#
# Shared CRUD helper functions.
#
# Purpose:
# - Reduce repeated router code
# - Standardize delete/archive behavior
# - Reuse across all Maintain Hub domains
# ==================================================


def delete_record(
    db,
    model_class,
    record_id: int,
    record_name: str
):
    """
    Permanently delete a database record.

    Example:

        delete_record(
            db,
            House,
            1,
            "House"
        )
    """

    record = db.query(
        model_class
    ).filter(
        model_class.id == record_id
    ).first()

    if not record:

        return {
            "error": f"{record_name} not found"
        }

    db.delete(
        record
    )

    db.commit()

    return {
        "message": f"{record_name} deleted"
    }