# # import os
# # from dotenv import load_dotenv
# # from google import genai
# # from google.genai import types
# # import wave

# # load_dotenv()
# # api_key = os.getenv("GEMINI_API_KEY")
# # client = genai.Client(api_key=api_key)

# # def save_audio(path, pcm):
# #     with wave.open(path, "wb") as wf:
# #         wf.setnchannels(1)
# #         wf.setsampwidth(2)
# #         wf.setframerate(24000)
# #         wf.writeframes(pcm)

# # # 1. Generate explanation text + image
# # text_resp = client.models.generate_content(
# #     model="gemini-2.5-flash",
# #     contents="Explain what AI is in simple terms and generate an illustration concept.",
# #     config=types.GenerateContentConfig()
# # )
# # explanation = text_resp.text
# # print("Explanation text:", explanation)

# # # 2. Generate image based on concept
# # img_resp = client.models.generate_content(
# #     model="gemini-2.0-flash-preview-image-generation",
# #     contents=f"Illustration of: {explanation.split('.')[0]}",
# #     config=types.GenerateContentConfig(response_modalities=["IMAGE"])
# # )
# # img_url = img_resp.image.uri  # You can download this image programmatically
# # print("Image URL:", img_url)

# # # 3. Generate TTS audio
# # tts_resp = client.models.generate_content(
# #     model="gemini-2.5-flash-preview-tts",
# #     contents=explanation,
# #     config=types.GenerateContentConfig(
# #         response_modalities=["AUDIO"],
# #         speech_config=types.SpeechConfig(
# #             voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore"))
# #         )
# #     )
# # )
# # save_audio("tts_audio.wav", tts_resp.audio.pcm)
# # print("Audio saved to tts_audio.wav")


# import os
# import wave
# from io import BytesIO
# from PIL import Image
# from dotenv import load_dotenv
# from google import genai
# from google.genai import types

# # Load API key
# load_dotenv()
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# def save_audio(path, pcm_bytes):
#     with wave.open(path, "wb") as wf:
#         wf.setnchannels(1)
#         wf.setsampwidth(2)
#         wf.setframerate(24000)
#         wf.writeframes(pcm_bytes)

# # 1️⃣ FLASH multimodal call (TEXT + IMAGE)
# text, img_saved = "", False
# resp = client.models.generate_content(
#     model="gemini-2.0-flash-preview-image-generation",
#     contents="Explain Artificial Intelligence simply and generate an illustrative image.",
#     config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
# )

# for part in resp.candidates[0].content.parts:
#     if part.text:
#         text += part.text
#     if part.inline_data and part.inline_data.data and not img_saved:
#         try:
#             img = Image.open(BytesIO(part.inline_data.data))
#             img.save("ai_explained.png")
#             print("✅ FLASH image saved: ai_explained.png")
#             img_saved = True
#         except Exception:
#             print("⚠️ FLASH image invalid, will fallback")

# # 2️⃣ Fallback to Imagen (if FLASH failed)
# if not img_saved:
#     try:
#         print("🔄 Attempting fallback via Imagen...")
#         img_resp = client.models.generate_images(
#             model="imagen-4.0-generate-preview-06-06",
#             prompt="Friendly robot AI illustration: input → processing → output",
#             config=types.GenerateImagesConfig(number_of_images=1)
#         )
#         img_bytes = img_resp.generated_images[0].image.image_bytes
#         img = Image.open(BytesIO(img_bytes))
#         img.save("ai_explained.png")
#         print("✅ Imagen image saved: ai_explained.png")
#         img_saved = True
#     except Exception as e:
#         print("⚠️ Imagen failed (billing or access issue):", str(e))

# # 3️⃣ Use local default image if both fail
# if not img_saved:
#     fallback_path = "assets/default_ai_image.png"
#     if os.path.exists(fallback_path):
#         Image.open(fallback_path).save("ai_explained.png")
#         print("ℹ️ Using local default image:", fallback_path)
#     else:
#         raise FileNotFoundError(
#             "No valid generated image, and default fallback not found at " + fallback_path
#         )

# # 4️⃣ Generate TTS audio using the explanation text
# tts_resp = client.models.generate_content(
#     model="gemini-2.5-flash-preview-tts",
#     contents=text,
#     config=types.GenerateContentConfig(
#         response_modalities=["AUDIO"],
#         speech_config=types.SpeechConfig(
#             voice_config=types.VoiceConfig(
#                 prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
#             )
#         )
#     )
# )
# pcm = tts_resp.candidates[0].content.parts[0].audio.pcm
# save_audio("tts_audio.wav", pcm)
# print("✅ TTS audio saved: tts_audio.wav")

# # Summary
# print(f"\n🖼️ Image file: ai_explained.png")
# print(f"🔊 Audio file: tts_audio.wav")
# print("📄 Explanation preview:", text.strip()[:100].replace("\n", " "), "…")















import os
import wave
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
from huggingface_hub import InferenceClient

# Load env keys
load_dotenv()
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
hf = None
if os.getenv("HF_TOKEN"):
    hf = InferenceClient(provider="fal-ai", api_key=os.getenv("HF_TOKEN"))

def save_audio(path, pcm_bytes):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm_bytes)

# 1️⃣ Generate explanation + image via Gemini FLASH
text, img_saved = "", False
resp = gemini.models.generate_content(
    model="gemini-2.0-flash-preview-image-generation",
    contents="Explain Artificial Intelligence simply and generate an illustrative image.",
    config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
)

for part in resp.candidates[0].content.parts:
    if part.text:
        text += part.text
    if part.inline_data and part.inline_data.data and not img_saved:
        try:
            img = Image.open(BytesIO(part.inline_data.data))
            img.save("ai_explained.png")
            print("✅ FLASH image saved.")
            img_saved = True
        except Exception:
            print("⚠️ FLASH image invalid — falling back")

# 2️⃣ Fallback via HF FLUX API
if not img_saved and hf:
    try:
        print("🔄 Attempting Hugging Face FLUX via Inference API...")
        image = hf.text_to_image(
            "Friendly robot AI illustration: input → thinking → output",
            model="black-forest-labs/FLUX.1-dev"
        )
        image.save("ai_explained.png")
        print("✅ HF FLUX image saved via Hugging Face")  # using FLUX.1-dev :contentReference[oaicite:1]{index=1}
        img_saved = True
    except Exception as e:
        print("⚠️ HF fallback failed:", e)

# 3️⃣ Final fallback: local default
if not img_saved and hf:
    try:
        print("🔄 Attempting HF free FLUX.1‑schnell via Inference API...")
        image = hf.text_to_image(
            "Friendly robot AI illustration: input → thinking → output",
            model="black-forest-labs/FLUX.1-schnell",
            provider="hf-inference"
        )
        image.save("ai_explained.png")
        print("✅ Free FLUX.1-schnell image saved.")
        img_saved = True
    except Exception as e:
        print("⚠️ HF fallback failed:", e)


# 4️⃣ Generate TTS audio using Gemini
tts_resp = gemini.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=text,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
            )
        )
    )
)
pcm = tts_resp.candidates[0].content.parts[0].audio.pcm
save_audio("tts_audio.wav", pcm)
print("✅ TTS audio saved.")

# 🧾 Summary
print(f"\n🎨 Image: ai_explained.png\n🔊 Audio: tts_audio.wav\n📝 Text preview: {text.strip()[:100]}…")
