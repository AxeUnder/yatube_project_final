from django.core.paginator import Paginator


def paginator(request, li, pages):
    paginator = Paginator(li, pages)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
