
import streamlit as st

from image_analysis import analyze_image

st.set_page_config(
    page_title="Chromatic Echo",
    page_icon="🎨",
    layout="centered",
)

st.title("Chromatic Echo")
st.caption("Turn images into sound — Stage 1: visual analysis")

st.write(
    "Upload an image to discover the visual features "
    "that will shape its sound."
)

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file is None:
    st.info(
        "Upload a JPG, PNG, or WEBP image to begin "
        "(maximum 10 MB)."
    )

else:
    try:
        image, features = analyze_image(uploaded_file.getvalue())

    except ValueError as exc:
        st.error(str(exc))
        st.info("Please upload a different image to try again.")

    else:
        st.image(
            image,
            caption="Your uploaded image",
            use_container_width=True,
        )

        st.success("Image analyzed successfully!")

        a, b, c = st.columns(3)

        a.metric("Brightness", f"{features['brightness']:.0%}")
        b.metric("Saturation", f"{features['saturation']:.0%}")
        c.metric("Hue", f"{features['hue'] * 360:.0f}°")

        st.subheader("Average color")

        r, g, b = features["average_rgb"]

        st.markdown(
            f'<div style="height:40px;border-radius:8px;'
            f'background:rgb({r},{g},{b})"></div>',
            unsafe_allow_html=True,
        )

        st.subheader("Eight image regions")

        st.caption(
            "Left to right — these colors will help create "
            "an eight-note melody in Stage 2."
        )

        cols = st.columns(8)

        for i, (col, rgb) in enumerate(
            zip(cols, features["region_colors"])
        ):
            r, g, b = rgb

            with col:
                st.markdown(
                    f'<div style="height:42px;border-radius:6px;'
                    f'background:rgb({r},{g},{b})"></div>',
                    unsafe_allow_html=True,
                )
                st.caption(str(i + 1))

        st.info(
            "Next stage: map these visual features "
            "to a playable sound."
        )
