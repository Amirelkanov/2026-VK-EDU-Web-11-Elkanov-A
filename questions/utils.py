from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from data.questions.mock_data import MOCK_TAGS


def get_popular_tags(count=10):
    return MOCK_TAGS[:count]


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
