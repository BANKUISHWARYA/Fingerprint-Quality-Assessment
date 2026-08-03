import streamlit as st
import cv2
import numpy as np

from quality_assessment import quality_gate

# ======================================
# Page Configuration
# ======================================

st.set_page_config(
    page_title="Fingerprint Quality Assessment",
    layout="wide"
)

st.title("🖐 Fingerprint Quality Assessment")
st.write("Upload a fingerprint image to analyze its quality.")

# ======================================
# Upload Image
# ======================================

uploaded_file = st.file_uploader(
    "Choose a fingerprint image",
    type=["jpg", "jpeg", "png"]
)

# ======================================
# Process Image
# ======================================

if uploaded_file is not None:

    file_bytes = np.asarray(
        bytearray(uploaded_file.read()),
        dtype=np.uint8
    )

    image = cv2.imdecode(
        file_bytes,
        cv2.IMREAD_COLOR
    )

    results = quality_gate(image)

    st.subheader("Original Fingerprint")

    st.image(
        image,
        channels="BGR",
        width="stretch"
    )

    st.divider()

        # ======================================
    # Quality Metrics
    # ======================================

    st.subheader("Quality Metrics")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Blur Score",
            f"{results['blur_value']:.2f}"
        )

        st.metric(
            "Brightness",
            f"{results['brightness_value']:.2f}"
        )

        st.metric(
            "Glare %",
            f"{results['glare_value']:.2f}%"
        )

    with col2:

        st.metric(
            "ROI Coverage",
            f"{results['roi_value']:.2f}%"
        )

        st.metric(
            "Ridge Clarity",
            f"{results['ridge_value']:.2f}"
        )

        st.metric(
            "Edge Pixels",
            results["edge_pixels"]
        )

    st.divider()

        # ======================================
    # Quality Analysis
    # ======================================

    st.subheader("Quality Analysis")

    col1, col2 = st.columns(2)

    with col1:

        if results["blur_quality"] == "Good":
            st.success(f"Blur: {results['blur_quality']}")
        elif results["blur_quality"] == "Average":
            st.warning(f"Blur: {results['blur_quality']}")
        else:
            st.error(f"Blur: {results['blur_quality']}")

        if results["brightness_quality"] == "Good":
            st.success(f"Brightness: {results['brightness_quality']}")
        elif results["brightness_quality"] == "Average":
            st.warning(f"Brightness: {results['brightness_quality']}")
        else:
            st.error(f"Brightness: {results['brightness_quality']}")

        if results["glare_quality"] == "Good":
            st.success(f"Glare: {results['glare_quality']}")
        elif results["glare_quality"] == "Average":
            st.warning(f"Glare: {results['glare_quality']}")
        else:
            st.error(f"Glare: {results['glare_quality']}")

    with col2:

        if results["roi_quality"] == "Good":
            st.success(f"ROI Coverage: {results['roi_quality']}")
        elif results["roi_quality"] == "Average":
            st.warning(f"ROI Coverage: {results['roi_quality']}")
        else:
            st.error(f"ROI Coverage: {results['roi_quality']}")

        if results["ridge_quality"] == "Good":
            st.success(f"Ridge Clarity: {results['ridge_quality']}")
        elif results["ridge_quality"] == "Average":
            st.warning(f"Ridge Clarity: {results['ridge_quality']}")
        else:
            st.error(f"Ridge Clarity: {results['ridge_quality']}")

    st.divider()

    # ======================================
    # Overall Score
    # ======================================

    st.subheader("Overall Quality Score")

    st.progress(results["score"] / 100)

    st.metric(
        "Composite Score",
        f"{results['score']}/100"
    )

    # ======================================
    # Decision
    # ======================================

    if results["decision"] == "PASS":
        st.success("✅ PASS - Good Quality Fingerprint")

    elif results["decision"] == "AVERAGE":
        st.warning("⚠ AVERAGE - Acceptable Quality")

    else:
        st.error("❌ FAIL - Poor Quality Fingerprint")

    st.divider()

    # ======================================
    # Guidance
    # ======================================

    st.subheader("Capture Guidance")

    for msg in results["guidance"]:
        st.info(msg)

    st.divider()

        # ======================================
    # Processed Images
    # ======================================

    st.subheader("Processed Images")

    col1, col2 = st.columns(2)

    with col1:

        st.image(
            results["mask"],
            caption="ROI Mask",
            width="stretch",
            clamp=True
        )

    with col2:

        st.image(
            results["edges"],
            caption="Edge Detection",
            width="stretch",
            clamp=True
        )

    st.write("")

    st.image(
        results["ridge_image"],
        caption="Ridge Enhancement (Gabor Filter)",
        width="stretch",
        clamp=True
    )

    st.divider()

    # ======================================
    # Summary
    # ======================================

    st.subheader("Assessment Summary")

    summary = {
        "Blur": results["blur_quality"],
        "Brightness": results["brightness_quality"],
        "Glare": results["glare_quality"],
        "ROI": results["roi_quality"],
        "Ridge": results["ridge_quality"],
        "Final Score": f"{results['score']}/100",
        "Decision": results["decision"]
    }

    st.json(summary)