from ..services.recommendation_service import get_recommendations as _get_recs


def get_access_recommendations(employee_id: str, db):
    return _get_recs(db, employee_id)
