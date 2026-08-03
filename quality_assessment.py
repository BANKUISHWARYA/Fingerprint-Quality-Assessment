import cv2
import numpy as np

# -----------------------------
# Blur Detection
# -----------------------------
def blur_score(gray):
    score = cv2.Laplacian(gray, cv2.CV_64F).var()

    if score > 150:
        quality = "Good"
    elif score > 80:
        quality = "Average"
    else:
        quality = "Poor"

    return score, quality


# -----------------------------
# Brightness
# -----------------------------
def brightness_score(gray):
    value = np.mean(gray)

    if 80 <= value <= 180:
        quality = "Good"
    elif 60 <= value < 80 or 180 < value <= 210:
        quality = "Average"
    else:
        quality = "Poor"

    return value, quality


# -----------------------------
# Glare Detection
# -----------------------------
def glare_score(gray):
    glare_pixels = np.sum(gray > 240)

    glare_percent = (
        glare_pixels /
        gray.size
    ) * 100

    if glare_percent < 2:
        quality = "Good"
    elif glare_percent < 5:
        quality = "Average"
    else:
        quality = "Poor"

    return glare_percent, quality


# -----------------------------
# ROI Completeness
# -----------------------------
def roi_score(gray):

    _, mask = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    roi_pixels = cv2.countNonZero(mask)

    percent = (
        roi_pixels /
        gray.size
    ) * 100

    if percent > 60:
        quality = "Good"
    elif percent > 40:
        quality = "Average"
    else:
        quality = "Poor"

    return percent, quality, mask


# -----------------------------
# Ridge Clarity (Gabor Filter)
# -----------------------------
def ridge_score(gray):

    kernel = cv2.getGaborKernel(
        (21, 21),
        5,
        np.pi / 4,
        10,
        0.5,
        0,
        ktype=cv2.CV_32F
    )

    filtered = cv2.filter2D(
        gray,
        cv2.CV_8UC3,
        kernel
    )

    score = filtered.std()

    if score > 40:
        quality = "Good"
    elif score > 20:
        quality = "Average"
    else:
        quality = "Poor"

    return score, quality, filtered


# -----------------------------
# Edge Detection
# -----------------------------
def edge_detection(gray):

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    edge_pixels = cv2.countNonZero(edges)

    return edges, edge_pixels


# -----------------------------
# Composite Score
# -----------------------------
def composite_score(results):

    score = 0

    # Blur (25)

    if results["blur"] == "Good":
        score += 25
    elif results["blur"] == "Average":
        score += 15

    # Brightness (15)

    if results["brightness"] == "Good":
        score += 15
    elif results["brightness"] == "Average":
        score += 8

    # Glare (15)

    if results["glare"] == "Good":
        score += 15
    elif results["glare"] == "Average":
        score += 8

    # ROI (20)

    if results["roi"] == "Good":
        score += 20
    elif results["roi"] == "Average":
        score += 10

    # Ridge (25)

    if results["ridge"] == "Good":
        score += 25
    elif results["ridge"] == "Average":
        score += 15

    return score


# -----------------------------
# Guidance
# -----------------------------
def generate_guidance(results):

    messages = []

    if results["blur"] == "Poor":
        messages.append("Image is blurry. Hold the camera steady.")

    if results["brightness"] == "Poor":
        messages.append("Adjust lighting.")

    if results["glare"] == "Poor":
        messages.append("Reduce reflections on the finger.")

    if results["roi"] == "Poor":
        messages.append("Place the complete finger inside the frame.")

    if results["ridge"] == "Poor":
        messages.append("Fingerprint ridges are unclear.")

    if len(messages) == 0:
        messages.append("Fingerprint quality is good.")

    return messages


# -----------------------------
# Complete Assessment
# -----------------------------
def quality_gate(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blur_value, blur_quality = blur_score(gray)

    brightness_value, brightness_quality = brightness_score(gray)

    glare_value, glare_quality = glare_score(gray)

    roi_value, roi_quality, mask = roi_score(gray)

    ridge_value, ridge_quality, ridge = ridge_score(gray)

    edges, edge_pixels = edge_detection(gray)

    metric_results = {
        "blur": blur_quality,
        "brightness": brightness_quality,
        "glare": glare_quality,
        "roi": roi_quality,
        "ridge": ridge_quality
    }

    final_score = composite_score(metric_results)

    if final_score >= 80:
        decision = "PASS"

    elif final_score >= 60:
        decision = "AVERAGE"

    else:
        decision = "FAIL"

    guidance = generate_guidance(metric_results)

    return {

        "blur_value": blur_value,
        "brightness_value": brightness_value,
        "glare_value": glare_value,
        "roi_value": roi_value,
        "ridge_value": ridge_value,

        "blur_quality": blur_quality,
        "brightness_quality": brightness_quality,
        "glare_quality": glare_quality,
        "roi_quality": roi_quality,
        "ridge_quality": ridge_quality,

        "edge_pixels": edge_pixels,

        "score": final_score,

        "decision": decision,

        "guidance": guidance,

        "mask": mask,

        "edges": edges,

        "ridge_image": ridge
    }