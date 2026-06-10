import math

def paginate_queryset(queryset, page: int = 1, page_size: int = 20):
    """
    Standardizes pagination across APIs.
    Returns: (paginated_data, meta)
    """
    total_items = queryset.count()
    if total_items == 0:
        return [], {
            "total_items": 0,
            "total_pages": 0,
            "current_page": page,
            "page_size": page_size,
            "has_next": False,
            "has_previous": False
        }

    total_pages = math.ceil(total_items / page_size)
    
    # Clip page numbers
    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start = (page - 1) * page_size
    end = start + page_size
    
    paginated_data = queryset[start:end]
    
    return paginated_data, {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }
