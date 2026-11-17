"""
Views for the Classifier application.
Includes landing pages, researcher dashboard, image upload, ML execution,
prediction result presentation, and history filtering.
"""

import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.utils import timezone

from .models import Prediction
from .forms import PlantImageUploadForm
from .ml.predictor import (
    predict_plant,
    PlantPredictor,
    ModelNotFoundError,
    MLEnvironmentError
)
from plants.models import Plant

logger = logging.getLogger(__name__)


def home(request):
    """
    Public landing page for AyuMorph.
    """
    catalog_count = Plant.objects.filter(is_active=True).count()
    context = {
        'catalog_count': catalog_count,
        'model_ready': PlantPredictor.is_model_available(),
    }
    return render(request, 'home.html', context)


def about(request):
    """
    Detailed project description, architectural methodology,
    and academic viva documentation.
    """
    context = {
        'model_metadata': PlantPredictor().get_metadata(),
    }
    return render(request, 'about.html', context)


@login_required
def dashboard(request):
    """
    Personal researcher dashboard showing classification statistics,
    recent inferences, and quick actions.
    """
    user_predictions = Prediction.objects.filter(user=request.user)

    total_count = user_predictions.count()
    ayurvedic_count = user_predictions.filter(
        predicted_class__icontains='Ayurvedic'
    ).exclude(predicted_class__icontains='Non-Ayurvedic').count()
    non_ayurvedic_count = user_predictions.filter(
        predicted_class__icontains='Non-Ayurvedic'
    ).count()

    recent_predictions = user_predictions.select_related('plant')[:6]
    catalog_count = Plant.objects.filter(is_active=True).count()
    is_model_ready = PlantPredictor.is_model_available()

    context = {
        'total_count': total_count,
        'ayurvedic_count': ayurvedic_count,
        'non_ayurvedic_count': non_ayurvedic_count,
        'recent_predictions': recent_predictions,
        'catalog_count': catalog_count,
        'is_model_ready': is_model_ready,
    }
    return render(request, 'classifier/dashboard.html', context)


@login_required
def upload_view(request):
    """
    Image upload view with drag-and-drop support, server-side validation,
    and invocation of the MobileNetV2 predictor.
    """
    is_model_ready = PlantPredictor.is_model_available()

    if request.method == 'POST':
        form = PlantImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['image']
            notes = form.cleaned_data.get('notes', '')

            # Create an initial prediction entry to store image on disk
            prediction_record = Prediction(
                user=request.user,
                uploaded_image=uploaded_file,
                predicted_class="Processing...",
                confidence=0.0,
                prediction_status="PENDING",
                notes=notes
            )
            prediction_record.save()

            image_path = prediction_record.uploaded_image.path

            # Run MobileNetV2 Inference
            try:
                if not is_model_ready:
                    # Model file not yet placed: inform user explicitly
                    prediction_record.prediction_status = 'FAILED'
                    prediction_record.predicted_class = 'Model Pending Placement'
                    prediction_record.save()
                    messages.warning(
                        request,
                        "Trained model file ('model.h5' or 'model.keras') was not found in 'classifier/ml_model/'. "
                        "Please place your trained MobileNetV2 file into this directory to enable live predictions."
                    )
                    return redirect('classifier:prediction_detail', pk=prediction_record.pk)

                # Execute genuine model prediction
                result = predict_plant(image_path)

                prediction_record.predicted_class = result["class_name"]
                prediction_record.confidence = result["confidence"]
                prediction_record.raw_score = result.get("raw_score")
                prediction_record.processing_time = result.get("processing_time")
                prediction_record.model_version = result.get("model_version", "MobileNetV2")
                prediction_record.prediction_status = "SUCCESS"

                # Link matched botanical species if identified as Ayurvedic
                if result.get("is_ayurvedic"):
                    # Match exact plant or default to first catalog plant for demonstration
                    matched_plant = Plant.objects.filter(
                        Q(name__icontains=result["class_name"]) |
                        Q(category='Ayurvedic Plant')
                    ).first()
                    prediction_record.plant = matched_plant

                prediction_record.save()
                messages.success(request, f"Classification complete: {prediction_record.predicted_class}")
                return redirect('classifier:prediction_result', pk=prediction_record.pk)

            except ModelNotFoundError as e:
                prediction_record.prediction_status = 'FAILED'
                prediction_record.predicted_class = 'Model File Missing'
                prediction_record.save()
                messages.error(request, str(e))
                return redirect('classifier:prediction_detail', pk=prediction_record.pk)

            except MLEnvironmentError as e:
                prediction_record.prediction_status = 'FAILED'
                prediction_record.predicted_class = 'ML Runtime Incompatibility'
                prediction_record.save()
                messages.error(request, f"Machine Learning framework error: {str(e)}")
                return redirect('classifier:prediction_detail', pk=prediction_record.pk)

            except Exception as e:
                logger.exception("Unexpected error during image classification")
                prediction_record.prediction_status = 'FAILED'
                prediction_record.predicted_class = 'Inference Error'
                prediction_record.save()
                messages.error(request, f"An error occurred during inference: {str(e)}")
                return redirect('classifier:prediction_detail', pk=prediction_record.pk)
        else:
            messages.error(request, "Please correct the upload validation errors below.")
    else:
        form = PlantImageUploadForm()

    context = {
        'form': form,
        'is_model_ready': is_model_ready,
    }
    return render(request, 'classifier/upload.html', context)


@login_required
def prediction_result(request, pk):
    """
    Displays the inference outcome, confidence meter, botanical characteristics,
    and educational medicinal disclaimers.
    """
    prediction = get_object_or_404(Prediction, pk=pk, user=request.user)
    context = {
        'prediction': prediction,
        'plant': prediction.plant,
    }
    return render(request, 'classifier/result.html', context)


@login_required
def prediction_detail(request, pk):
    """
    Displays deep audit and technical metadata for an individual prediction.
    """
    prediction = get_object_or_404(Prediction, pk=pk, user=request.user)
    context = {
        'prediction': prediction,
    }
    return render(request, 'classifier/prediction_detail.html', context)


@login_required
def history_view(request):
    """
    Displays user-isolated prediction history with search, filtering,
    sorting, and pagination.
    """
    search_query = request.GET.get('q', '').strip()
    class_filter = request.GET.get('class', '').strip()
    sort_by = request.GET.get('sort', 'newest')

    predictions = Prediction.objects.filter(user=request.user).select_related('plant')

    if search_query:
        predictions = predictions.filter(
            Q(predicted_class__icontains=search_query) |
            Q(plant__name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    if class_filter == 'ayurvedic':
        predictions = predictions.filter(
            predicted_class__icontains='Ayurvedic'
        ).exclude(predicted_class__icontains='Non-Ayurvedic')
    elif class_filter == 'non_ayurvedic':
        predictions = predictions.filter(predicted_class__icontains='Non-Ayurvedic')

    if sort_by == 'oldest':
        predictions = predictions.order_by('created_at')
    elif sort_by == 'confidence_desc':
        predictions = predictions.order_by('-confidence')
    elif sort_by == 'confidence_asc':
        predictions = predictions.order_by('confidence')
    else:
        predictions = predictions.order_by('-created_at')

    paginator = Paginator(predictions, 10)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'class_filter': class_filter,
        'sort_by': sort_by,
        'total_count': paginator.count,
    }
    return render(request, 'classifier/history.html', context)


@login_required
def prediction_delete(request, pk):
    """
    Allows user to delete their own prediction record and clean up the uploaded media file.
    """
    prediction = get_object_or_404(Prediction, pk=pk, user=request.user)

    if request.method == 'POST':
        # Clean up image file on disk safely
        if prediction.uploaded_image:
            try:
                if os.path.exists(prediction.uploaded_image.path):
                    os.remove(prediction.uploaded_image.path)
            except Exception as e:
                logger.warning(f"Could not remove image file {prediction.uploaded_image.name}: {e}")

        pred_id = prediction.id
        prediction.delete()
        messages.success(request, f"Prediction #{pred_id} has been permanently deleted.")
        return redirect('classifier:history')

    return render(request, 'classifier/prediction_confirm_delete.html', {'prediction': prediction})


# Custom HTTP Error Handlers
def error_400(request, exception=None):
    return render(request, '400.html', status=400)

def error_403(request, exception=None):
    return render(request, '403.html', status=403)

def error_404(request, exception=None):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)
