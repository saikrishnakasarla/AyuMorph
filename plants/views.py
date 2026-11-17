"""
Views for the Plants application.
"""

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Plant

def plant_list(request):
    """
    Displays the catalog of documented botanical species.
    Supports keyword search, category filtering, and pagination.
    """
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    sort_by = request.GET.get('sort', 'name')

    plants = Plant.objects.filter(is_active=True)

    if search_query:
        plants = plants.filter(
            Q(name__icontains=search_query) |
            Q(scientific_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(identification_features__icontains=search_query)
        )

    if category_filter:
        plants = plants.filter(category=category_filter)

    if sort_by == 'name_desc':
        plants = plants.order_by('-name')
    elif sort_by == 'created':
        plants = plants.order_by('-created_at')
    else:
        plants = plants.order_by('name')

    # Categories for the filter dropdown
    categories = Plant.CATEGORY_CHOICES

    # Pagination: 9 plants per page
    paginator = Paginator(plants, 9)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'sort_by': sort_by,
        'categories': categories,
        'total_count': paginator.count,
    }
    return render(request, 'plants/plant_list.html', context)

def plant_detail(request, pk):
    """
    Displays comprehensive scientific and traditional botanical documentation
    for a single plant specimen.
    """
    plant = get_object_or_404(Plant, pk=pk, is_active=True)
    recent_predictions = plant.predictions.filter(user=request.user)[:3] if request.user.is_authenticated else []
    
    context = {
        'plant': plant,
        'user_predictions': recent_predictions,
    }
    return render(request, 'plants/plant_detail.html', context)
