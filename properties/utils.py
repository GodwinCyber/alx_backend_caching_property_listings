from django.core.cache import cache
from .models import Property
from django_redis import get_redis_connection
import logging

logger = logging.getLogger(__name__)

def get_all_properties():
    '''
    Retrieves all properties from the cache if available
    Otherwise fetches from the database and store it in Redis for 1 Hour.
    '''
    # Checks Redis for all_properties using cache.get('all_properties').
    property_data = cache.get('all_properties')
    
    if property_data is None:
        properties = Property.objects.all().values(
            "id", "title", "description", "price", "location", "created_at"
        )

        property_data = list(properties)
        cache.set('all_properties', property_data, timeout=3600)
    return property_data

def get_redis_cache_metrics():
    '''
    Retrieve Redis cache hit and miss statistics safely
    Calculate hit ratio and percentage
    '''
    try:
        # Connect to redis
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()

        # Extract values
        keyspace_hits = info.get("keyspace_hits", 0)
        keyspace_misses = info.get("keyspace_misses", 0)

        # Calcualate totals and hit ratio
        total_requests = keyspace_hits + keyspace_misses
        if total_requests > 0:
            hit_ratio = keyspace_hits / total_requests
            hit_ratio_percentage = hit_ratio * 100
        else:
            hit_ratio = 0.0
            hit_ratio_percentage = 0.0

        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total': total_requests,
            'hit_ratio': round(hit_ratio, 4),
            'hit_ratio_percentage': round(hit_ratio_percentage, 2),
        }

        logger.info(
            f"Redis Cache Metrics: "
            f"{metrics['hit_ratio_percentage']}% hit ratio "
            f"({metrics['keyspace_hits']} hits, {metrics['keyspace_misses']} misses)"
        )

        return metrics
    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {e}")

        return {
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total': 0,
            'hit_ratio': 0.0,
            'hit_ratio_percentage': 0.0,
            'error': str(e)
        }





