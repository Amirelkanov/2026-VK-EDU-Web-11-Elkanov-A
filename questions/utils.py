from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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
