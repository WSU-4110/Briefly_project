# api_pipeline.py
from api_handlers import ValidationHandler, CacheHandler, FetchHandler

def build_api_pipeline():
    """
    Creates the Chain of Responsibility pipeline:
    Validation → Cache → Fetch
    """
    validate = ValidationHandler()
    cache = CacheHandler()
    fetch = FetchHandler()

    # Order: validate -> cache -> fetch
    validate.set_next(cache).set_next(fetch)
    return validate
