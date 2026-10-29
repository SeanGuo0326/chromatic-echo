
import hashlib
from io import BytesIO
import html

import streamlit as st
from PIL import Image

from image_analysis import analyze_image
from sound_generator import generate_sound, MOODS


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Chromatic Echo",
    page_icon="🎨",
    layout="centered",
)


# ==================================================
# COLOUR PALETTE
# ==================================================

COLOR_NAMES = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Cyan",
    "Blue",
    "Purple",
    "Pink",
]

COLOR_HEX = [
    "#F16B79",
    "#F4A35D",
    "#F5D86E",
    "#82D3A1",
    "#64CFD0",
    "#7298E8",
    "#B492E7",
    "#E98BC5",
]

MATERIAL_COLORS = {
    "Warm Resonance": "#F16B79",
    "Soft Bells": "#F4A35D",
    "Golden Chimes": "#F5D86E",
    "Organic Waves": "#82D3A1",
    "Air and Glass": "#64CFD0",
    "Deep Water": "#7298E8",
    "Crystal Dust": "#B492E7",
    "Dream Sparkles": "#E98BC5",
}


# ==================================================
# SESSION STATE
# ==================================================

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

if "notes" not in st.session_state:
    st.session_state.notes = None

if "generation_id" not in st.session_state:
    st.session_state.generation_id = None


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def rgb_css(rgb):
    r, g, b = rgb
    return f"rgb({int(r)}, {int(g)}, {int(b)})"


def colour_swatch(rgb, height=45):
    """
    Display a simple colour swatch.
    """
    st.markdown(
        (
            '<div style="'
            f'background:{rgb_css(rgb)};'
            f'height:{height}px;'
            'border-radius:10px;'
            '"></div>'
        ),
        unsafe_allow_html=True,
    )


def colour_bar(distribution, height=14):
    """
    Create a horizontal stacked colour bar.
    Uses a single-line HTML string to avoid
    Markdown interpreting indentation as code.
    """
    segments = []

    for index, value in enumerate(distribution):
        percentage = max(
            0.0,
            float(value) * 100.0,
        )

        if percentage <= 0:
            continue

        segments.append(
            '<div style="'
            f'width:{percentage:.4f}%;'
            f'background:{COLOR_HEX[index]};'
            'height:100%;'
            'flex-shrink:0;'
            '"></div>'
        )

    bar_html = (
        '<div style="'
        'display:flex;'
        'width:100%;'
        f'height:{height}px;'
        'border-radius:7px;'
        'overflow:hidden;'
        'background:#414552;'
        '">'
        + "".join(segments)
        + "</div>"
    )

    st.markdown(
        bar_html,
        unsafe_allow_html=True,
    )


def material_bar(layers):
    """
    Display the colour proportions
    associated with the sound materials.
    """
    segments = []

    total = 0.0

    for layer in layers:
        percentage = max(
            0.0,
            float(layer["weight"]) * 100.0,
        )

        if percentage <= 0:
            continue

        total += percentage

        material = layer["material"]

        colour = MATERIAL_COLORS.get(
            material,
            "#AAB2BD",
        )

        segments.append(
            '<div style="'
            f'width:{percentage:.4f}%;'
            f'background:{colour};'
            'height:100%;'
            'flex-shrink:0;'
            '"></div>'
        )

    remaining = max(
        0.0,
        100.0 - total,
    )

    if remaining > 0:
        segments.append(
            '<div style="'
            f'width:{remaining:.4f}%;'
            'background:#414552;'
            'height:100%;'
            'flex-shrink:0;'
            '"></div>'
        )

    st.markdown(
        (
            '<div style="'
            'display:flex;'
            'width:100%;'
            'height:14px;'
            'border-radius:7px;'
            'overflow:hidden;'
            'background:#414552;'
            '">'
            + "".join(segments)
            + "</div>"
        ),
        unsafe_allow_html=True,
    )


def show_material_card(index, note):
    """
    Compact Streamlit-based mapping card.
    """
    material = note.get(
        "material",
        "Ambient Texture",
    )

    layers = sorted(
        note.get("layers", []),
        key=lambda item: item["weight"],
        reverse=True,
    )

    with st.container(border=True):

        swatch_col, info_col = st.columns(
            [1, 6],
            vertical_alignment="center",
        )

        with swatch_col:
            colour_swatch(
                note["color"],
                height=46,
            )

        with info_col:
            st.markdown(
                f"**{index + 1:02d} — "
                f"{material}**"
            )

            st.caption(
                f'{float(note["frequency"]):.1f} Hz'
                f" · {len(layers)} sound materials"
            )

        if layers:
            material_bar(layers)

            summary = " · ".join(
                f'{layer["material"]} '
                f'{float(layer["weight"]) * 100:.1f}%'
                for layer in layers[:4]
            )

            st.caption(summary)

        else:
            st.caption(
                "Minimal chromatic information"
            )


# ==================================================
# HEADER
# ==================================================

st.title("Chromatic Echo")

st.caption(
    "An experimental image-to-sound experience"
)

st.write(
    "Upload an image and explore how its "
    "colours, brightness, and visual structure "
    "can become an evolving soundscape."
)


# ==================================================
# IMAGE UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "Upload an image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
    help="Choose a JPG, PNG, or WEBP image.",
)


if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    try:
        image, features = analyze_image(
            file_bytes
        )

    except ValueError as error:
        st.error(str(error))
        st.stop()

    except Exception:
        st.error(
            "The image could not be analysed. "
            "Please try another image."
        )
        st.stop()

    image_id = hashlib.sha256(
        file_bytes
    ).hexdigest()

    st.image(
        image,
        caption="Your uploaded image",
        width="stretch",
    )

    # ==============================================
    # SCAN DIRECTION
    # ==============================================

    st.subheader("Scan Direction")

    scan_direction = st.radio(
        "Choose how the image is read",
        options=["Left to Right", "Top to Bottom"],
        horizontal=True,
    )

    if scan_direction == "Top to Bottom":
        # A 90-degree counterclockwise rotation maps the
        # original top-to-bottom rows onto left-to-right columns.
        # The uploaded image displayed above stays unchanged.
        rotated = image.transpose(Image.Transpose.ROTATE_90)
        rotated_buffer = BytesIO()
        rotated.save(rotated_buffer, format="PNG")
        _, features = analyze_image(rotated_buffer.getvalue())

    # ==============================================
    # IMAGE ANALYSIS
    # ==============================================

    st.header("Image Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Brightness",
            f'{features["brightness"] * 100:.0f}%',
        )

    with col2:
        st.metric(
            "Saturation",
            f'{features["saturation"] * 100:.0f}%',
        )

    with col3:
        st.metric(
            "Hue",
            f'{features["hue"] * 360:.0f}°',
        )

    # ==============================================
    # COLOUR DISTRIBUTION
    # ==============================================

    st.subheader("Colour Distribution")

    st.write(
        "Instead of reducing the image to a "
        "single average colour, Chromatic Echo "
        "measures the proportion of different "
        "hue families."
    )

    distribution = features[
        "color_distribution"
    ]

    colour_bar(
        distribution,
        height=22,
    )

    colour_columns = st.columns(4)

    names = features.get(
        "color_names",
        COLOR_NAMES,
    )

    for index, name in enumerate(names):

        with colour_columns[index % 4]:

            st.markdown(
                (
                    f'<span style="color:{COLOR_HEX[index]}">'
                    "●</span> "
                    f"{html.escape(str(name))}: "
                    f"{float(distribution[index]) * 100:.1f}%"
                ),
                unsafe_allow_html=True,
            )

    st.metric(
        "Colour Diversity",
        f'{features["color_diversity"] * 100:.0f}%',
    )

    st.caption(
        "Colour Diversity measures how evenly "
        "the eight hue families are represented. "
        "It does not measure the number of "
        "individual RGB colours."
    )

    # ==============================================
    # COLOUR JOURNEY
    # ==============================================

    st.subheader(f"Colour Journey — {scan_direction}")

    st.write(
        "Each scan region contains a distribution of colours, "
        "not just one average colour. The eight regions follow "
        "your selected scan direction."
    )

    for index, region in enumerate(
        features["region_distributions"]
    ):

        label_col, bar_col = st.columns(
            [1, 5],
            vertical_alignment="center",
        )

        with label_col:
            st.caption(
                f"Region {index + 1}"
            )

        with bar_col:
            colour_bar(
                region,
                height=14,
            )

    # ==============================================
    # SOUND CONTROLS
    # ==============================================

    st.divider()

    st.header("Create Your Soundscape")

    mood = st.selectbox(
        "Sound Mode",
        options=list(MOODS.keys()),
        index=0,
    )

    st.caption(
        MOODS[mood]
    )

    intensity_percent = st.slider(
        "Texture Intensity",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
    )

    intensity = (
        intensity_percent / 100.0
    )

    generation_id = (
        image_id,
        scan_direction,
        mood,
        intensity_percent,
    )

    generate_clicked = st.button(
        "🎵 Generate Soundscape",
        type="primary",
        width="stretch",
    )

    # ==============================================
    # GENERATE SOUND
    # ==============================================

    if generate_clicked:

        try:
            with st.spinner(
                "Transforming colours into sound..."
            ):

                audio_bytes, notes = generate_sound(
                    features,
                    mood=mood,
                    intensity=intensity,
                )

            st.session_state.audio_bytes = (
                audio_bytes
            )

            st.session_state.notes = notes

            st.session_state.generation_id = (
                generation_id
            )

        except Exception as error:

            st.session_state.audio_bytes = None
            st.session_state.notes = None
            st.session_state.generation_id = None

            st.error(
                "Sound generation failed."
            )

            with st.expander(
                "Technical details"
            ):
                st.code(str(error))

    # ==============================================
    # AUDIO PLAYBACK
    # ==============================================

    audio_is_current = (
        st.session_state.audio_bytes
        is not None
        and st.session_state.notes
        is not None
        and st.session_state.generation_id
        == generation_id
    )

    if audio_is_current:

        st.success(
            "Your soundscape is ready!"
        )

        st.audio(
            st.session_state.audio_bytes,
            format="audio/wav",
        )

        st.download_button(
            "Download WAV",
            data=st.session_state.audio_bytes,
            file_name="chromatic_echo.wav",
            mime="audio/wav",
            width="stretch",
        )

        # ==========================================
        # IMAGE-TO-SOUND MAPPING
        # ==========================================

        st.subheader(
            "Image-to-Sound Mapping"
        )

        st.caption(
            "Explore how colours become layered "
            "sound materials. Each region represents "
            f"a moment in the image's {scan_direction.lower()} "
            "sonic journey."
        )

        for index, note in enumerate(
            st.session_state.notes
        ):

            show_material_card(
                index,
                note,
            )

    elif (
        st.session_state.audio_bytes
        is not None
    ):

        st.info(
            "The image or sound settings have "
            "changed. Click Generate Soundscape "
            "to create a new result."
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Chromatic Echo · "
    "Experimental Image Sonification · "
    "SD5913"
)
