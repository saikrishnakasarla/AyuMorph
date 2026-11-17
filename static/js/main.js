/**
 * AyuMorph - Frontend JavaScript Interactions
 * Handles image drag-and-drop, client-side validation, instant previews,
 * and loading overlays for MobileNetV2 inference.
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialize Bootstrap Tooltips if available
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 2. Auto-dismiss alerts after 6 seconds
  const alertElements = document.querySelectorAll('.alert-dismissible');
  alertElements.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 6000);
  });

  // 3. Image Upload, Drag-and-Drop, and Instant Preview Handling
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('image-input');
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('preview-image');
  const previewFileName = document.getElementById('preview-filename');
  const previewFileSize = document.getElementById('preview-filesize');
  const removePreviewBtn = document.getElementById('remove-preview-btn');
  const uploadForm = document.getElementById('plant-upload-form');
  const loadingOverlay = document.getElementById('loading-overlay');

  if (dropzone && fileInput) {
    // Click on dropzone triggers hidden file input
    dropzone.addEventListener('click', function (e) {
      if (e.target !== removePreviewBtn && !previewContainer.contains(e.target)) {
        fileInput.click();
      }
    });

    // Drag-and-drop visual events
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    // Drop file event
    dropzone.addEventListener('drop', function (e) {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        fileInput.files = files;
        handleSelectedFile(files[0]);
      }
    });

    // Standard file input change
    fileInput.addEventListener('change', function () {
      if (fileInput.files && fileInput.files.length > 0) {
        handleSelectedFile(fileInput.files[0]);
      }
    });

    // Remove preview action
    if (removePreviewBtn) {
      removePreviewBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        fileInput.value = '';
        previewContainer.style.display = 'none';
        previewImage.src = '';
        dropzone.querySelector('.dropzone-prompt').style.display = 'block';
      });
    }

    function handleSelectedFile(file) {
      // Validate format
      const validExtensions = ['image/jpeg', 'image/png', 'image/webp'];
      if (!validExtensions.includes(file.type)) {
        alert('Unsupported file format. Please upload a JPEG, PNG, or WEBP image.');
        fileInput.value = '';
        return;
      }

      // Validate size (max 5 MB)
      const maxSizeBytes = 5 * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        alert('File size exceeds 5 MB. Please select a smaller image.');
        fileInput.value = '';
        return;
      }

      // Generate preview
      const reader = new FileReader();
      reader.onload = function (e) {
        previewImage.src = e.target.result;
        previewFileName.textContent = file.name;
        previewFileSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
        previewContainer.style.display = 'block';
        dropzone.querySelector('.dropzone-prompt').style.display = 'none';
      };
      reader.readAsDataURL(file);
    }
  }

  // 4. Form submission with Loading Overlay
  if (uploadForm && loadingOverlay) {
    uploadForm.addEventListener('submit', function (e) {
      if (fileInput && fileInput.files.length === 0) {
        e.preventDefault();
        alert('Please choose or drop an image file before analyzing.');
        return;
      }
      loadingOverlay.style.display = 'flex';
    });
  }
});
