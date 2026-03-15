# 🍽️ Fridge 2 Feast

**From fridge to feast — turn the ingredients you already have into AI-generated recipes and visualize the final dish instantly.**

Fridge 2 Feast is an AI-powered web app that generates recipes from ingredients you already have and visualizes the final dish using AI-generated images. The goal is to help users quickly decide what to cook while reducing food waste.

---

# 💡 Problem

Many people struggle to decide what to cook with the ingredients already in their fridge. This often leads to wasted food, unnecessary grocery purchases, and time spent searching for recipes online.

---

# 🚀 Features

- Generate recipes from ingredients you already have
- Step-by-step cooking instructions
- AI-generated image of the finished dish
- Simple and interactive web interface
- Fast AI responses using the Gemini API

---

# 🧠 How It Works

1. The user enters ingredients they currently have available.
2. The app queries the **Spoonacular API** to retrieve recipes related to those ingredients.
3. The selected recipe and ingredients are sent to the **Gemini AI model**.
4. Gemini generates:
   - A refined recipe
   - Step-by-step cooking instructions
5. The system then generates an AI image showing what the final dish could look like.

This allows users to quickly discover meals they can cook without manually searching through recipes.

---

# 🛠 Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### APIs
- **Google Gemini API** – generates recipes and AI images
- **Spoonacular API** – retrieves ingredient-based recipe data

### Libraries
- streamlit  
- google-generativeai  
- pillow  

---

# ⚙️ Installation & Setup

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/your-repository-name.git
cd your-repository-name
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Add your API key

Create a file called:

```
.streamlit/secrets.toml
```

Inside the file add:

```
GEMINI_API_KEY="your_api_key_here"
SPOONACULAR_API_KEY = "8c0df04318ca46b2884b4c26db6efa83"
```

## 4. Run the application

```bash
streamlit run app.py
```

---

# 🎥 Demo Video

4-minute demo video explaining the project:

[https://youtube.com/your-demo-video-link](https://youtu.be/c8Eyi7PfzDc)

---

# 📂 Project Structure

```
project-folder
│
├── README.md
├── app.py
└── requirements.txt
```

---

# 🔮 Future Improvements

- Add nutritional analysis for recipes
- Support dietary preferences (vegan, halal, gluten-free)
- Allow users to save favorite recipes
- Improve UI and mobile responsiveness

---

# 👨‍💻 Team

- Wasi Ullah  
- Devarya Roy  
- Armin Farhad  
- Anusihvan Pratheepan
