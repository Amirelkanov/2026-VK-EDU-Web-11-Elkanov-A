from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse

LIKE_CHOICES = (
    (1, "Like"),
    (-1, "Dislike"),
)

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)

    page = request.GET.get("page", 1)

    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1

    try:
        paginated_page = paginator.page(page)
    except PageNotAnInteger:
        paginated_page = paginator.page(1)
    except EmptyPage:
        paginated_page = paginator.page(paginator.num_pages)

    return paginated_page, paginator

def json_error(message, status=400, **extra):
    payload = {"ok": False, "error": message}
    payload.update(extra)
    return JsonResponse(payload, status=status)