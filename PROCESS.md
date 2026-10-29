# PROCESS — Chromatic Echo

## 1. Initial Concept

Chromatic Echo began with a question: *What if we could listen to an image instead of only looking at it?*

As someone with a background in animation and visual arts, I am interested in how different media can communicate atmosphere and emotion. I wanted to explore whether the visual qualities of an image could be translated into a musical experience.

The intended users are people interested in photography, visual art, and experimental sound. They can upload an image, listen to a sound generated from its visual characteristics, and explore the relationship between what they see and what they hear.

Rather than relying on a paid AI music-generation service, I chose to experiment with image analysis and procedural sound synthesis. This approach allows the relationship between visual input and audio output to be more transparent and reproducible.

## 2. Iteration 1 — Image Upload and Visual Analysis

My first prototype focused on creating a working interaction using Python and Streamlit.

I implemented an image uploader and used Pillow and NumPy to analyse the uploaded image. The program calculates brightness, saturation, hue, average colour, and the average colours of eight vertical image regions.

I divided the image into eight regions because I wanted the spatial arrangement of colours to influence the eventual musical sequence, rather than relying only on the overall average colour.

### Problem Encountered

During initial testing, I attempted to upload a high-resolution photograph, but the application rejected it because the file exceeded the original 10 MB limit.

The program displayed an error message instead of crashing, which showed that the error handling was working. However, the limit was too restrictive for some photographs taken with digital cameras.

### Design Decision

I increased the file-size limit from 10 MB to 25 MB and retained image resizing during analysis to reduce processing costs.

After restarting the application, I successfully uploaded the photograph and confirmed that the visual analysis worked.

This experience reminded me that technical constraints should be considered in relation to the materials users are likely to provide.

## 3. Iteration 2 — Translating Images into Sound

The second iteration focused on creating the main interactive response.

I developed a sound-generation module using NumPy and Python's wave library. The application maps the colours of eight image regions to a sequence of eight musical notes.

The overall hue influences the tonal centre, brightness influences the pitch register, and saturation affects the harmonic content of the synthesized sound.

I also added a Generate Sound button, an audio player, a WAV download option, and information about the generated notes.

This established the main interaction loop:

**Image Upload → Visual Analysis → Sound Generation → Listening and Feedback**

### Initial Sound Evaluation

I tested the program with a relatively dark photograph containing warm brown tones.

The resulting sound was low-pitched and subdued. I felt that this atmosphere suited the image, suggesting that the initial mapping produced a meaningful relationship between the visual input and the audio output.

However, I also noticed that several generated notes had the same frequency, resulting in limited melodic variation.

### Design Decision

Rather than immediately increasing the pitch range, I decided to preserve the relationship between the image's visual atmosphere and the generated sound.

For the next iteration, I plan to explore richer sound textures and more subtle musical variation while maintaining the influence of the original image.

## 4. AI Assistance

I used ChatGPT during the development process to help structure the project, understand technical concepts, draft Python code, and troubleshoot implementation problems.

AI assistance was particularly useful for organizing the image-analysis and sound-generation functions and connecting them to the Streamlit interface.

I kept the suggestion to separate image analysis and sound synthesis into different Python modules because it made the program easier to understand and modify.

However, I did not want to prioritize melodic complexity simply for the sake of producing more notes. Based on my initial listening experience, I decided that preserving the atmosphere of the uploaded image was more important than maximizing musical variation.

I tested the generated code locally, observed the results, and made decisions based on the behaviour of the application and my own artistic intentions.

## 5. Next Steps — Planned Iteration

The next stage will focus on improving the musical experience and adding more meaningful user controls.

Planned improvements include:

- Developing richer ambient sound textures.
- Introducing subtle melodic variation.
- Adding user-adjustable sound parameters.
- Improving the visual explanation of the image-to-sound mapping.
- Testing the experience with another person and making a design decision based on their observations.

These improvements have not yet been completed.

## 6. User Testing — Pending

A user trial with at least one other person will be conducted after the next interactive prototype is ready.

The trial will examine whether users understand the controls, recognize the relationship between images and sound, and know how to modify or restart the experience.

Observations, design decisions, and resulting changes will be documented here after the trial.

## 7. Final Reflection — To Be Completed

This section will be completed after the final implementation and user testing.

## 8. Iteration 3 — Improving Colour Recognition and Sound Diversity

During testing, I noticed that different images often produced very similar sounds. Although the initial sound engine worked technically, the results were frequently low-pitched and repetitive. This made the relationship between the uploaded image and the generated sound difficult to perceive.

I also tested a colourful rainbow illustration and discovered that the system was not adequately representing its visual diversity. The early approach relied heavily on average colours and a single representative frequency for each image region. As a result, visually different areas could produce almost identical notes.

To address this, I revised the image analysis to calculate colour distributions across eight hue families rather than relying only on average colours. I also introduced colour diversity measurements and regional distributions to better represent images containing multiple colours.

The sound generation system was then developed to use different sound materials, allowing colour combinations to contribute to a more layered and experimental soundscape.

After these changes, I tested another colourful illustration featuring an elephant and a giraffe. The resulting sound showed noticeably more variation, suggesting that the revised approach was more successful in translating visual differences into audible changes.

## 9. Iteration 4 — Making the Image-to-Sound Relationship Visible

Although the sound generation had improved, I found that the interface still did not clearly communicate how the image influenced the audio.

I therefore redesigned the Image-to-Sound Mapping section to display the dominant sound material, representative frequency, and proportions of contributing sound materials for each region.

During implementation, an HTML rendering issue caused raw code to appear in the interface instead of the intended visual components. I revised the display implementation and tested it again until the information appeared correctly as compact visual cards with coloured proportion bars.

This iteration improved the transparency of the interaction by helping users understand why different parts of an image contribute different sound textures.

## 10. Reflection and Next Steps

These iterations showed me that technical functionality alone is not enough for an interactive artwork. The relationship between user input and system output must also be perceptible and understandable.

My next planned improvement is to introduce alternative image-scanning directions, allowing users to explore how reading an image from left to right or from top to bottom changes the resulting soundscape.

A user test with another person is still required. I will document their observations and any resulting design changes after the test has been completed.