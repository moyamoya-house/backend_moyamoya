from project.models import Moyamoya, MoyamoyaHashtag, HashTag
from sqlalchemy import func

def get_trending_hashtags(session, limit=10):
    results = (
        session.query(HashTag.tag_name, func.count(MoyamoyaHashtag.moyamoya_hashtag_id).label('count'))
        .join(MoyamoyaHashtag, HashTag.tag_id == MoyamoyaHashtag.moyamoya_hashtag_id)
        .group_by(HashTag.tag_name)
        .order_by(func.count(MoyamoyaHashtag.moyamoya_hashtag_id).desc())
        .limit(limit)
        .all()
    )
    return results
