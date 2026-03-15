import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import io
import re
import urllib.parse
import base64

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Fridge 2 Feast",
    page_icon="🍳",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #fff8f1 0%, #fffdfb 45%, #fff7ed 100%);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff1dc 0%, #ffe5c1 100%);
        border-right: 1px solid rgba(234, 88, 12, 0.12);
    }
    section[data-testid="stSidebar"] * {
        color: #5e3414 !important;
    }
    .block-container {
        padding-top: 1.7rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }
    .hero-box {
        background: linear-gradient(135deg, #fff0db 0%, #ffe7c7 45%, #fff9f1 100%);
        border: 1px solid rgba(255, 153, 51, 0.18);
        padding: 2rem 2rem 1.4rem 2rem;
        border-radius: 28px;
        box-shadow: 0 14px 32px rgba(245, 158, 11, 0.10);
        margin-bottom: 1.4rem;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #3a2412;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #6d4c35;
        font-size: 1.05rem;
        margin-bottom: 0;
    }
    .section-card {
        background: linear-gradient(180deg, #ffffff 0%, #fffaf4 100%);
        border-radius: 24px;
        padding: 1.2rem;
        box-shadow: 0 10px 26px rgba(0,0,0,0.05);
        border: 1px solid rgba(255, 153, 51, 0.08);
        margin-bottom: 1rem;
    }
    .ingredient-card {
        background: linear-gradient(180deg, #ffffff 0%, #fff6ed 100%);
        border: 1px solid rgba(245, 158, 11, 0.10);
        border-radius: 22px;
        padding: 0.9rem;
        box-shadow: 0 8px 18px rgba(245, 158, 11, 0.06);
        text-align: center;
        height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-bottom: 1rem;
    }
    .ingredient-img-wrap {
        height: 140px;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border-radius: 16px;
        background: #fffdf9;
        border: 1px solid rgba(245, 158, 11, 0.08);
        margin-bottom: 0.7rem;
    }
    .ingredient-img-wrap img {
        max-height: 120px !important;
        max-width: 100% !important;
        width: auto !important;
        object-fit: contain !important;
        display: block;
    }
    .ingredient-qty {
        font-size: 1.02rem;
        font-weight: 700;
        color: #3b2a1f;
        margin-top: 0.45rem;
        margin-bottom: 0.15rem;
    }
    .ingredient-name {
        color: #7c6856;
        font-size: 0.95rem;
        margin-bottom: 0;
        min-height: 40px;
    }
    .metric-card {
        background: linear-gradient(135deg, #fff3e6 0%, #ffe8cc 100%);
        border: 1px solid rgba(234, 88, 12, 0.10);
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 8px 18px rgba(234, 88, 12, 0.06);
        margin-bottom: 2rem;
    }
    .metric-label {
        color: #9a5a16;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        color: #3a2412;
        font-size: 1.15rem;
        font-weight: 800;
    }
    .recipe-step {
        background: linear-gradient(180deg, #ffffff 0%, #fff8f1 100%);
        border-left: 5px solid #f59e0b;
        padding: 0.95rem 1rem;
        border-radius: 14px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.04);
        margin-bottom: 0.8rem;
        color: #2f241d;
    }
    .info-banner {
        background: linear-gradient(135deg, #fff4d8 0%, #ffedd5 100%);
        border: 1px solid rgba(245, 158, 11, 0.14);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        color: #7c4a03;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    div[data-baseweb="tab-list"] {
        gap: 8px;
    }
    button[data-baseweb="tab"] {
        border-radius: 999px !important;
        padding: 10px 18px !important;
        background: #fff2e2 !important;
        color: #7c4a03 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%) !important;
        color: white !important;
    }
    .stButton > button {
        border-radius: 14px;
        border: none;
        background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
        color: white;
        font-weight: 700;
        padding: 0.85rem 1rem;
        box-shadow: 0 8px 18px rgba(234, 88, 12, 0.22);
    }
    .stButton > button:hover {
        filter: brightness(1.03);
    }
    [data-testid="stImage"] img {
        border-radius: 18px;
    }
    .stRadio > div {
        background: linear-gradient(180deg, #fffaf4 0%, #fff5ea 100%);
        padding: 0.9rem 1rem;
        border-radius: 18px;
        border: 1px solid rgba(245, 158, 11, 0.10);
    }
</style>
""", unsafe_allow_html=True)

# =========================
# MODEL SETUP
# =========================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    try:
        model = genai.GenerativeModel("gemini-3-flash-preview")
        model.count_tokens("ping")
    except Exception:
        model = genai.GenerativeModel("gemini-2.5-flash")
except Exception:
    st.error("API Error. Check that GEMINI_API_KEY is in your .streamlit/secrets.toml file!")
    st.stop()

# =========================
# HELPERS
# =========================
@st.cache_data(ttl=3600)
def generate_flux_image(prompt):
    headers = {
        "Accept": "image/png",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {}
    }
    response = requests.post(
        "https://jjx1c75qu4j1zt5s.us-east-1.aws.endpoints.huggingface.cloud",
        headers=headers,
        json=payload,
        timeout=20
    )
    response.raise_for_status()
    return response.content

@st.cache_data(ttl=3600)
def get_spoonacular_recipe(ingredients_string, cuisine, health_level):
    api_key = st.secrets.get("SPOONACULAR_API_KEY")
    if not api_key:
        return None, "Missing SPOONACULAR_API_KEY in your .streamlit/secrets.toml file!"

    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "apiKey": api_key,
        "includeIngredients": ingredients_string,
        "sort": "max-used-ingredients",
        "fillIngredients": True,
        "addRecipeInformation": True,
        "addRecipeNutrition": True,
        "number": 5,
        "ignorePantry": False
    }

    if health_level == "Healthy":
        params["maxCalories"] = 600
    elif health_level == "Balanced":
        params["maxCalories"] = 800
    elif health_level == "Comfort":
        params["minCalories"] = 600

    if cuisine != "Any":
        params["cuisine"] = cuisine

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 402:
            return None, "Spoonacular API Daily Quota Exceeded (Error 402). Please switch to 'AI Chef' mode!"

        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                best_recipe = min(data["results"], key=lambda x: x.get("missedIngredientCount", 99))
                return best_recipe, None
            return None, f"No real recipes found for these ingredients and a '{health_level}' goal."
        return None, f"Spoonacular Error: {response.status_code}"
    except Exception as e:
        return None, f"API Request Failed: {e}"

def normalize_ingredient_query(name):
    clean = name.lower().strip()
    replacements = {
        "eggs": "egg",
        "bell peppers": "bell pepper",
        "peppers": "pepper",
        "breads": "bread",
        "garlic cloves": "garlic",
        "cloves garlic": "garlic"
    }
    remove_words = [
        "large", "small", "medium", "fresh", "raw", "cooked", "chopped",
        "diced", "sliced", "minced", "whole", "extra", "virgin", "tbsp",
        "tsp", "cup", "cups", "slice", "slices", "clove", "cloves"
    ]
    clean = re.sub(r"[^a-zA-Z0-9\s-]", "", clean)
    if clean in replacements:
        clean = replacements[clean]

    words = [w for w in clean.split() if w not in remove_words]
    clean = " ".join(words).strip()
    return "egg" if clean == "eggs" else (clean if clean else name.strip())

@st.cache_data(ttl=86400)
def get_spoonacular_search_image_url(name):
    api_key = st.secrets.get("SPOONACULAR_API_KEY")
    if not api_key:
        return None

    cleaned_name = normalize_ingredient_query(name)

    try:
        url = "https://api.spoonacular.com/food/ingredients/search"
        params = {
            "apiKey": api_key,
            "query": cleaned_name,
            "number": 1
        }
        r = requests.get(url, params=params, timeout=6)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            if results:
                image_name = results[0].get("image")
                if image_name:
                    return f"https://img.spoonacular.com/ingredients_250x250/{image_name}"
    except Exception:
        pass

    return None

@st.cache_data(ttl=86400)
def get_ingredient_image_url(name):
    cleaned_name = normalize_ingredient_query(name)
    formatted_name = cleaned_name.replace(" ", "-")
    spoonacular_static_url = f"https://img.spoonacular.com/ingredients_250x250/{formatted_name}.jpg"

    try:
        r = requests.get(spoonacular_static_url, timeout=5)
        if r.status_code == 200 and r.content:
            return spoonacular_static_url
    except Exception:
        pass

    search_url = get_spoonacular_search_image_url(name)
    if search_url:
        return search_url

    safe_name = urllib.parse.quote(cleaned_name)
    return f"https://image.pollinations.ai/prompt/{safe_name}%20food%20ingredient%20isolated%20on%20white%20background?width=250&height=250&nologo=true"

@st.cache_data(ttl=86400)
def fetch_image_base64(url):
    if not url:
        return None
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.content:
            return base64.b64encode(r.content).decode("utf-8")
    except Exception:
        pass
    return None

def build_svg_placeholder(name):
    label = (name[:18] if name else "Ingredient")
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="250" height="140">
        <rect width="100%" height="100%" fill="#fff7ed"/>
        <text x="50%" y="42%" dominant-baseline="middle" text-anchor="middle"
              font-size="34" fill="#f59e0b">🥕</text>
        <text x="50%" y="72%" dominant-baseline="middle" text-anchor="middle"
              font-size="15" fill="#7c4a03" font-family="Arial">{label}</text>
    </svg>
    """
    return base64.b64encode(svg.encode("utf-8")).decode("utf-8")

def generate_instruction_fallback(recipe_name, ingredients_list):
    prompt = f"""
    Write clear step-by-step cooking instructions for this recipe.

    Recipe name: {recipe_name}
    Ingredients: {ingredients_list}

    Requirements:
    - 5 to 8 steps
    - practical cooking instructions
    - short and clear
    - no intro text
    - format as numbered steps
    """
    try:
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return "1. Prepare all ingredients.\n2. Combine and cook them in a suitable pan or pot.\n3. Season to taste.\n4. Cook until done.\n5. Serve warm."

def render_ingredient_card(img_url, qty, name):
    img_b64 = fetch_image_base64(img_url) if img_url else None
    if not img_b64:
        img_b64 = build_svg_placeholder(name)

    st.markdown(f"""
    <div class="ingredient-card">
        <div class="ingredient-img-wrap">
            <img src="data:image/jpeg;base64,{img_b64}">
        </div>
        <div class="ingredient-qty">{qty}</div>
        <div class="ingredient-name">{name}</div>
    </div>
    """, unsafe_allow_html=True)

def render_meta_cards(prep_time, difficulty, cost, estimated=False):
    label_cost = "Estimated Cost / Serving" if estimated else "Cost / Serving"
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Prep Time</div>
            <div class="metric-value">{prep_time} min</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Difficulty</div>
            <div class="metric-value">{difficulty}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label_cost}</div>
            <div class="metric-value">${cost:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

def render_macro_cards(calories, protein, carbs, fat):
    m1, m2, m3, m4 = st.columns(4)
    macro_vals = [
        ("Calories", calories),
        ("Protein", protein),
        ("Carbs", carbs),
        ("Fat", fat)
    ]
    for col, (label, value) in zip([m1, m2, m3, m4], macro_vals):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero-box">
    <div class="hero-title">🍳 Fridge 2 Feast</div>
    <p class="hero-subtitle">
        Turn your fridge into a personalized recipe with ingredient visuals, nutrition insights, and a cleaner cooking experience.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## Preferences")
nationality = st.sidebar.selectbox(
    "Cuisine Style",
    ["Any", "American", "Italian", "Mexican", "Chinese", "Indian", "Mediterranean"]
)
health_level = st.sidebar.select_slider(
    "Health Goal",
    options=["Comfort", "Balanced", "Healthy"]
)

# =========================
# TOP INPUT SECTION
# =========================
left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    recipe_mode = st.radio(
        "Choose your cooking engine:",
        [
            "🧑‍🍳 AI Chef (Invent a recipe using ONLY what I have)",
            "🥘 Perfect Recipe Match (Spoonacular - Uses database)"
        ]
    )
    uploaded_file = st.file_uploader("Upload fridge photo...", type=["jpg", "jpeg", "png"])
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="section-card" style="height: 100%;">
        <div class="info-banner" style="font-size: 1.1rem;">✨ <b>Core Features</b></div>
        <ul style="color: #5e3414; font-size: 1rem; line-height: 1.8; margin-top: 10px;">
            <li><b>Instant Pantry Matching:</b> Snap a photo of your fridge to build meals.</li>
            <li><b>Precision Nutrition:</b> Get exact macro and micro breakdowns.</li>
            <li><b>Adaptive AI Chef:</b> Can't find a database match? The AI invents one.</li>
            <li><b>Photorealistic Previews:</b> Powered by the advanced FLUX-1 model.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =========================
# MAIN FLOW
# =========================
if uploaded_file is not None:
    img = Image.open(uploaded_file)

    st.markdown("### Fridge Scan")
    st.image(img, caption="Uploaded fridge image", use_container_width=True)

    if st.button("🚀 Analyze & Generate Full Report", use_container_width=True):
        with st.spinner("Scanning ingredients and building your recipe..."):
            vision_prompt = """
            Identify the food ingredients in this image.
            Return ONLY a single, comma-separated list of the main ingredients you see
            (e.g., eggs, milk, tomato, chicken).
            Do NOT include quantities. Do NOT include any other text.
            """

            try:
                vision_response = model.generate_content([vision_prompt, img])
                detected_ingredients = vision_response.text.strip()

                st.success(f"Detected ingredients: {detected_ingredients}")

                dish_name = ""
                spoonacular_image = ""
                final_dish_image = None

                if "Perfect Recipe Match" in recipe_mode:
                    recipe_data, error_msg = get_spoonacular_recipe(detected_ingredients, nationality, health_level)

                    if error_msg or not recipe_data:
                        st.error(f"Spoonacular Error: {error_msg}")
                        st.stop()

                    dish_name = recipe_data.get("title", "Delicious Meal")
                    spoonacular_image = recipe_data.get("image", "")

                    prep_time = recipe_data.get("readyInMinutes", "N/A")
                    price_per_serving_cents = recipe_data.get("pricePerServing")
                    cost_per_serving = round(price_per_serving_cents / 100, 2) if price_per_serving_cents is not None else 0.0

                    if prep_time != "N/A":
                        if prep_time <= 20:
                            difficulty = "Easy"
                        elif prep_time <= 40:
                            difficulty = "Medium"
                        else:
                            difficulty = "Hard"
                    else:
                        difficulty = "Medium"

                    try:
                        flux_prompt = f"Professional food photography of {dish_name}, highly detailed, natural cinematic lighting, photorealistic, appetizing, culinary magazine style, 8k resolution"
                        image_bytes = generate_flux_image(flux_prompt)
                        final_dish_image = Image.open(io.BytesIO(image_bytes))
                    except Exception:
                        pass

                    st.markdown(f"## {dish_name}")
                    render_meta_cards(prep_time, difficulty, cost_per_serving, estimated=False)

                    st.markdown("<br>", unsafe_allow_html=True)

                    tab1, tab2, tab3 = st.tabs(["🛒 Grocery Check", "👨‍🍳 Recipe", "🔬 Nutrition"])

                    with tab1:
                        st.markdown("### ✅ Ingredients You Have")
                        used_items = recipe_data.get("usedIngredients", [])
                        if used_items:
                            cols = st.columns(3)
                            for i, item in enumerate(used_items):
                                with cols[i % 3]:
                                    qty_text = f"{str(item.get('amount', '')).replace('*', '').strip()} {item.get('unitShort', '')}".strip()
                                    img_url = item.get("image", "")
                                    render_ingredient_card(img_url, qty_text, item.get("name", "Ingredient"))

                        st.markdown("### ❌ Missing Ingredients")
                        missed_items = recipe_data.get("missedIngredients", [])
                        if not missed_items:
                            st.success("You already have everything needed for this recipe.")
                        else:
                            miss_cols = st.columns(3)
                            for i, item in enumerate(missed_items):
                                with miss_cols[i % 3]:
                                    qty_text = f"{str(item.get('amount', '')).replace('*', '').strip()} {item.get('unitShort', '')}".strip()
                                    img_url = item.get("image", "")
                                    render_ingredient_card(img_url, qty_text, item.get("name", "Ingredient"))

                    with tab2:
                        st.markdown("### Step-by-Step Instructions")
                        instructions = recipe_data.get("analyzedInstructions", [])
                        raw_instructions = recipe_data.get("instructions", "")

                        if instructions and len(instructions) > 0 and instructions[0].get("steps"):
                            steps = instructions[0].get("steps", [])
                            for step in steps:
                                st.markdown(
                                    f'<div class="recipe-step"><b>Step {step["number"]}:</b> {step["step"]}</div>',
                                    unsafe_allow_html=True
                                )
                        elif raw_instructions:
                            clean_text = re.sub(r'<[^>]+>', '', raw_instructions)
                            split_steps = [s.strip() for s in re.split(r'\.\s+', clean_text) if s.strip()]
                            for idx, step in enumerate(split_steps, start=1):
                                st.markdown(
                                    f'<div class="recipe-step"><b>Step {idx}:</b> {step}</div>',
                                    unsafe_allow_html=True
                                )
                        else:
                            used_items = recipe_data.get("usedIngredients", [])
                            missed_items = recipe_data.get("missedIngredients", [])
                            ingredient_names = ", ".join([i.get("name", "") for i in used_items + missed_items])

                            fallback_steps = generate_instruction_fallback(dish_name, ingredient_names)
                            step_lines = [line.strip() for line in fallback_steps.split("\n") if line.strip()]

                            for idx, line in enumerate(step_lines, start=1):
                                line_clean = re.sub(r"^\d+[\).\s-]*", "", line)
                                st.markdown(
                                    f'<div class="recipe-step"><b>Step {idx}:</b> {line_clean}</div>',
                                    unsafe_allow_html=True
                                )

                        st.markdown("### Dish Preview")
                        if final_dish_image:
                            st.image(final_dish_image, caption=f"Photorealistic visualization of {dish_name}", use_container_width=True)
                        elif spoonacular_image:
                            st.image(spoonacular_image, caption=f"Recipe image for {dish_name}", use_container_width=True)

                    with tab3:
                        nutrients = recipe_data.get("nutrition", {}).get("nutrients", [])
                        if nutrients:
                            macros = {
                                n["name"]: f"{n['amount']}{n['unit']}"
                                for n in nutrients if n["name"] in ["Calories", "Protein", "Carbohydrates", "Fat"]
                            }

                            render_macro_cards(
                                macros.get("Calories", "N/A"),
                                macros.get("Protein", "N/A"),
                                macros.get("Carbohydrates", "N/A"),
                                macros.get("Fat", "N/A")
                            )

                            st.markdown("### Verified Micronutrient Daily Value")
                            target_micros = ["Vitamin A", "Vitamin C", "Calcium", "Iron", "Sodium", "Potassium", "Magnesium"]
                            for n in nutrients:
                                if n["name"] in target_micros:
                                    val_percent = int(n.get("percentOfDailyNeeds", 0))
                                    st.write(f"**{n['name']}** ({val_percent}%)")
                                    st.progress(min(val_percent / 100.0, 1.0))

                else:
                    st.info("AI Chef is inventing a custom recipe using strictly what you have.")

                    # PROMPT UPGRADE: Directly asking the AI to calculate the time, difficulty, and cost
                    fallback_prompt = f"""
                    The user ONLY has the following ingredients: {detected_ingredients}.
                    Create a creative {nationality} recipe for a {health_level} goal using STRICTLY these limited resources (you may assume they have basic water, salt, and cooking oil/butter).

                    YOU MUST SEPARATE DATA WITH THESE EXACT HEADERS (No bolding, no markdown on the brackets):
                    [NAME]
                    [SERVINGS] (A single integer)
                    [PREP_TIME] (A single integer representing total minutes, e.g., 25)
                    [DIFFICULTY] (Strictly one word: Easy, Medium, or Hard)
                    [COST_PER_SERVING] (A single decimal number representing USD, e.g., 3.50)
                    [INGREDIENTS] (Format each on a new line strictly as: Quantity AND Unit | Name)
                    [RECIPE_STEPS] (Numbered list)
                    [MACROS] (Format strictly as:
                    Calories: X kcal
                    Protein: Xg
                    Carbs: Xg
                    Fats: Xg)
                    [MICROS] (Calculate based strictly on the exact quantities used. Provide exactly the 7 highest micronutrients, and you MUST always include Sodium. Format strictly as 'Name: X%')
                    """

                    fallback_response = model.generate_content(fallback_prompt)
                    text = fallback_response.text

                    sections = [s.strip() for s in re.split(r'\[(.*?)\]', text)]

                    dish_name = sections[sections.index("NAME") + 1]
                    servings_text = sections[sections.index("SERVINGS") + 1]
                    prep_time_text = sections[sections.index("PREP_TIME") + 1]
                    difficulty_text = sections[sections.index("DIFFICULTY") + 1].strip()
                    cost_text = sections[sections.index("COST_PER_SERVING") + 1]
                    ingredients_raw = sections[sections.index("INGREDIENTS") + 1]
                    recipe_text = sections[sections.index("RECIPE_STEPS") + 1]
                    macro_text = sections[sections.index("MACROS") + 1]
                    micro_text = sections[sections.index("MICROS") + 1]

                    # Safely parsing the AI's responses for the UI
                    try:
                        servings_match = re.search(r"\d+", servings_text)
                        servings = max(1, int(servings_match.group())) if servings_match else 2
                    except:
                        servings = 2
                        
                    try:
                        prep_time_match = re.search(r"\d+", prep_time_text)
                        prep_time = int(prep_time_match.group()) if prep_time_match else 30
                    except:
                        prep_time = 30
                        
                    try:
                        cost_match = re.search(r"\d+\.\d+", cost_text)
                        cost_per_serving = float(cost_match.group()) if cost_match else 2.50
                    except:
                        cost_per_serving = 2.50
                        
                    difficulty = difficulty_text if difficulty_text in ["Easy", "Medium", "Hard"] else "Medium"

                    try:
                        flux_prompt = f"Professional food photography of {dish_name}, highly detailed, natural cinematic lighting, photorealistic, appetizing, culinary magazine style, 8k resolution"
                        image_bytes = generate_flux_image(flux_prompt)
                        final_dish_image = Image.open(io.BytesIO(image_bytes))
                    except Exception:
                        pass

                    st.markdown(f"## {dish_name}")
                    render_meta_cards(prep_time, difficulty, cost_per_serving, estimated=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    tab1, tab2, tab3 = st.tabs(["🛒 Ingredients Needed", "👨‍🍳 Recipe", "🔬 Nutrition"])

                    with tab1:
                        st.markdown("### Exact Quantities Needed")
                        st.caption(f"Estimated servings: {servings}")
                        ing_list = [i.strip() for i in ingredients_raw.split('\n') if "|" in i]
                        cols = st.columns(3)

                        for i, item in enumerate(ing_list):
                            if "|" in item:
                                qty, name = item.split("|", 1)
                                clean_qty = str(qty).replace('*', '').strip()
                                clean_name = name.strip()
                                img_url = get_ingredient_image_url(clean_name)

                                with cols[i % 3]:
                                    render_ingredient_card(img_url, clean_qty, clean_name)

                    with tab2:
                        st.markdown("### Step-by-Step Instructions")
                        recipe_lines = [line.strip() for line in recipe_text.split("\n") if line.strip()]
                        for idx, line in enumerate(recipe_lines, start=1):
                            line_clean = re.sub(r"^\d+[\).\s-]*", "", line)
                            st.markdown(
                                f'<div class="recipe-step"><b>Step {idx}:</b> {line_clean}</div>',
                                unsafe_allow_html=True
                            )

                        st.markdown("### Dish Preview")
                        if final_dish_image:
                            st.image(final_dish_image, caption=f"Photorealistic visualization of {dish_name}", use_container_width=True)
                        else:
                            safe_dish = re.sub(r'[^a-zA-Z0-9\s]', '', dish_name)
                            encoded_name = urllib.parse.quote(safe_dish + " food photography")
                            st.image(
                                f"https://image.pollinations.ai/prompt/{encoded_name}?width=800&height=500&nologo=true",
                                caption=f"AI visualization of {dish_name}",
                                use_container_width=True
                            )

                    with tab3:
                        st.warning("Nutrition in AI Chef mode is mathematically estimated from the generated ingredient quantities.")
                        st.markdown("### Calculated Macronutrients")

                        calories = "N/A"
                        protein = "N/A"
                        carbs = "N/A"
                        fat = "N/A"

                        for line in macro_text.split("\n"):
                            line = line.strip()
                            if line.lower().startswith("calories:"):
                                calories = line.split(":", 1)[1].strip()
                            elif line.lower().startswith("protein:"):
                                protein = line.split(":", 1)[1].strip()
                            elif line.lower().startswith("carbs:"):
                                carbs = line.split(":", 1)[1].strip()
                            elif line.lower().startswith("fats:"):
                                fat = line.split(":", 1)[1].strip()
                            elif line.lower().startswith("fat:"):
                                fat = line.split(":", 1)[1].strip()

                        render_macro_cards(calories, protein, carbs, fat)

                        st.markdown("### Calculated Micronutrient Daily Value")
                        micros = re.findall(r'([a-zA-Z0-9\s]+):\s*(\d+)%', micro_text)
                        for m_name, m_val in micros:
                            m_name_clean = m_name.strip()
                            val = int(m_val)
                            st.write(f"**{m_name_clean}** ({val}%)")
                            st.progress(min(val / 100.0, 1.0))

            except Exception as e:
                st.error(f"Error building report: {e}")
