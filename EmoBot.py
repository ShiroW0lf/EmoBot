import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np

# Expanded dataset for emotion detection
data = {
    "texts": [
        "I am so happy today!", "This is the best day ever!", "I feel great!",
        "I am so sad right now.", "This is the worst day.", "I feel terrible.",
        "I am so angry about this!", "This makes me furious!", "I can't believe this happened.",
        "The weather is nice today.", "I have no strong feelings about this.", "This is just okay.",
        "Wow, I didn't expect that!", "This is such a surprise!", "I am shocked!",
        "I am scared of the dark.", "This is terrifying!", "I feel frightened.",
        "I am so excited for the trip!", "This is going to be amazing!", "I can't wait!"
    ],
    "emotions": [
        "happy", "happy", "happy",
        "sad", "sad", "sad",
        "angry", "angry", "angry",
        "neutral", "neutral", "neutral",
        "surprised", "surprised", "surprised",
        "scared", "scared", "scared",
        "excited", "excited", "excited"
    ]
}

# Emojis for each emotion
emotion_emojis = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😡",
    "neutral": "😐",
    "surprised": "😮",
    "scared": "😨",
    "excited": "🎉"
}

# Train a simple Naive Bayes model with TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data["texts"])
model = MultinomialNB()
model.fit(X, data["emotions"])

# Global variables for survey responses
pre_survey_responses = {}
post_survey_responses = {}

# Gamification variables
points = 0
badges = []
progress = 0
challenges = {
    "detect_5_in_a_row": {"goal": 5, "progress": 0, "completed": False},
    "train_10_examples": {"goal": 10, "progress": 0, "completed": False}
}

# Storyline variables
storyline = [
    "Welcome to the world of AI! 🌍",
    "You are training an AI assistant named 'EmoBot' to understand human emotions.",
    "Help EmoBot learn by detecting emotions and adding training data.",
    "Complete challenges to unlock rewards and become an AI expert!"
]

# Function to detect emotion
def detect_emotion(input_text):
    global points, progress
    text = input_text.get("1.0", "end-1c")  # Get user input
    if not text.strip():
        messagebox.showwarning("Oops!", "Please enter some text!")
        return
    
    # Predict emotion
    text_vec = vectorizer.transform([text])
    emotion = model.predict(text_vec)[0]
    probabilities = model.predict_proba(text_vec)[0]
    
    # Show result with emoji
    result_label.config(text=f"AI detects: {emotion.capitalize()} {emotion_emojis.get(emotion, '')}", fg="green")
    
    # Explain AI process
    explain_ai_process(text, emotion, probabilities, text_vec)
    
    # Visualize word importance
    visualize_word_importance(text, text_vec)

    # Award points
    points += 10
    update_points()

    # Update challenges
    update_challenges("detect_5_in_a_row")

    # Check for badges
    if points >= 50 and "AI Novice" not in badges:
        badges.append("AI Novice")
        messagebox.showinfo("Badge Unlocked!", "You unlocked the 'AI Novice' badge! 🎉")
    if points >= 100 and "AI Expert" not in badges:
        badges.append("AI Expert")
        messagebox.showinfo("Badge Unlocked!", "You unlocked the 'AI Expert' badge! 🎉")

    # Update progress
    progress += 10
    update_progress()

    # Update storyline
    update_storyline(f"EmoBot detected: {emotion.capitalize()} {emotion_emojis.get(emotion, '')}")

# Function to explain how the AI works
def explain_ai_process(text, emotion, probabilities, text_vec):
    explanation = (
        "How the AI works:\n"
        "1. The AI looks at the words in your text.\n"
        "2. It compares them to words it has seen before.\n"
        "3. Based on patterns, it predicts the emotion.\n"
        f"\nFor example, words like '{', '.join(vectorizer.inverse_transform(text_vec)[0][:3])}' helped it decide this is '{emotion}'.\n"
        f"\nProbabilities:\n"
    )
    for i, emotion_class in enumerate(model.classes_):
        explanation += f"{emotion_class.capitalize()}: {probabilities[i]*100:.2f}%\n"
    explanation_label.config(text=explanation)

# Function to visualize word importance
def visualize_word_importance(text, text_vec):
    word_importance = np.array(text_vec.sum(axis=0)).flatten()
    important_words = [
        (word, word_importance[idx])
        for word, idx in vectorizer.vocabulary_.items()
        if word_importance[idx] > 0
    ]
    important_words.sort(key=lambda x: x[1], reverse=True)
    
    word_importance_text = "Top contributing words:\n"
    for word, importance in important_words[:5]:
        word_importance_text += f"{word}: {importance:.2f}\n"
    word_importance_label.config(text=word_importance_text)

# Function to add training data
def add_training_data(training_text, emotion_var):
    global points, progress
    text = training_text.get("1.0", "end-1c")
    emotion = emotion_var.get()
    if text.strip() and emotion:
        data["texts"].append(text)
        data["emotions"].append(emotion.lower())
        retrain_model()
        messagebox.showinfo("Success!", "New training data added and model retrained!")
        training_text.delete("1.0", "end")

        # Award points
        points += 20
        update_points()

        # Update challenges
        update_challenges("train_10_examples")

        # Update progress
        progress += 20
        update_progress()

        # Update storyline
        update_storyline(f"EmoBot learned: {emotion.capitalize()} {emotion_emojis.get(emotion, '')}")
    else:
        messagebox.showwarning("Oops!", "Please enter both text and select an emotion!")

# Function to retrain the model
def retrain_model():
    global X, model
    X = vectorizer.fit_transform(data["texts"])
    model.fit(X, data["emotions"])

# Function to update points display
def update_points():
    points_label.config(text=f"Points: {points}")

# Function to update progress bar
def update_progress():
    progress_bar["value"] = progress
    if progress >= 100:
        messagebox.showinfo("Congratulations!", "You've completed the training! 🎉")

# Function to update challenges
def update_challenges(challenge_key):
    if not challenges[challenge_key]["completed"]:
        challenges[challenge_key]["progress"] += 1
        if challenges[challenge_key]["progress"] >= challenges[challenge_key]["goal"]:
            challenges[challenge_key]["completed"] = True
            messagebox.showinfo("Challenge Complete!", f"You completed the '{challenge_key.replace('_', ' ')}' challenge! 🎉")
            points += 50  # Bonus points for completing a challenge
            update_points()

# Function to update storyline
def update_storyline(message):
    storyline.append(message)
    storyline_text.config(state="normal")
    storyline_text.insert("end", f"\n{message}")
    storyline_text.config(state="disabled")
    storyline_text.see("end")

# Function to switch between pages
def show_page(page):
    for frame in pages.values():
        frame.pack_forget()
    pages[page].pack(fill="both", expand=True)

# Welcome Page
def create_welcome_page():
    frame = tk.Frame(main_frame, bg="#E6F3FF")
    label = tk.Label(frame, text="Welcome to the AI Emotion Detector! 🧠", font=("Arial", 24), bg="#E6F3FF")
    label.pack(pady=40)
    next_button = tk.Button(frame, text="Next", font=("Arial", 14), bg="#4CAF50", fg="white", command=lambda: show_page("pre_survey"))
    next_button.pack(pady=20)
    return frame

# Pre-Survey Page
def create_pre_survey_page():
    frame = tk.Frame(main_frame, bg="#E6F3FF")
    label = tk.Label(frame, text="Pre-Survey: What do you know about AI?", font=("Arial", 20), bg="#E6F3FF")
    label.pack(pady=20)

    questions = [
        "1. Have you heard about AI before?",
        "2. Do you know how AI learns from data?",
        "3. Can you name an example of AI in real life?",
        "4. Do you know what sentiment analysis is?",
        "5. Have you ever trained an AI model?"
    ]
    options = ["Yes", "No", "Maybe"]

    for i, question in enumerate(questions):
        q_frame = tk.Frame(frame, bg="#E6F3FF")
        q_frame.pack(pady=10, fill="x", padx=20)
        q_label = tk.Label(q_frame, text=question, font=("Arial", 12), bg="#E6F3FF")
        q_label.pack(side="left")
        var = tk.StringVar(value="")  # No pre-selected option
        for j, option in enumerate(options):
            rb = tk.Radiobutton(q_frame, text=option, variable=var, value=option, font=("Arial", 12), bg="#E6F3FF")
            rb.pack(side="left", padx=10)
        pre_survey_responses[i] = var

    next_button = tk.Button(frame, text="Next", font=("Arial", 14), bg="#4CAF50", fg="white", command=lambda: show_page("instructions"))
    next_button.pack(pady=20)
    return frame

# Instructions Page
def create_instructions_page():
    frame = tk.Frame(main_frame, bg="#E6F3FF")
    label = tk.Label(frame, text="How to Use the App", font=("Arial", 20), bg="#E6F3FF")
    label.pack(pady=20)

    instructions = [
        "1. Enter a sentence or phrase in the text box.",
        "2. Click 'Detect Emotion' to see what the AI predicts.",
        "3. Add your own examples to help the AI learn!",
        "4. Earn points and badges as you progress!",
        "5. Have fun and learn how AI works!"
    ]

    for instruction in instructions:
        i_label = tk.Label(frame, text=instruction, font=("Arial", 12), bg="#E6F3FF")
        i_label.pack(pady=5, anchor="w")

    start_button = tk.Button(frame, text="Start", font=("Arial", 14), bg="#4CAF50", fg="white", command=lambda: show_page("main_app"))
    start_button.pack(pady=20)
    return frame

# Main App Page
def create_main_app_page():
    frame = tk.Frame(main_frame, bg="#E6F3FF")

    # Add a canvas and scrollbar for the main app page
    canvas = tk.Canvas(frame, bg="#E6F3FF")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Create a frame inside the canvas
    content_frame = tk.Frame(canvas, bg="#E6F3FF")
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    # Points and Progress Bar
    global points_label, progress_bar
    points_label = tk.Label(content_frame, text=f"Points: {points}", font=("Arial", 14), bg="#E6F3FF")
    points_label.pack(pady=10)

    progress_bar = ttk.Progressbar(content_frame, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)
    progress_bar["value"] = progress

    # Storyline Section
    storyline_frame = tk.LabelFrame(content_frame, text="Storyline", font=("Arial", 14), bg="#E6F3FF")
    storyline_frame.pack(pady=10, fill="x")

    global storyline_text
    storyline_text = tk.Text(storyline_frame, height=5, width=60, font=("Arial", 12), wrap="word", state="disabled")
    storyline_text.pack(pady=10, padx=10)
    for line in storyline:
        storyline_text.config(state="normal")
        storyline_text.insert("end", f"{line}\n")
        storyline_text.config(state="disabled")

    # Challenges Section
    challenges_frame = tk.LabelFrame(content_frame, text="Challenges", font=("Arial", 14), bg="#E6F3FF")
    challenges_frame.pack(pady=10, fill="x")

    challenges_label = tk.Label(challenges_frame, text="Complete these challenges to earn rewards!", font=("Arial", 12), bg="#E6F3FF")
    challenges_label.pack(pady=5)

    for challenge, details in challenges.items():
        challenge_text = f"{challenge.replace('_', ' ').capitalize()}: {details['progress']}/{details['goal']}"
        challenge_label = tk.Label(challenges_frame, text=challenge_text, font=("Arial", 12), bg="#E6F3FF")
        challenge_label.pack(pady=5)

    # Input Section
    input_frame = tk.LabelFrame(content_frame, text="Enter Text", font=("Arial", 14), bg="#E6F3FF")
    input_frame.pack(pady=10, fill="x")

    input_text = tk.Text(input_frame, height=5, width=60, font=("Arial", 12))
    input_text.pack(pady=10, padx=10)
    input_text.insert("1.0", "Example: I am so happy today!")  # Example text

    detect_button = tk.Button(input_frame, text="Detect Emotion", font=("Arial", 12), bg="#4CAF50", fg="white", command=lambda: detect_emotion(input_text))
    detect_button.pack(pady=10)

    # Result Section
    global result_label
    result_label = tk.Label(content_frame, text="", font=("Arial", 16), bg="#E6F3FF")
    result_label.pack(pady=10)

    # Explanation Section
    global explanation_label
    explanation_frame = tk.LabelFrame(content_frame, text="How the AI Works", font=("Arial", 14), bg="#E6F3FF")
    explanation_frame.pack(pady=10, fill="x")

    explanation_label = tk.Label(explanation_frame, text="", font=("Arial", 12), bg="#E6F3FF", wraplength=600, justify="left")
    explanation_label.pack(pady=10, padx=10)

    # Word Importance Section
    global word_importance_label
    word_importance_frame = tk.LabelFrame(content_frame, text="Top Contributing Words", font=("Arial", 14), bg="#E6F3FF")
    word_importance_frame.pack(pady=10, fill="x")

    word_importance_label = tk.Label(word_importance_frame, text="", font=("Arial", 12), bg="#E6F3FF", wraplength=600, justify="left")
    word_importance_label.pack(pady=10, padx=10)

    # Training Section
    training_frame = tk.LabelFrame(content_frame, text="Add Training Data", font=("Arial", 14), bg="#E6F3FF")
    training_frame.pack(pady=10, fill="x")

    text_label = tk.Label(training_frame, text="Enter Text Data:", font=("Arial", 12), bg="#E6F3FF")
    text_label.pack(pady=5, padx=10, anchor="w")

    training_text = tk.Text(training_frame, height=3, width=60, font=("Arial", 12))
    training_text.pack(pady=5, padx=10)
    training_text.insert("1.0", "Example: I feel excited about the trip!")  # Example text

    emotion_label = tk.Label(training_frame, text="Select Emotion:", font=("Arial", 12), bg="#E6F3FF")
    emotion_label.pack(pady=5, padx=10, anchor="w")

    emotion_var = tk.StringVar()
    emotion_dropdown = ttk.Combobox(training_frame, textvariable=emotion_var, values=["happy", "sad", "angry", "neutral", "surprised", "scared", "excited"], font=("Arial", 12))
    emotion_dropdown.pack(pady=5, padx=10)

    add_data_button = tk.Button(training_frame, text="Add Data and Retrain", font=("Arial", 12), bg="#3498DB", fg="white", command=lambda: add_training_data(training_text, emotion_var))
    add_data_button.pack(pady=10)

    next_button = tk.Button(content_frame, text="Next", font=("Arial", 14), bg="#4CAF50", fg="white", command=lambda: show_page("post_survey"))
    next_button.pack(pady=20)
    return frame

# Post-Survey Page
def create_post_survey_page():
    frame = tk.Frame(main_frame, bg="#E6F3FF")
    label = tk.Label(frame, text="Post-Survey: What did you learn?", font=("Arial", 20), bg="#E6F3FF")
    label.pack(pady=20)

    questions = [
        "1. Did you learn how AI detects emotions?",
        "2. Can you explain how the AI works?",
        "3. Would you like to learn more about AI?",
        "4. Did you enjoy training the AI?",
        "5. Do you think AI can understand human emotions?"
    ]
    options = ["Yes", "No", "Maybe"]

    for i, question in enumerate(questions):
        q_frame = tk.Frame(frame, bg="#E6F3FF")
        q_frame.pack(pady=10, fill="x", padx=20)
        q_label = tk.Label(q_frame, text=question, font=("Arial", 12), bg="#E6F3FF")
        q_label.pack(side="left")
        var = tk.StringVar(value="")  # No pre-selected option
        for j, option in enumerate(options):
            rb = tk.Radiobutton(q_frame, text=option, variable=var, value=option, font=("Arial", 12), bg="#E6F3FF")
            rb.pack(side="left", padx=10)
        post_survey_responses[i] = var

    submit_button = tk.Button(frame, text="Submit", font=("Arial", 14), bg="#4CAF50", fg="white", command=show_feedback)
    submit_button.pack(pady=20)
    return frame

# Function to show feedback
def show_feedback():
    feedback = "Thank you for completing the survey!\n\n"
    feedback += "Here's what you shared:\n"
    for i, var in post_survey_responses.items():
        feedback += f"Q{i+1}: {var.get()}\n"
    messagebox.showinfo("Feedback", feedback)

# Initialize the main window
root = tk.Tk()
root.title("Make Your Own AI Emotion Detector 🧠")
root.geometry("700x600")  # Adjusted window size
root.configure(bg="#E6F3FF")

# Main Frame
main_frame = tk.Frame(root, bg="#E6F3FF")
main_frame.pack(fill="both", expand=True)

# Create pages
pages = {
    "welcome": create_welcome_page(),
    "pre_survey": create_pre_survey_page(),
    "instructions": create_instructions_page(),
    "main_app": create_main_app_page(),
    "post_survey": create_post_survey_page()
}

# Show the first page
show_page("welcome")

# Run the app
root.mainloop()