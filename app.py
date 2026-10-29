
import hashlib

import streamlit as st

from image_analysis import analyze_image
from sound_generator import generate_sound


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Chromatic Echo",
    page_icon="🎨",
    layout="centered",
)

st.title("Chromatic Echo")

st.caption("Turn images into sound — Interactive Sound Artwork")

st.write(
    "Upload an image and discover how its colors, "
    "brightness, and visual patterns can become music."
)


# --------------------------------------------------
# Initialize session state
# --------------------------------------------------

if "audio_bytes" not in st.session_state:
    st.session_state["audio_bytes"] = None

if "notes" not in st.session_state:
    st.session_state["notes"] = None

if "image_id" not in st.session_state:
    st.session_state["image_id"] = None


# --------------------------------------------------
# Image upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=False,
)

if uploaded_file is None:

    st.info(
        "Upload a JPG, PNG, or WEBP image to begin "
        "(maximum 25 MB)."
    )

else:

    try:
        file_bytes = uploaded_file.getvalue()

        image, features = analyze_image(file_bytes)

        current_image_id = hashlib.sha256(
            file_bytes
        ).hexdigest()

    except ValueError as exc:

        st.error(str(exc))

        st.info(
            "Please upload a different image to try again."
        )

    else:

        # ------------------------------------------
        # Display uploaded image
        # ------------------------------------------

        st.image(
            image,
            caption="Your uploaded image",
            use_container_width=True,
        )

        st.success("Image analyzed successfully!")

        # ------------------------------------------
        # Visual analysis
        # ------------------------------------------

        st.subheader("Visual Analysis")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Brightness",
            f"{features['brightness']:.0%}",
        )

        col2.metric(
            "Saturation",
            f"{features['saturation']:.0%}",
        )

        col3.metric(
            "Hue",
            f"{features['hue'] * 360:.0f}°",
        )

        # ------------------------------------------
        # Average color
        # ------------------------------------------

        st.subheader("Average Color")

        r, g, b = features["average_rgb"]

        st.markdown(
            f'<div style="height:45px;'
            f'border-radius:8px;'
            f'background:rgb({r},{g},{b})">'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ------------------------------------------
        # Eight image regions
        # ------------------------------------------

        st.subheader("Eight Image Regions")

        st.caption(
            "The image is divided into eight vertical "
            "regions. Each region will become a musical note."
        )

        columns = st.columns(8)

        for i, (column, rgb) in enumerate(
            zip(columns, features["region_colors"])
        ):

            r, g, b = rgb

            with column:

                st.markdown(
                    f'<div style="height:42px;'
                    f'border-radius:6px;'
                    f'background:rgb({r},{g},{b})">'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.caption(str(i + 1))

        # ------------------------------------------
        # Sound generation
        # ------------------------------------------

        st.divider()

        st.subheader("Listen to Your Image")

        st.write(
            "Generate an original ambient melody based "
            "on the colors and brightness of your image."
        )

        generate_clicked = st.button(
            "🎵 Generate Sound",
            type="primary",
            use_container_width=True,
        )

        if generate_clicked:

            try:

                with st.spinner(
                    "Turning colors into sound..."
                ):

                    audio_bytes, notes = generate_sound(
                        features
                    )

                st.session_state["audio_bytes"] = (
                    audio_bytes
                )

                st.session_state["notes"] = notes

                st.session_state["image_id"] = (
                    current_image_id
                )

            except Exception as exc:

                st.error(
                    "Sound generation failed. "
                    "Please try again."
                )

                st.session_state["audio_bytes"] = None
                st.session_state["notes"] = None
                st.session_state["image_id"] = None

                # Show technical details during development.
                with st.expander("Technical details"):
                    st.exception(exc)

        # ------------------------------------------
        # Audio player
        # ------------------------------------------

        if (
            st.session_state["audio_bytes"] is not None
            and st.session_state["image_id"]
            == current_image_id
        ):

            st.success("Your sound is ready!")

            st.audio(
                st.session_state["audio_bytes"],
                format="audio/wav",
            )

            st.download_button(
                label="Download WAV",
                data=st.session_state["audio_bytes"],
                file_name="chromatic_echo.wav",
                mime="audio/wav",
                use_container_width=True,
            )

            # --------------------------------------
            # Musical note information
            # --------------------------------------

            st.subheader("Your Eight Musical Notes")

            st.caption(
                "Each note corresponds to one image "
                "region, from left to right."
            )

            for i, note in enumerate(
                st.session_state["notes"]
            ):

                st.write(
                    f"Note {i + 1}: "
                    f"{note['frequency']:.1f} Hz"
                )

            st.info(
                "Try uploading another image to hear "
                "how different colors change the music."
            )
