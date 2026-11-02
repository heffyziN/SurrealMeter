import base64
import logging
import warnings
from io import BytesIO

from django.shortcuts import render
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import Artwork

logger = logging.getLogger(__name__)
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
ARTIST_NAMES = {
    "dali": "Сальвадор Дали",
    "magritte": "Рене Магритт",
    "ernst": "Макс Эрнст",
    "miro": "Жоан Миро",
}
ARTIST_LABELS = {
    "dali": "Дали",
    "magritte": "Магритт",
    "ernst": "Эрнст",
    "miro": "Миро",
    "other": "Другое",
}


def _load_image(uploaded_file):
    """Validate an uploaded image and return a normalized PIL image and its bytes."""
    if uploaded_file.size > MAX_IMAGE_BYTES:
        raise ValueError("Размер изображения не должен превышать 10 МБ.")
    raw = uploaded_file.read()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as probe:
                image_format = (probe.format or "").upper()
                if image_format not in ALLOWED_FORMATS:
                    raise ValueError("Поддерживаются изображения JPEG, PNG и WEBP.")
                if probe.width * probe.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Слишком большое разрешение изображения.")
                probe.verify()
            with Image.open(BytesIO(raw)) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise ValueError("Не удалось прочитать изображение. Проверьте файл и попробуйте снова.") from exc
    return image, raw, image_format


def index(request):
    if request.method != "POST":
        return render(request, "index.html")

    uploaded_file = request.FILES.get("image")
    if uploaded_file is None:
        return render(request, "index.html", {"error": "Выберите изображение для анализа."})

    try:
        image, raw, image_format = _load_image(uploaded_file)
        # Load the ML model only when a user submits an image.
        from .ml.classifier import classify_image
        scores = classify_image(image)

        artist_scores = {key: float(scores.get(key, 0.0)) for key in ARTIST_NAMES}
        top_label = max(artist_scores, key=artist_scores.get)
        top_score = artist_scores[top_label]
        other_score = float(scores.get("other", 0.0))
        is_surreal = other_score <= 50.0 and top_score >= 40.0
        warning_message = (
            "Классификатор не определил достаточно уверенное сходство с одним из выбранных "
            "художественных стилей. Результат следует рассматривать как ориентировочную оценку."
        )

        percentages = {
            ARTIST_LABELS[key]: round(float(scores.get(key, 0.0)), 1)
            for key in ("dali", "magritte", "ernst", "miro", "other")
        }
        mime_types = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
        uploaded_img_uri = (
            f"data:{mime_types[image_format]};base64,{base64.b64encode(raw).decode('ascii')}"
        )
        similar_paintings = []
        if is_surreal:
            similar_paintings = list(Artwork.objects.filter(style_tag=top_label).order_by("id")[:4])

        context = {
            "uploaded_img_uri": uploaded_img_uri,
            "top_artist": ARTIST_NAMES[top_label],
            "top_label": top_label,
            "winner_label": ARTIST_LABELS[top_label],
            "percentages": percentages,
            "is_surreal": is_surreal,
            "warning_message": warning_message,
            "similar_paintings": similar_paintings,
        }
        return render(request, "results.html", context)
    except ValueError as exc:
        return render(request, "index.html", {"error": str(exc)})
    except Exception:
        logger.exception("Image classification failed")
        return render(request, "index.html", {
            "error": "Не удалось выполнить анализ. Проверьте зависимости и доступность модели CLIP."
        })
