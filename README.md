# 🎥 AI Video Explanation Maker

This project generates a **2–3 minute explainer video** on **"What is AI?"**, combining:

- **Text explanation** via **Google Gemini**
- **Image generation** with logic:
    1. Gemini FLASH (multimodal)
    2. Hugging Face **FLUX.1‑schnell** (free/open-source)
    3. Local placeholder image (`assets/default_ai_image.png`)
- **TTS narration** with Gemini

---

## ✅ Features

- Explains AI simply and clearly
- Multiple fallback layers for image generation
- Open-source and free-tier friendly
- Easy to customize and extend

---

## 📂 Project Structure

```
.
├── assets/
│   ├── default_ai_image.png # Local fallback image
│   └── title_slide.png # Optional title slide for video intro
├── generate_media.py # Main script (text, image, audio)
├── assemble_video.sh # Combines assets into final video
├── requirements.txt # Python dependencies
└── README.md # This file
```

---

## 🔧 Setup Instructions

1. **Install dependencies**

     ```bash
     pip install -r requirements.txt
     ```

2. **Create a .env file** in the project root with:

     ```
     GEMINI_API_KEY=your_gemini_api_key
     HF_TOKEN=hf_your_huggingface_token  # optional for HF fallback
     ```

     - Generate Gemini key from Google AI Studio
     - Generate HF token: Hugging Face → Profile → Settings → Access Tokens (read scope)

3. **Add fallback image**

     Place an image file at `assets/default_ai_image.png` to ensure image backup if remote generation fails.

4. **Run the script**

     ```bash
     python generate_media.py
     ```

     This creates:
     - `ai_explained.png`
     - `tts_audio.wav`

5. **Generate final video**

     ```bash
     bash assemble_video.sh
     ```
     
     Outputs: `output_video.mp4`

---

## 💡 Configuration Tips

- Swap out image prompts in `generate_media.py` for different AI visuals
- Customize voice via Gemini TTS options
- Add extra slides/audio segments by modifying the script and video assembly

---

## 🛠️ Troubleshooting

- Missing HF token → uses local fallback image
- Gemini FLASH image fails → HF or fallback used
- No image fallback → script raises error (add `default_ai_image.png`)
- Want higher-quality visuals? Consider premium HF models or Google Imagen

---

## 🙋‍♂️ Need Help?

I'm happy to help with:
- Prompt tuning
- Adding background music or transitions
- Multi-segment narration flow

Good luck with your video maker AI project! 😊
