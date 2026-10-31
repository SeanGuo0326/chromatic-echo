# PROCESS — Chromatic Echo

## 1. Initial Concept

Chromatic Echo began with a question: *What if we could listen to an image instead of only looking at it?*

As someone with a background in animation and visual arts, I am interested in how different media communicate atmosphere and emotion. I wanted to explore whether the visual characteristics of an image could be translated into a musical and experimental sound experience.

The intended users are people interested in photography, visual art, and experimental sound. They can upload an image, listen to a soundscape generated from its visual characteristics, and explore how different ways of reading an image affect what they hear.

Rather than relying on an external AI music-generation service, I chose image analysis and procedural sound synthesis. This allows the relationship between visual input and audio output to remain transparent, reproducible, and open to experimentation.

## 2. Iteration 1 — Image Upload and Visual Analysis

The first prototype focused on establishing a working interaction using Python and Streamlit.

I implemented an image uploader and used Pillow and NumPy to analyse brightness, saturation, hue, average colour, and the average colours of eight vertical image regions.

I divided the image into eight regions because I wanted its spatial composition to influence the eventual sound, rather than using only one overall average colour.

### Problem Encountered

During testing, I uploaded a high-resolution photograph, but the application rejected it because the file exceeded the original 10 MB limit.

The program displayed an error message instead of crashing, demonstrating that basic error handling worked. However, the restriction was too limiting for some digital photographs.

### Design Decision and Result

I increased the maximum file size to 25 MB while retaining image resizing during analysis to control processing costs.

After restarting the application, I successfully uploaded the photograph and confirmed that the analysis worked.

This demonstrated the importance of designing technical constraints around the materials users are likely to provide.

## 3. Iteration 2 — Translating Images into Sound

The second iteration established the central interaction.

I developed a sound-generation module using NumPy and Python's wave library. The initial system translated eight image regions into eight musical notes, using image characteristics to influence pitch and sound.

I also implemented a Generate Sound button, an audio player, a WAV download option, and information about the generated notes.

The main interaction became:

**Image Upload → Visual Analysis → Sound Generation → Listening**

### Initial Sound Evaluation

I tested the prototype with a relatively dark photograph containing warm brown tones.

The resulting sound was low-pitched and subdued. I felt that its atmosphere suited the image, suggesting that the initial mapping had expressive potential.

However, several notes had the same frequency, creating a repetitive musical sequence.

### Design Decision

Instead of simply increasing the pitch range, I wanted to preserve the relationship between the image's atmosphere and the generated sound.

I decided to move towards layered ambient textures and experimental sound materials rather than conventional melody generation.

## 4. Iteration 3 — Improving Colour Recognition and Sound Diversity

During further testing, I noticed that different images often produced similar sounds.

I tested a colourful rainbow illustration and found that the original analysis did not adequately represent its visual diversity. The system relied heavily on average colours, so regions containing different combinations of colours could produce almost identical notes.

### Design Decision

I revised the image analysis to calculate the distribution of eight hue families:

- Red
- Orange
- Yellow
- Green
- Cyan
- Blue
- Purple
- Pink

I also introduced overall and regional colour-diversity measurements.

Instead of representing each region through only one frequency, the sound engine could now combine multiple sound materials according to the proportions of different colours.

Each colour family was assigned an artistic sound identity, such as Warm Resonance, Organic Waves, Air and Glass, or Crystal Dust. These mappings are expressive design choices, not claims that colours possess scientifically corresponding musical frequencies.

### Testing and Result

I tested the revised system with a colourful illustration featuring an elephant and a giraffe.

The analysis represented more of the colours within each region, and the generated sound contained noticeably more variation.

This was an improvement over the earlier repetitive output, although the connection between visual information and audio still needed to be communicated more clearly.

## 5. Iteration 4 — Making the Mapping Visible

Although the sound generation had improved, I noticed that the interface did not clearly explain how the image influenced the audio.

The user could hear a sound, but the underlying relationship between image regions, colours, and sound materials was difficult to understand.

### Design Decision

I redesigned the Image-to-Sound Mapping section to display:

- The dominant sound material for each region.
- A representative frequency.
- The proportions of contributing sound materials.
- Coloured bars illustrating the distribution.

This allowed the interface to communicate the logic behind the sound rather than presenting the result as an unexplained transformation.

### Problem Encountered

During implementation, an HTML rendering issue caused raw code to appear in the interface instead of the intended visual elements.

I revised the display implementation and tested it again until the information appeared correctly as compact visual cards.

### Result

The interface became more informative and visually connected to the artwork.

I learned that transparency can be part of the aesthetic experience: showing how a system interprets an image can encourage users to experiment rather than simply accept the generated result.

## 6. Iteration 5 — Exploring Scan Direction

After improving the colour analysis and visual mapping, I wanted to give users more control over how an image was interpreted.

Previously, the program analysed eight vertical regions from left to right. However, an image can also be experienced as a sequence from top to bottom.

I introduced two scanning directions:

**Left to Right** — Eight vertical regions.

**Top to Bottom** — Eight horizontal regions.

This changed the interaction from a single fixed interpretation into a small experiment in visual reading.

### Testing and Observation

I tested both directions using the same colourful illustration.

When scanning from top to bottom, the early regions contained substantial cyan and blue, while later regions were more strongly influenced by orange and yellow.

When scanning from left to right, orange was dominant across more regions, with different contributions from other colours.

The overall brightness, saturation, and colour diversity remained the same because the uploaded image had not changed. However, the regional colour distributions changed significantly.

### Design Reflection

This test demonstrated that the order in which visual information is interpreted can change the resulting representation.

I was interested in this not only as a technical feature but also as an artistic question: *Does an image have one fixed sound, or can different ways of reading it create different experiences?*

## 7. Iteration 6 — Making the Soundscape Evolve

Although the two scanning directions produced different colour distributions, I wanted the difference to become more perceptible through listening.

The previous sound engine already used different timbres and colour-dependent envelopes, but much of the audio consisted of continuous oscillating tones. This could make the overall sound feel relatively stable, even when the underlying region data changed.

### Design Decision

I revised the sound-generation approach to introduce more distinct changes over time.

Rather than relying primarily on continuous sound layers, the updated version uses evolving sound events associated with the sequence of image regions.

The intention was to make the order of the visual scan more audible while preserving the dreamy and experimental character of the work.

I retained the three sound modes — Echo, Flow, and Pulse — and the Texture Intensity control.

### Testing and Result

I replaced the sound-generation module and tested the application locally.

The application successfully generated and played audio. During listening tests, I found that the sounds produced by different scanning directions were now noticeably different.

This was an important improvement because the scanning control had become meaningful not only in the visual analysis but also in the resulting listening experience.

The test was my own evaluation; it does not yet establish whether another user will perceive or understand the difference independently.

## 8. AI Assistance and Design Decisions

I used ChatGPT throughout development to help plan the application, explain technical concepts, draft and revise Python code, troubleshoot errors, and structure the project documentation.

AI assistance was particularly useful when developing the image-analysis functions, procedural audio synthesis, Streamlit interface, and the connection between these components.

I chose to keep image analysis and sound generation in separate modules because this made the program easier to understand, test, and modify.

However, I did not automatically accept every proposed design direction.

For example, when the early sounds were repetitive, I did not want to solve the problem simply by introducing more random notes. I preferred to develop richer textures that could preserve the visual atmosphere of an image.

Similarly, when a colourful image produced insufficient sonic variation, I focused on improving how the image was analysed rather than adding arbitrary musical complexity.

I tested the code locally, examined the interface, listened to the generated audio, and used those observations to guide subsequent changes.

The final application uses procedural synthesis rather than an AI music-generation model. AI was a development assistant, not the system generating the final sound at runtime.

## 9. User Testing and Feedback

I conducted a usability test with a fellow student to evaluate whether Chromatic Echo communicated its intended relationship between images and sound.

The participant was asked three questions about the experience.

**1. What relationship do you notice between the uploaded image and the generated sound?**

The participant felt that the image and sound were connected through their overall style and atmosphere.

**2. Can you hear a difference between the two scanning directions?**

The participant confirmed that the two scanning directions produced noticeably different sounds.

**3. Which feature was confusing, and what would you improve?**

The participant found the colour-block visualization confusing and suggested introducing a wider variety of instrumental sounds.

### Reflection and Design Decisions

The feedback suggested that the project was successful in communicating an atmospheric relationship between images and audio. It also supported my earlier observation that scanning direction could create meaningful differences in the listening experience.

However, the participant's confusion about the colour blocks revealed a usability problem. Although the interface displayed detailed colour distributions, their purpose was not immediately clear.

Based on this feedback, I decided to prioritize a clearer explanation of the colour-to-sound mapping, using accessible language to describe what each colour block represents.

The suggestion to include more instrumental variety is also valuable. However, because the current system already uses eight procedural sound materials, I decided to retain the existing synthesis architecture for this version and consider additional instrumental textures as a future development.

This test reminded me that an interactive experience must not only produce interesting results but also communicate how users can interpret and explore them.
### Implemented Improvement

Following the participant's feedback, I improved the Colour Journey interface to make the colour-block visualization easier to understand.

I added a short explanation describing how the image is divided into eight scanning regions and how the colour proportions influence the evolving soundscape. I also introduced a colour legend identifying the eight hue families and an expandable section explaining how different colours correspond to synthesized sound materials.

After implementing these changes, I reopened the application and checked the updated interface. The explanations, colour legend, and eight regional bars displayed correctly.

This iteration demonstrated how user feedback can lead to a focused usability improvement without requiring a complete redesign of the application.
## 10. Current Reflection

Developing Chromatic Echo has changed how I think about interactive artwork.

Initially, I focused on whether a computer could translate an image into sound. As development progressed, I realized that a technically functioning transformation is not necessarily a meaningful experience.

The first version could generate notes, but different images often sounded too similar. Improving colour recognition made the system more responsive to visual differences. Making the mapping visible helped communicate its internal logic. Introducing scan direction gave users a way to explore alternative interpretations, while evolving sound events made those interpretations more audible.

The project also reinforced the importance of testing through actual experience. Several important design decisions emerged only after I uploaded photographs and illustrations, examined the output, and listened critically.

For me, the most interesting outcome is not the idea that every image has a correct musical equivalent. Instead, Chromatic Echo treats translation between visual and auditory media as an artistic interpretation shaped by both the image and the user's choices.