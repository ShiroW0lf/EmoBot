import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import random
import sqlite3
import os
import datetime
import csv
import math

# Define colors for a vibrant kids' app
COLORS = {
    "background": "#E6F3FF",  # Light blue
    "primary": "#FF6B6B",     # Coral red
    "secondary": "#4CAF50",   # Green
    "accent": "#FFD166",      # Yellow
    "text": "#333333",        # Dark gray
    "light_text": "#FFFFFF",  # White
    "highlight": "#FF9500"    # Orange
}

# Define fonts for consistent styling
FONTS = {
    "title": ("Comic Sans MS", 24, "bold"),
    "subtitle": ("Comic Sans MS", 18),
    "normal": ("Comic Sans MS", 14),
    "small": ("Comic Sans MS", 12)
}

# Utility function to create scrollable frames
def create_scrollable_frame(parent_frame):
    """
    Creates a scrollable frame inside the parent frame
    Returns the canvas and the interior frame where widgets should be placed
    """
    # Create a canvas object and a vertical scrollbar for scrolling
    canvas = tk.Canvas(parent_frame, bg=COLORS["background"], highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
    
    # Pack the scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Create an interior frame to hold the widgets
    interior_frame = tk.Frame(canvas, bg=COLORS["background"])
    interior_id = canvas.create_window(0, 0, window=interior_frame, anchor="nw", tags="interior")
    
    # Configure the canvas to resize the interior frame when configured
    def _configure_interior(event):
        # Update the scrollregion to encompass the interior frame
        size = (interior_frame.winfo_reqwidth(), interior_frame.winfo_reqheight())
        canvas.config(scrollregion="0 0 %s %s" % size)
        # Resize the canvas's width to fit the interior frame
        if interior_frame.winfo_reqwidth() != canvas.winfo_width():
            canvas.config(width=interior_frame.winfo_reqwidth())
    
    interior_frame.bind('<Configure>', _configure_interior)
    
    def _configure_canvas(event):
        if interior_frame.winfo_reqwidth() != canvas.winfo_width():
            # Update the interior frame's width to fill the canvas
            canvas.itemconfigure(interior_id, width=canvas.winfo_width())
    
    canvas.bind('<Configure>', _configure_canvas)
    
    # Bind mouse wheel events for scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)  # For Windows
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # For Linux
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # For Linux
    
    return canvas, interior_frame

class BouncingButton(tk.Button):
    """A button that bounces when hovered over"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Store original colors
        self.original_bg = self.cget("background")
        self.original_fg = self.cget("foreground")
        
        # Hover colors
        self.hover_bg = COLORS["highlight"]
        self.hover_fg = COLORS["light_text"]
        
        # Add round corners and shadow effect with styling
        self.config(relief="raised", borderwidth=0, padx=15, pady=8)
        
    def _on_enter(self, event):
        # Change colors
        self.config(background=self.hover_bg, foreground=self.hover_fg)
        
        # Make button slightly larger for bounce effect
        current_font = self.cget("font")
        if isinstance(current_font, str):
            # Handle default font string
            self.config(font=(current_font, 12, "bold"))
        else:
            # Handle tuple font
            larger_font = (current_font[0], current_font[1] + 2, current_font[2])
            self.config(font=larger_font)
        
    def _on_leave(self, event):
        # Restore original appearance
        self.config(background=self.original_bg, foreground=self.original_fg)
        
        # Restore original font size
        current_font = self.cget("font")
        if isinstance(current_font, str):
            # Handle default font string
            self.config(font=(current_font, 10, "bold"))
        else:
            # Handle tuple font
            original_font = (current_font[0], current_font[1] - 2, current_font[2])
            self.config(font=original_font)

class RainbowText(tk.Frame):
    """Create text with rainbow colored letters"""
    def __init__(self, master, text, font=FONTS["title"], **kwargs):
        super().__init__(master, bg=COLORS["background"], **kwargs)
        
        rainbow_colors = ["#FF9AA2", "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA"]
        
        for i, char in enumerate(text):
            color = rainbow_colors[i % len(rainbow_colors)]
            label = tk.Label(self, text=char, font=font, bg=COLORS["background"], fg=color)
            label.pack(side="left", padx=0)

class AuthenticationSystem:
    def __init__(self, root, on_successful_login=None):
        self.root = root
        self.on_successful_login = on_successful_login
        self.current_user = None
        
        # Set up database
        self.setup_database()
        
        # Create login frame with colorful background
        self.login_frame = tk.Frame(root, bg=COLORS["background"])
        
        # Create scrollable frame for login content
        canvas, content_frame = create_scrollable_frame(self.login_frame)
        self.login_content = content_frame
        
        # Add title with rainbow text
        title_frame = tk.Frame(self.login_content, bg=COLORS["background"])
        title_frame.pack(pady=20)
        
        rainbow_title = RainbowText(title_frame, "Welcome to AI Emotion Detector!")
        rainbow_title.pack()
        
        # Add robot character
        robot_frame = tk.Frame(self.login_content, bg=COLORS["background"])
        robot_frame.pack(pady=10)
        
        robot_label = tk.Label(robot_frame, text="🤖", font=("Arial", 72), bg=COLORS["background"])
        robot_label.pack()
        
        # Add login subtitle
        subtitle = tk.Label(self.login_content, text="Please sign in to start your adventure!", 
                          font=FONTS["subtitle"], bg=COLORS["background"], fg=COLORS["text"])
        subtitle.pack(pady=10)
        
        # Create form frame with pretty styling
        form_frame = tk.Frame(self.login_content, bg="white", bd=2, relief="solid")
        form_frame.pack(pady=20, padx=30)
        
        # Draw colorful border around form
        rainbow_colors = ["#FF9AA2", "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA"]
        for i in range(4):
            border = tk.Frame(form_frame, bg=rainbow_colors[i % len(rainbow_colors)], height=4)
            border.pack(fill="x")
        
        # First Name with emoji
        first_name_frame = tk.Frame(form_frame, bg="white")
        first_name_frame.pack(fill="x", pady=10, padx=20)
        
        first_name_emoji = tk.Label(first_name_frame, text="👤", font=("Arial", 16), bg="white")
        first_name_emoji.pack(side="left", padx=5)
        
        first_name_label = tk.Label(first_name_frame, text="First Name:", 
                                  font=FONTS["normal"], bg="white")
        first_name_label.pack(side="left", pady=5)
        
        self.first_name_entry = tk.Entry(first_name_frame, font=FONTS["normal"], width=20)
        self.first_name_entry.pack(side="left", padx=10)
        
        # Last Name
        last_name_frame = tk.Frame(form_frame, bg="white")
        last_name_frame.pack(fill="x", pady=10, padx=20)
        
        last_name_emoji = tk.Label(last_name_frame, text="👥", font=("Arial", 16), bg="white")
        last_name_emoji.pack(side="left", padx=5)
        
        last_name_label = tk.Label(last_name_frame, text="Last Name:", 
                                 font=FONTS["normal"], bg="white")
        last_name_label.pack(side="left", pady=5)
        
        self.last_name_entry = tk.Entry(last_name_frame, font=FONTS["normal"], width=20)
        self.last_name_entry.pack(side="left", padx=10)
        
        # Grade with fun icons
        grade_frame = tk.Frame(form_frame, bg="white")
        grade_frame.pack(fill="x", pady=10, padx=20)
        
        grade_emoji = tk.Label(grade_frame, text="🎓", font=("Arial", 16), bg="white")
        grade_emoji.pack(side="left", padx=5)
        
        grade_label = tk.Label(grade_frame, text="My Grade:", 
                             font=FONTS["normal"], bg="white")
        grade_label.pack(side="left", pady=5)
        
        grades = ["K 🌱", "1 🐣", "2 🐶", "3 🦊", "4 🦁", "5 🦄", "6 🚀", "7 ⚡", 
                 "8 🌟", "9 🔥", "10 💫", "11 🌈", "12 🌠", "College 🎓", "Teacher 🍎", "Other 🌍"]
        self.grade_var = tk.StringVar()
        
        # Create combobox with colorful options
        self.grade_combo = ttk.Combobox(grade_frame, textvariable=self.grade_var, 
                                      values=grades, font=FONTS["normal"], width=15)
        self.grade_combo.pack(side="left", padx=10)
        
        # Login button with bounce effect
        login_button = BouncingButton(self.login_content, text="Start Adventure! 🚀", 
                                    font=FONTS["subtitle"], 
                                    bg=COLORS["secondary"], fg="white",
                                    command=self.login)
        login_button.pack(pady=20)
        
        # User stats
        stats_frame = tk.Frame(self.login_content, bg=COLORS["background"])
        stats_frame.pack(pady=10, fill="x")
        
        # Get current user count
        user_count = self.get_user_count()
        
        stats_label = tk.Label(stats_frame, 
                             text=f"{user_count} explorers have joined this adventure!", 
                             font=FONTS["small"], bg=COLORS["background"], fg=COLORS["text"])
        stats_label.pack()
    
    def setup_database(self):
        """Create database and tables if they don't exist"""
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # Connect to database
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            grade TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create sessions table to track logins
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_count(self):
        """Get the count of unique users"""
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def login(self):
        """Handle user login"""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        
        # Get grade without emoji
        grade = self.grade_var.get().split()[0] if self.grade_var.get() else ""
        
        # Basic validation
        if not first_name or not last_name or not grade:
            messagebox.showinfo("Oops!", "Please fill in all fields to start your adventure! 🚀", 
                              icon=messagebox.INFO)
            return
        
        # Store in database
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute(
            "SELECT id FROM users WHERE first_name = ? AND last_name = ? AND grade = ?", 
            (first_name, last_name, grade)
        )
        user = cursor.fetchone()
        
        if user:
            # User exists, get their ID
            user_id = user[0]
        else:
            # User doesn't exist, create new user
            cursor.execute(
                "INSERT INTO users (first_name, last_name, grade) VALUES (?, ?, ?)",
                (first_name, last_name, grade)
            )
            conn.commit()
            user_id = cursor.lastrowid
        
        # Record this session
        cursor.execute(
            "INSERT INTO sessions (user_id, login_time) VALUES (?, ?)",
            (user_id, datetime.datetime.now())
        )
        conn.commit()
        conn.close()
        
        # Store current user info
        self.current_user = {
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "grade": grade
        }
        
        # Show welcome message
        messagebox.showinfo("Welcome!", f"Welcome, {first_name}! 🎉", icon=messagebox.INFO)
        
        # Hide login frame
        self.login_frame.pack_forget()
        
        # Call the callback function if provided
        if self.on_successful_login:
            self.on_successful_login(self.current_user)
    
    def show_login(self):
        """Show the login frame"""
        self.login_frame.pack(fill="both", expand=True)
    
    def get_current_user(self):
        """Return the current logged-in user"""
        return self.current_user


class EmotionDetectorApp:
    def __init__(self, root, user=None):
        self.root = root
        self.user = user
        
        # Expanded dataset for emotion detection
        self.data = {
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
        self.emotion_emojis = {
            "happy": "😊",
            "sad": "😢",
            "angry": "😡",
            "neutral": "😐",
            "surprised": "😮",
            "scared": "😨",
            "excited": "🎉"
        }
        
        # Kid-friendly emotion descriptions
        self.emotion_descriptions = {
            "happy": "feeling good inside, like when you get a present!",
            "sad": "feeling down, like when you drop your ice cream cone",
            "angry": "feeling mad, like when someone breaks your toy",
            "neutral": "feeling just okay, not good or bad",
            "surprised": "feeling shocked, like when something unexpected happens",
            "scared": "feeling afraid, like when you watch a spooky movie",
            "excited": "feeling super happy about something that's going to happen"
        }
        
        # Train a simple Naive Bayes model with TF-IDF
        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(self.data["texts"])
        self.model = MultinomialNB()
        self.model.fit(self.X, self.data["emotions"])
        
        # Global variables for survey responses
        self.pre_survey_responses = {}
        self.post_survey_responses = {}
        
        # Gamification variables
        self.points = 0
        self.badges = []
        self.progress = 0
        self.challenges = {
            "detect_5_in_a_row": {"goal": 5, "progress": 0, "completed": False},
            "train_10_examples": {"goal": 10, "progress": 0, "completed": False}
        }
        
        # Storyline variables
        self.storyline = [
            "Welcome to the world of AI! 🌍",
            "You are training a robot named 'EmoBot' to understand feelings.",
            "Help EmoBot learn by detecting emotions and adding training data.",
            "Complete challenges to unlock rewards and become an AI expert!"
        ]
        
        # Fun Facts about AI
        self.fun_facts = [
            "Robots don't have feelings, but they can learn to recognize yours!",
            "Your tablet can understand you when you talk because of AI!",
            "AI can learn from mistakes, just like you do in school!",
            "Self-driving cars use AI to see the road, like robot eyes!",
            "AI needs lots of examples to learn, just like you needed to practice reading!",
            "When you use a translation app, AI helps you understand other languages!",
            "AI can beat champion players at chess and video games!",
            "AI can recognize your pets in photos but might get confused by cartoons!",
            "The characters in video games that you play against use AI to make decisions!"
        ]
        
        # Create main app frame and initialize pages
        self.main_frame = tk.Frame(self.root, bg=COLORS["background"])
        self.pages = {}
        self.create_pages()
        
    def create_pages(self):
        self.pages = {
            "welcome": self.create_welcome_page(),
            "pre_survey": self.create_pre_survey_page(),
            "instructions": self.create_instructions_page(),
            "main_app": self.create_main_app_page(),
            "post_survey": self.create_post_survey_page()
        }
    
    def show(self):
        """Show the main app frame and the welcome page"""
        self.main_frame.pack(fill="both", expand=True)
        self.show_page("welcome")
        
        # If we have a user, personalize the welcome message
        if self.user:
            self.personalize_welcome_page()
    
    def personalize_welcome_page(self):
        """Personalize welcome page with user information"""
        # Find the welcome label in the scrollable frame
        for child in self.pages["welcome"].winfo_children():
            if isinstance(child, tk.Canvas):
                interior = child.winfo_children()[0]  # Get the interior frame
                welcome_label = interior.winfo_children()[0]  # First child should be the welcome label
                welcome_label.config(text=f"Welcome to the AI Emotion Detector, {self.user['first_name']}! 🧠")
                break
    
    def show_page(self, page):
        """Show a page and reset scroll position to top"""
        for frame in self.pages.values():
            frame.pack_forget()
        self.pages[page].pack(fill="both", expand=True)
        
        # Reset scroll position to top
        for child in self.pages[page].winfo_children():
            if isinstance(child, tk.Canvas):
                child.yview_moveto(0)  # Reset scroll position to top
    
    def create_welcome_page(self):
        frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        
        # Create scrollable frame
        canvas, content_frame = create_scrollable_frame(frame)
        
        # Add colorful welcome message
        welcome_label = tk.Label(content_frame, text="Welcome to the AI Emotion Detector! 🧠", 
                              font=FONTS["title"], bg=COLORS["background"], fg=COLORS["primary"])
        welcome_label.pack(pady=40)
        
        # Add robot character
        robot_label = tk.Label(content_frame, text="🤖", font=("Arial", 72), bg=COLORS["background"])
        robot_label.pack(pady=20)
        
        # Add explanation
        explanation = tk.Label(content_frame, 
                            text="Get ready to teach a robot how to understand feelings!\nAre you up for the challenge?", 
                            font=FONTS["normal"], bg=COLORS["background"], fg=COLORS["text"])
        explanation.pack(pady=20)
        
        # Add next button with bounce effect
        next_button = BouncingButton(content_frame, text="Let's Go! →", font=FONTS["subtitle"], 
                                  bg=COLORS["secondary"], fg="white", 
                                  command=lambda: self.show_page("pre_survey"))
        next_button.pack(pady=20)
        
        return frame
    
    def create_pre_survey_page(self):
        frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        
        # Create scrollable frame
        canvas, content_frame = create_scrollable_frame(frame)
        
        # Add title with robot emoji
        title_frame = tk.Frame(content_frame, bg=COLORS["background"])
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="AI Explorer Survey ", 
                            font=FONTS["title"], bg=COLORS["background"], fg=COLORS["primary"])
        title_label.pack(side="left")
        
        robot_label = tk.Label(title_frame, text="🤖", font=("Arial", 32), bg=COLORS["background"])
        robot_label.pack(side="left", padx=10)
        
        # Add subtitle
        subtitle = tk.Label(content_frame, text="What do you know about AI?", 
                         font=FONTS["subtitle"], bg=COLORS["background"], fg=COLORS["text"])
        subtitle.pack(pady=10)
        
        # Create colorful question frames
        # Question 1
        q1_frame = tk.Frame(content_frame, bg=COLORS["accent"], relief="raised", bd=2)
        q1_frame.pack(pady=15, padx=30, fill="x")
        
        q1_label = tk.Label(q1_frame, text="1. Have you heard of AI before?", 
                         font=FONTS["normal"], bg=COLORS["accent"])
        q1_label.pack(pady=10, padx=10, anchor="w")
        
        q1_options_frame = tk.Frame(q1_frame, bg=COLORS["accent"])
        q1_options_frame.pack(pady=5, padx=10, fill="x")
        
        q1_var = tk.StringVar()
        for i, option in enumerate(["Yes! 👍", "No 🤔", "Maybe 🤷"]):
            rb = tk.Radiobutton(q1_options_frame, text=option, variable=q1_var, value=option, 
                             font=FONTS["normal"], bg=COLORS["accent"], 
                             activebackground=COLORS["accent"])
            rb.pack(side="left", padx=20)
        self.pre_survey_responses["q1"] = q1_var
        
        # Question 2
        q2_frame = tk.Frame(content_frame, bg="#B5EAD7", relief="raised", bd=2)
        q2_frame.pack(pady=15, padx=30, fill="x")
        
        q2_label = tk.Label(q2_frame, text="2. What do you think AI does?", 
                         font=FONTS["normal"], bg="#B5EAD7")
        q2_label.pack(pady=10, padx=10, anchor="w")
        
        q2_options_frame = tk.Frame(q2_frame, bg="#B5EAD7")
        q2_options_frame.pack(pady=5, padx=10, fill="x")
        
        q2_var = tk.StringVar()
        options = [
            "A) Thinks like a human 🧠", 
            "B) Learns from examples 📚", 
            "C) Is just a robot 🤖", 
            "D) Not sure 🤷"
        ]
        
        for i, option in enumerate(options):
            rb = tk.Radiobutton(q2_options_frame, text=option, variable=q2_var, value=option, 
                             font=FONTS["normal"], bg="#B5EAD7", 
                             activebackground="#B5EAD7")
            rb.grid(row=i//2, column=i%2, padx=20, pady=5, sticky="w")
        self.pre_survey_responses["q2"] = q2_var
        
        # Question 3
        q3_frame = tk.Frame(content_frame, bg="#C7CEEA", relief="raised", bd=2)
        q3_frame.pack(pady=15, padx=30, fill="x")
        
        q3_label = tk.Label(q3_frame, text="3. Can you name an example of AI you've seen or used?", 
                         font=FONTS["normal"], bg="#C7CEEA")
        q3_label.pack(pady=10, padx=10, anchor="w")
        
        q3_entry = tk.Entry(q3_frame, font=FONTS["normal"], width=40)
        q3_entry.pack(pady=10, padx=20)
        self.pre_survey_responses["q3"] = q3_entry
        
        # Next button
        next_button = BouncingButton(content_frame, text="Next Step! →", font=FONTS["subtitle"], 
                                   bg=COLORS["secondary"], fg="white",
                                   command=lambda: self.show_page("instructions"))
        next_button.pack(pady=20)
        
        return frame
    
    def create_instructions_page(self):
        frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        
        # Create scrollable frame
        canvas, content_frame = create_scrollable_frame(frame)
        
        # Add title
        title_label = tk.Label(content_frame, text="How to Use EmoBot 🤖", 
                            font=FONTS["title"], bg=COLORS["background"], fg=COLORS["primary"])
        title_label.pack(pady=20)
        
        # Create instruction cards
        instruction_colors = ["#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA", "#FFB7B2"]
        
        instructions = [
            {
                "title": "1. Type a sentence 📝",
                "text": "Enter how you feel or a sentence about emotions in the text box.",
                "icon": "✏️"
            },
            {
                "title": "2. Detect the emotion 🔍",
                "text": "Click 'Detect Emotion' and see what EmoBot thinks the feeling is!",
                "icon": "🔍"
            },
            {
                "title": "3. Teach EmoBot new emotions 🧠",
                "text": "Add your own examples to help EmoBot learn more about feelings!",
                "icon": "🧠"
            },
            {
                "title": "4. Earn points and badges 🏆",
                "text": "Complete challenges to become an AI Expert!",
                "icon": "🎮"
            },
            {
                "title": "5. Have fun learning! 🎉",
                "text": "Explore how AI works through games and activities!",
                "icon": "🎓"
            }
        ]
        
        for i, instruction in enumerate(instructions):
            card_frame = tk.Frame(content_frame, bg=instruction_colors[i % len(instruction_colors)], 
                               relief="raised", bd=2)
            card_frame.pack(pady=10, padx=20, fill="x")
            
            # Title with icon
            title_frame = tk.Frame(card_frame, bg=instruction_colors[i % len(instruction_colors)])
            title_frame.pack(pady=5, padx=10, fill="x")
            
            icon_label = tk.Label(title_frame, text=instruction["icon"], 
                               font=("Arial", 32), bg=instruction_colors[i % len(instruction_colors)])
            icon_label.pack(side="left", padx=10)
            
            title_label = tk.Label(title_frame, text=instruction["title"], 
                                font=FONTS["subtitle"], bg=instruction_colors[i % len(instruction_colors)])
            title_label.pack(side="left", padx=10)
            
            # Description
            desc_label = tk.Label(card_frame, text=instruction["text"], 
                               font=FONTS["normal"], bg=instruction_colors[i % len(instruction_colors)], 
                               wraplength=550, justify="left")
            desc_label.pack(pady=10, padx=20, fill="x")
        
        # Start button
        start_button = BouncingButton(content_frame, text="Start Adventure! 🚀", font=FONTS["subtitle"], 
                                    bg=COLORS["secondary"], fg="white",
                                    command=lambda: self.show_page("main_app"))
        start_button.pack(pady=20)
        
        return frame
    
    def create_main_app_page(self):
        frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        
        # Create scrollable frame
        canvas, content_frame = create_scrollable_frame(frame)
        
        # Add personalized greeting
        if self.user:
            greeting_label = tk.Label(content_frame, 
                                    text=f"Hello, {self.user['first_name']}! Let's explore AI emotions!", 
                                    font=FONTS["subtitle"], bg=COLORS["background"], fg=COLORS["primary"])
            greeting_label.pack(pady=15, padx=20)
        
        # Header section with points and progress
        header_frame = tk.Frame(content_frame, bg=COLORS["background"])
        header_frame.pack(pady=10, padx=20, fill="x")
        
        # Points display
        points_frame = tk.Frame(header_frame, bg="#FFD166", bd=2, relief="raised")
        points_frame.pack(side="left", padx=10)
        
        self.points_label = tk.Label(points_frame, text=f"Points: {self.points}", 
                                   font=FONTS["normal"], bg="#FFD166", fg=COLORS["text"])
        self.points_label.pack(pady=5, padx=10)
        
        # Progress bar
        progress_frame = tk.Frame(header_frame, bg=COLORS["background"])
        progress_frame.pack(side="right", fill="x", expand=True, padx=10)
        
        progress_label = tk.Label(progress_frame, text="Your AI Learning Progress:", 
                                font=FONTS["small"], bg=COLORS["background"])
        progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(fill="x")
        self.progress_bar["value"] = self.progress
        
        # Storyline section
        storyline_frame = tk.LabelFrame(content_frame, text="EmoBot's Adventure 📖", 
                                      font=FONTS["subtitle"], bg="#E2F0CB", bd=2)
        storyline_frame.pack(pady=15, padx=20, fill="x")
        
        self.storyline_text = tk.Text(storyline_frame, height=5, width=60, 
                                    font=FONTS["normal"], wrap="word", 
                                    bg="#E2F0CB", bd=0)
        self.storyline_text.pack(pady=10, padx=10, fill="x")
        
        # Insert initial storyline
        for line in self.storyline:
            self.storyline_text.insert("end", f"{line}\n")
        self.storyline_text.config(state="disabled")  # Make read-only
        
        # Fun fact section
        fun_fact_frame = tk.LabelFrame(content_frame, text="Fun AI Fact 💡", 
                                     font=FONTS["subtitle"], bg="#B5EAD7", bd=2)
        fun_fact_frame.pack(pady=15, padx=20, fill="x")
        
        self.fun_fact_label = tk.Label(fun_fact_frame, text="", 
                                     font=FONTS["normal"], bg="#B5EAD7", 
                                     wraplength=600, justify="left")
        self.fun_fact_label.pack(pady=10, padx=10)
        self.show_fun_fact()  # Show initial fun fact
        
        # Create two-column layout for main content
        columns_frame = tk.Frame(content_frame, bg=COLORS["background"])
        columns_frame.pack(pady=10, padx=10, fill="x")
        
        # Left column - Input and detection
        left_col = tk.Frame(columns_frame, bg=COLORS["background"])
        left_col.pack(side="left", fill="both", expand=True, padx=5)
        
        # Right column - Challenges and training
        right_col = tk.Frame(columns_frame, bg=COLORS["background"])
        right_col.pack(side="right", fill="both", expand=True, padx=5)
        
        # Input section
        input_frame = tk.LabelFrame(left_col, text="Tell EmoBot how you feel 💬", 
                                  font=FONTS["subtitle"], bg="#FFDAC1", bd=2)
        input_frame.pack(pady=10, fill="x")
        
        input_text = tk.Text(input_frame, height=4, width=30, 
                           font=FONTS["normal"], bd=2, relief="solid")
        input_text.pack(pady=10, padx=10, fill="x")
        
        input_text.insert("1.0", "Example: I am so happy today!")  # Example text
        
        # Create frame for button
        button_frame = tk.Frame(input_frame, bg="#FFDAC1")
        button_frame.pack(pady=10)
        
        detect_button = BouncingButton(button_frame, text="Detect Emotion! 🔍", 
                                     font=FONTS["normal"], bg=COLORS["secondary"], fg="white",
                                     command=lambda: self.detect_emotion(input_text))
        detect_button.pack()
        
        # Result section
        result_frame = tk.Frame(left_col, bg="#FFB7B2", bd=2, relief="raised")
        result_frame.pack(pady=10, fill="x")
        
        self.result_label = tk.Label(result_frame, text="AI will detect your emotion here", 
                                   font=FONTS["subtitle"], bg="#FFB7B2", fg=COLORS["text"])
        self.result_label.pack(pady=15, padx=10)
        
        # Explanation section
        explanation_frame = tk.LabelFrame(left_col, text="How EmoBot thinks 🧠", 
                                        font=FONTS["subtitle"], bg="#C7CEEA", bd=2)
        explanation_frame.pack(pady=10, fill="x")
        
        self.explanation_label = tk.Label(explanation_frame, text="After you enter text, I'll explain how I detected the emotion!", 
                                       font=FONTS["normal"], bg="#C7CEEA", 
                                       wraplength=300, justify="left")
        self.explanation_label.pack(pady=10, padx=10)
        
        # Word importance section
        word_importance_frame = tk.LabelFrame(left_col, text="Important Words 📊", 
                                           font=FONTS["subtitle"], bg="#B5EAD7", bd=2)
        word_importance_frame.pack(pady=10, fill="x")
        
        self.word_importance_label = tk.Label(word_importance_frame, 
                                          text="I'll show which words helped me most in making my decision!", 
                                          font=FONTS["normal"], bg="#B5EAD7", 
                                          wraplength=300, justify="left")
        self.word_importance_label.pack(pady=10, padx=10)
        
        # Challenges section
        self.challenge_frame = tk.LabelFrame(right_col, text="Your Missions 🚀", 
                                          font=FONTS["subtitle"], bg="#FFD166", bd=2)
        self.challenge_frame.pack(pady=10, fill="x")
        
        # Add challenge title
        title_label = tk.Label(self.challenge_frame, text="Challenges:", 
                            font=FONTS["subtitle"], bg="#FFD166")
        title_label.pack(pady=5)
        
        # Add challenge labels
        for key, challenge in self.challenges.items():
            # Create frame for each challenge
            c_frame = tk.Frame(self.challenge_frame, bg="#FFD166")
            c_frame.pack(fill="x", pady=5)
            
            # Add emoji based on progress
            emoji = "🔴"  # Not started
            if challenge["completed"]:
                emoji = "✅"  # Completed
            elif challenge["progress"] > 0:
                emoji = "🟡"  # In progress
                
            # Create label
            c_label = tk.Label(c_frame, 
                             text=f"{emoji} {key.replace('_', ' ').title()}: {challenge['progress']}/{challenge['goal']}", 
                             font=FONTS["normal"], bg="#FFD166")
            c_label.pack(pady=2)
        
        # Training section
        training_frame = tk.LabelFrame(right_col, text="Train EmoBot 🧠", 
                                     font=FONTS["subtitle"], bg="#E2F0CB", bd=2)
        training_frame.pack(pady=10, fill="x")
        
        training_label = tk.Label(training_frame, 
                               text="Help EmoBot learn by adding more examples of emotions!", 
                               font=FONTS["normal"], bg="#E2F0CB", 
                               wraplength=300, justify="left")
        training_label.pack(pady=10, padx=10)
        
        text_label = tk.Label(training_frame, text="Enter Text:", 
                           font=FONTS["normal"], bg="#E2F0CB")
        text_label.pack(pady=5, padx=10, anchor="w")
        
        training_text = tk.Text(training_frame, height=3, width=30, 
                              font=FONTS["normal"], bd=2, relief="solid")
        training_text.pack(pady=5, padx=10, fill="x")
        
        training_text.insert("1.0", "Example: I feel excited about my birthday!")  # Example text
        
        emotion_frame = tk.Frame(training_frame, bg="#E2F0CB")
        emotion_frame.pack(pady=5, padx=10, fill="x")
        
        emotion_label = tk.Label(emotion_frame, text="Select Emotion:", 
                              font=FONTS["normal"], bg="#E2F0CB")
        emotion_label.pack(side="left", pady=5)
        
        emotion_var = tk.StringVar()
        emotion_dropdown = ttk.Combobox(emotion_frame, textvariable=emotion_var, 
                                      values=list(self.emotion_emojis.keys()), 
                                      font=FONTS["normal"], width=12)
        emotion_dropdown.pack(side="left", padx=10)
        
        # Create frame for button
        train_button_frame = tk.Frame(training_frame, bg="#E2F0CB")
        train_button_frame.pack(pady=10)
        
        add_data_button = BouncingButton(train_button_frame, text="Teach EmoBot! 📚", 
                                       font=FONTS["normal"], bg=COLORS["primary"], fg="white",
                                       command=lambda: self.add_training_data(training_text, emotion_var))
        add_data_button.pack()
        
        # Emotion guide section
        emotions_frame = tk.LabelFrame(right_col, text="Emotion Guide 📖", 
                                     font=FONTS["subtitle"], bg="#FFB7B2", bd=2)
        emotions_frame.pack(pady=10, fill="x")
        
        # Add each emotion with description
        for emotion, emoji in self.emotion_emojis.items():
            emotion_row = tk.Frame(emotions_frame, bg="#FFB7B2")
            emotion_row.pack(pady=5, padx=5, fill="x")
            
            emotion_emoji = tk.Label(emotion_row, text=emoji, 
                                   font=("Arial", 24), bg="#FFB7B2")
            emotion_emoji.pack(side="left", padx=5)
            
            emotion_name = tk.Label(emotion_row, text=f"{emotion.capitalize()}: ", 
                                  font=FONTS["normal"], bg="#FFB7B2", fg=COLORS["text"])
            emotion_name.pack(side="left")
            
            emotion_desc = tk.Label(emotion_row, 
                                  text=self.emotion_descriptions.get(emotion, ""), 
                                  font=FONTS["small"], bg="#FFB7B2", fg=COLORS["text"], 
                                  wraplength=200, justify="left")
            emotion_desc.pack(side="left", padx=5)
        
        # Next/Finish button at bottom
        next_button = BouncingButton(content_frame, text="Finish Adventure! 🎉", 
                                   font=FONTS["subtitle"], bg=COLORS["secondary"], fg="white",
                                   command=lambda: self.show_page("post_survey"))
        next_button.pack(pady=20)
        
        return frame
    
    def create_post_survey_page(self):
        frame = tk.Frame(self.main_frame, bg=COLORS["background"])
        
        # Create scrollable frame
        canvas, content_frame = create_scrollable_frame(frame)
        
        # Add title with confetti emoji
        title_frame = tk.Frame(content_frame, bg=COLORS["background"])
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="AI Explorer Checkpoint ", 
                            font=FONTS["title"], bg=COLORS["background"], fg=COLORS["primary"])
        title_label.pack(side="left")
        
        emoji_label = tk.Label(title_frame, text="🎉", font=("Arial", 32), bg=COLORS["background"])
        emoji_label.pack(side="left", padx=10)
        
        # Add subtitle
        subtitle = tk.Label(content_frame, text="Tell us what you learned about AI!", 
                         font=FONTS["subtitle"], bg=COLORS["background"], fg=COLORS["text"])
        subtitle.pack(pady=10)
        
        # Create colorful question frames
        # Question 1
        q1_frame = tk.Frame(content_frame, bg="#FFDAC1", relief="raised", bd=2)
        q1_frame.pack(pady=15, padx=30, fill="x")
        
        q1_label = tk.Label(q1_frame, text="1. Now that you've played, how would you define AI?", 
                         font=FONTS["normal"], bg="#FFDAC1")
        q1_label.pack(pady=10, padx=10, anchor="w")
        
        q1_options_frame = tk.Frame(q1_frame, bg="#FFDAC1")
        q1_options_frame.pack(pady=5, padx=10, fill="x")
        
        q1_var = tk.StringVar()
        options = [
            "A) A machine that learns from examples 📚", 
            "B) A thinking robot 🤖", 
            "C) Magic ✨", 
            "D) Still not sure 🤷"
        ]
        
        for i, option in enumerate(options):
            rb = tk.Radiobutton(q1_options_frame, text=option, variable=q1_var, value=option, 
                             font=FONTS["normal"], bg="#FFDAC1", 
                             activebackground="#FFDAC1")
            rb.grid(row=i//2, column=i%2, padx=20, pady=5, sticky="w")
        self.post_survey_responses["q1"] = q1_var
        
        # Question 2
        q2_frame = tk.Frame(content_frame, bg="#E2F0CB", relief="raised", bd=2)
        q2_frame.pack(pady=15, padx=30, fill="x")
        
        q2_label = tk.Label(q2_frame, text="2. What does AI need to learn emotions?", 
                         font=FONTS["normal"], bg="#E2F0CB")
        q2_label.pack(pady=10, padx=10, anchor="w")
        
        q2_options_frame = tk.Frame(q2_frame, bg="#E2F0CB")
        q2_options_frame.pack(pady=5, padx=10, fill="x")
        
        q2_var = tk.StringVar()
        options = [
            "A) A big book of emotions 📚", 
            "B) Examples of emotions from people 👥", 
            "C) Nothing, AI already knows everything 🧠", 
            "D) Not sure 🤷"
        ]
        
        for i, option in enumerate(options):
            rb = tk.Radiobutton(q2_options_frame, text=option, variable=q2_var, value=option, 
                             font=FONTS["normal"], bg="#E2F0CB", 
                             activebackground="#E2F0CB")
            rb.grid(row=i//2, column=i%2, padx=20, pady=5, sticky="w")
        self.post_survey_responses["q2"] = q2_var
        
        # Question 3
        q3_frame = tk.Frame(content_frame, bg="#B5EAD7", relief="raised", bd=2)
        q3_frame.pack(pady=15, padx=30, fill="x")
        
        q3_label = tk.Label(q3_frame, text="3. Can AI make mistakes? If yes, why?", 
                         font=FONTS["normal"], bg="#B5EAD7")
        q3_label.pack(pady=10, padx=10, anchor="w")
        
        q3_entry = tk.Entry(q3_frame, font=FONTS["normal"], width=40)
        q3_entry.pack(pady=10, padx=20)
        self.post_survey_responses["q3"] = q3_entry
        
        # Question 4
        q4_frame = tk.Frame(content_frame, bg="#C7CEEA", relief="raised", bd=2)
        q4_frame.pack(pady=15, padx=30, fill="x")
        
        q4_label = tk.Label(q4_frame, text="4. What was the most surprising thing you learned about AI?", 
                         font=FONTS["normal"], bg="#C7CEEA")
        q4_label.pack(pady=10, padx=10, anchor="w")
        
        q4_entry = tk.Entry(q4_frame, font=FONTS["normal"], width=40)
        q4_entry.pack(pady=10, padx=20)
        self.post_survey_responses["q4"] = q4_entry
        
        # Question 5
        q5_frame = tk.Frame(content_frame, bg="#FFB7B2", relief="raised", bd=2)
        q5_frame.pack(pady=15, padx=30, fill="x")
        
        q5_label = tk.Label(q5_frame, text="5. If you could improve EmoBot, what would you add?", 
                         font=FONTS["normal"], bg="#FFB7B2")
        q5_label.pack(pady=10, padx=10, anchor="w")
        
        q5_entry = tk.Entry(q5_frame, font=FONTS["normal"], width=40)
        q5_entry.pack(pady=10, padx=20)
        self.post_survey_responses["q5"] = q5_entry
        
        # Submit button
        submit_button = BouncingButton(content_frame, text="Finish Adventure! 🎉", 
                                     font=FONTS["subtitle"], bg=COLORS["secondary"], fg="white",
                                     command=self.show_feedback)
        submit_button.pack(pady=20)
        
        return frame
    
    def detect_emotion(self, input_text):
        text = input_text.get("1.0", "end-1c")  # Get user input
        if not text.strip():
            messagebox.showinfo("Oops!", "Please enter some text! EmoBot needs to read something. 📝", 
                             icon=messagebox.INFO)
            return
        
        # Predict emotion
        text_vec = self.vectorizer.transform([text])
        emotion = self.model.predict(text_vec)[0]
        probabilities = self.model.predict_proba(text_vec)[0]
        
        # Show result with emoji and animation
        result_text = f"AI detects: {emotion.capitalize()} {self.emotion_emojis.get(emotion, '')}"
        self.result_label.config(text=result_text, fg=COLORS["primary"])
        
        # Flash animation on result
        self.flash_label(self.result_label)
        
        # Explain AI process with kid-friendly language
        self.explain_ai_process(text, emotion, probabilities, text_vec)
        
        # Visualize word importance with fun animation
        self.visualize_word_importance(text, text_vec)
        
        # Award points with celebration
        self.points += 10
        self.update_points(celebration=True)
        
        # Update challenges
        self.update_challenges("detect_5_in_a_row")
        
        # Check for badges
        if self.points >= 50 and "AI Novice" not in self.badges:
            self.badges.append("AI Novice")
            messagebox.showinfo("Badge Unlocked!", "You unlocked the 'AI Novice' badge! 🎉", 
                              icon=messagebox.INFO)
        if self.points >= 100 and "AI Expert" not in self.badges:
            self.badges.append("AI Expert")
            messagebox.showinfo("Badge Unlocked!", "You unlocked the 'AI Expert' badge! 🎉", 
                              icon=messagebox.INFO)
        
        # Update progress with animation
        self.progress += 10
        self.update_progress()
        
        # Update storyline
        self.update_storyline(f"EmoBot detected: {emotion.capitalize()} {self.emotion_emojis.get(emotion, '')}")
        
        # Show a random fun fact
        self.show_fun_fact()
    
    def flash_label(self, label):
        """Create a flashing highlight effect on a label"""
        original_bg = label.cget("background")
        original_fg = label.cget("foreground")
        
        label.config(bg=COLORS["accent"], fg=COLORS["text"])
        label.after(300, lambda: label.config(bg=original_bg, fg=original_fg))
    
    def explain_ai_process(self, text, emotion, probabilities, text_vec):
        explanation = (
            "How AI works (kid-friendly version):\n\n"
            "1. The AI reads the words you typed\n"
            "2. It remembers other examples it has seen before\n"
            "3. It makes its best guess about the feeling\n\n"
            f"It thinks this is '{emotion}' because it found words like "
        )
        
        # Get important words if possible
        try:
            important_words = self.vectorizer.inverse_transform(text_vec)[0]
            if important_words:
                word_list = ", ".join([f"'{word}'" for word in important_words[:3]])
                explanation += word_list
            else:
                explanation += "these in your text"
        except:
            explanation += "these in your text"
            
        explanation += ".\n\n"
        explanation += f"EmoBot is {self.emotion_descriptions.get(emotion, 'feeling something')}\n\n"
        explanation += "EmoBot's confidence levels:\n"
        
        # Show probabilities with emoji bars
        for i, emotion_class in enumerate(self.model.classes_):
            prob_percent = int(probabilities[i] * 100)
            emoji_bar = "🟦" * (prob_percent // 10 + 1)  # Create emoji bar chart
            explanation += f"{emotion_class.capitalize()}: {emoji_bar} {prob_percent}%\n"
            
        self.explanation_label.config(text=explanation)
    
    def visualize_word_importance(self, text, text_vec):
        word_importance_text = "Top words that helped EmoBot decide:\n"
        
        try:
            # Calculate word importance
            word_importance = np.array(text_vec.sum(axis=0)).flatten()
            words = self.vectorizer.get_feature_names_out()
            
            # Create word-importance pairs
            important_words = [
                (words[i], word_importance[i])
                for i in range(len(words))
                if word_importance[i] > 0 and words[i] in text.lower()
            ]
            
            # Sort by importance
            important_words.sort(key=lambda x: x[1], reverse=True)
            
            # Display top words with fun emoji indicators
            for word, importance in important_words[:5]:
                stars = "⭐" * (int(importance * 5) + 1)
                word_importance_text += f"{word}: {stars}\n"
                
        except Exception as e:
            # Fallback if error occurs
            word_importance_text += "EmoBot is still learning to explain its decisions.\n"
            word_importance_text += "The more examples you give, the better it gets!"
            
        self.word_importance_label.config(text=word_importance_text)
    
    def add_training_data(self, training_text, emotion_var):
        text = training_text.get("1.0", "end-1c")
        emotion = emotion_var.get()
        if text.strip() and emotion:
            self.data["texts"].append(text)
            self.data["emotions"].append(emotion.lower())
            self.retrain_model()
            
            # Show success message with animation
            messagebox.showinfo("Amazing!", "EmoBot learned something new! You're a great teacher! 🎓", 
                              icon=messagebox.INFO)
            training_text.delete("1.0", "end")
            
            # Award points with celebration
            self.points += 20
            self.update_points(celebration=True)
            
            # Update challenges
            self.update_challenges("train_10_examples")
            
            # Update progress with animation
            self.progress += 20
            self.update_progress()
            
            # Update storyline
            self.update_storyline(f"EmoBot learned: {emotion.capitalize()} {self.emotion_emojis.get(emotion.lower(), '')}")
            
            # Show a random fun fact
            self.show_fun_fact()
        else:
            messagebox.showinfo("Oops!", "Please enter both text and select an emotion! EmoBot needs both to learn. 📚", 
                              icon=messagebox.INFO)
    
    def retrain_model(self):
        self.X = self.vectorizer.fit_transform(self.data["texts"])
        self.model.fit(self.X, self.data["emotions"])
    
    def update_points(self, celebration=False):
        self.points_label.config(text=f"Points: {self.points}")
        
        # Add celebration effect if requested
        if celebration:
            original_font = self.points_label.cget("font")
            larger_font = (original_font[0], original_font[1] + 6, original_font[2])
            self.points_label.config(font=larger_font, fg=COLORS["primary"])
            self.points_label.after(300, lambda: self.points_label.config(
                font=original_font, fg=COLORS["text"]))
    
    def update_progress(self):
        self.progress_bar["value"] = min(self.progress, 100)
        
        # Check for completion
        if self.progress >= 100 and not hasattr(self, 'progress_completed'):
            messagebox.showinfo("Congratulations!", "You've completed the training! EmoBot is so happy! 🎉", 
                              icon=messagebox.INFO)
            self.progress_completed = True
    
    def update_challenges(self, challenge_key):
        if not self.challenges[challenge_key]["completed"]:
            self.challenges[challenge_key]["progress"] += 1
            
            # Update challenge display
            for widget in self.challenge_frame.winfo_children():
                widget.destroy()
                
            # Add challenge title
            title_label = tk.Label(self.challenge_frame, text="Challenges:", 
                                  font=FONTS["subtitle"], bg="#FFD166")
            title_label.pack(pady=5)
            
            # Add updated challenge labels
            for key, challenge in self.challenges.items():
                # Create frame for each challenge
                c_frame = tk.Frame(self.challenge_frame, bg="#FFD166")
                c_frame.pack(fill="x", pady=5)
                
                # Add emoji based on progress
                emoji = "🔴"  # Not started
                if challenge["completed"]:
                    emoji = "✅"  # Completed
                elif challenge["progress"] > 0:
                    emoji = "🟡"  # In progress
                    
                # Create label
                c_label = tk.Label(c_frame, 
                                 text=f"{emoji} {key.replace('_', ' ').title()}: {challenge['progress']}/{challenge['goal']}", 
                                 font=FONTS["normal"], bg="#FFD166")
                c_label.pack(pady=2)
                
                # Check if just completed
                if challenge["progress"] >= challenge["goal"] and not challenge["completed"]:
                    challenge["completed"] = True
                    
                    # Show celebration message
                    messagebox.showinfo("Challenge Complete!", 
                                      f"You completed the '{key.replace('_', ' ')}' challenge! 🎉", 
                                      icon=messagebox.INFO)
                    
                    # Award bonus points
                    self.points += 50
                    self.update_points(celebration=True)
    
    def update_storyline(self, message):
        self.storyline.append(message)
        
        # Update storyline text widget
        self.storyline_text.config(state="normal")
        self.storyline_text.insert("end", f"\n{message}")
        self.storyline_text.config(state="disabled")
        self.storyline_text.see("end")  # Scroll to new content
    
    def show_fun_fact(self):
        fun_fact = random.choice(self.fun_facts)
        self.fun_fact_label.config(text=f"Fun Fact: {fun_fact}")
        
    def show_feedback(self):
        """Show feedback to user and save results"""
        # Create certificate frame
        certificate_frame = tk.Toplevel(self.root)
        certificate_frame.title("AI Explorer Certificate")
        certificate_frame.geometry("600x500")
        certificate_frame.configure(bg="#FFFFFF")
        
        # Add decorative border
        border_canvas = tk.Canvas(certificate_frame, bg="#FFFFFF", highlightthickness=0)
        border_canvas.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Draw rainbow border
        rainbow_colors = ["#FF9AA2", "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", "#C7CEEA"]
        border_width = 10
        
        for i, color in enumerate(rainbow_colors):
            inset = i * border_width / len(rainbow_colors)
            border_canvas.create_rectangle(
                inset, inset, 600 - inset, 500 - inset,
                outline=color, width=border_width / len(rainbow_colors), fill=""
            )
        
        # Add certificate content
        content_frame = tk.Frame(border_canvas, bg="#FFFFFF")
        border_canvas.create_window(300, 250, window=content_frame)
        
        # Add certificate title
        title_label = tk.Label(content_frame, text="Certificate of Achievement", 
                            font=("Comic Sans MS", 24, "bold"), bg="#FFFFFF", fg=COLORS["primary"])
        title_label.pack(pady=10)
        
        # Add robot character
        robot_label = tk.Label(content_frame, text="🤖", font=("Arial", 48), bg="#FFFFFF")
        robot_label.pack(pady=10)
        
        # Add personalized message
        name = self.user["first_name"] if self.user else "Explorer"
        message_label = tk.Label(content_frame, 
                              text=f"This certifies that\n{name}\nhas become an\nAI Emotion Detection Expert!", 
                              font=("Comic Sans MS", 14), bg="#FFFFFF", justify="center")
        message_label.pack(pady=10)
        
        # Add points and badges
        stats_label = tk.Label(content_frame, 
                            text=f"Points earned: {self.points}\nBadges collected: {len(self.badges)}", 
                            font=("Comic Sans MS", 12), bg="#FFFFFF")
        stats_label.pack(pady=10)
        
        # Add date
        today = datetime.datetime.now().strftime("%B %d, %Y")
        date_label = tk.Label(content_frame, text=f"Date: {today}", 
                           font=("Comic Sans MS", 12), bg="#FFFFFF")
        date_label.pack(pady=10)
        
        # Save survey responses to the database if we have a user
        if self.user:
            self.save_survey_responses()
    
    def save_survey_responses(self):
        """Save survey responses to the database"""
        try:
            conn = sqlite3.connect('data/users.db')
            cursor = conn.cursor()
            
            # Create survey_responses table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                survey_type TEXT,
                question TEXT,
                answer TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # Save pre-survey responses
            for question, var in self.pre_survey_responses.items():
                answer = var.get() if isinstance(var, tk.StringVar) else var.get()
                cursor.execute(
                    "INSERT INTO survey_responses (user_id, survey_type, question, answer) VALUES (?, ?, ?, ?)",
                    (self.user['id'], 'pre', question, answer)
                )
            
            # Save post-survey responses
            for question, var in self.post_survey_responses.items():
                answer = var.get() if isinstance(var, tk.StringVar) else var.get()
                cursor.execute(
                    "INSERT INTO survey_responses (user_id, survey_type, question, answer) VALUES (?, ?, ?, ?)",
                    (self.user['id'], 'post', question, answer)
                )
            
            conn.commit()
            
            # Also save user progress data
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                points INTEGER,
                progress INTEGER,
                badges TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            cursor.execute(
                "INSERT INTO user_progress (user_id, points, progress, badges) VALUES (?, ?, ?, ?)",
                (self.user['id'], self.points, self.progress, ','.join(self.badges))
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving survey responses: {e}")


class DatabaseViewer:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Database Viewer")
        self.window.geometry("800x600")
        self.window.configure(bg=COLORS["background"])
        
        # Create scrollable main frame
        canvas, content_frame = create_scrollable_frame(self.window)
        self.content_frame = content_frame
        
        # Create title
        title_label = tk.Label(self.content_frame, text="AI Emotion Detector - Database Viewer", 
                            font=FONTS["title"], bg=COLORS["background"], fg=COLORS["primary"])
        title_label.pack(pady=10)
        
        # Create table selection frame
        selection_frame = tk.Frame(self.content_frame, bg=COLORS["background"])
        selection_frame.pack(fill="x", pady=10)
        
        # Create label
        table_label = tk.Label(selection_frame, text="Select Table:", font=FONTS["normal"], bg=COLORS["background"])
        table_label.pack(side="left", padx=5)
        
        # Create table selection dropdown
        self.table_var = tk.StringVar()
        tables = ["users", "sessions", "survey_responses", "user_progress"]
        table_dropdown = ttk.Combobox(selection_frame, textvariable=self.table_var, values=tables, font=FONTS["normal"], width=20)
        table_dropdown.pack(side="left", padx=5)
        table_dropdown.current(0)  # Default to users table
        
        # Create action buttons
        button_frame = tk.Frame(selection_frame, bg=COLORS["background"])
        button_frame.pack(side="left", padx=10)
        
        view_button = tk.Button(button_frame, text="View Table", font=FONTS["normal"], 
                              bg=COLORS["secondary"], fg="white", command=self.load_table_data)
        view_button.pack(side="left", padx=5)
        
        refresh_button = tk.Button(button_frame, text="Refresh Data", font=FONTS["normal"], 
                                 bg=COLORS["primary"], fg="white", command=self.load_table_data)
        refresh_button.pack(side="left", padx=5)
        
        export_button = tk.Button(button_frame, text="Export to CSV", font=FONTS["normal"], 
                                bg=COLORS["accent"], fg=COLORS["text"], command=self.export_to_csv)
        export_button.pack(side="left", padx=5)
        
        # Create treeview frame
        tree_frame = tk.Frame(self.content_frame, bg=COLORS["background"])
        tree_frame.pack(fill="both", expand=True, pady=10)
        
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame)
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Create treeview with nicer styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                     background="#ffffff",
                     foreground=COLORS["text"],
                     rowheight=25,
                     fieldbackground="#ffffff",
                     font=FONTS["small"])
        style.configure("Treeview.Heading", font=FONTS["normal"], background=COLORS["primary"], foreground="white")
        style.map('Treeview', background=[('selected', COLORS["accent"])])
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.tree.pack(fill="both", expand=True)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.content_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=FONTS["small"])
        status_bar.pack(side="bottom", fill="x")
        
        # Load initial data
        self.load_table_data()
    
    def load_table_data(self):
        """Load and display data from the selected table"""
        table_name = self.table_var.get()
        if not table_name:
            self.status_var.set("Please select a table")
            return
        
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Clear existing columns
            for col in self.tree["columns"]:
                self.tree.heading(col, text="")
            
            # Connect to database
            conn = sqlite3.connect('data/users.db')
            cursor = conn.cursor()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Configure tree columns
            self.tree["columns"] = columns
            self.tree["show"] = "headings"  # Hide the first empty column
            
            # Set column headings and widths
            for col in columns:
                self.tree.heading(col, text=col.capitalize())
                self.tree.column(col, width=150, anchor="center")
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Insert data into tree with alternating row colors
            for i, row in enumerate(rows):
                tag = "even" if i % 2 == 0 else "odd"
                self.tree.insert("", "end", values=row, tags=(tag,))
            
            # Configure row colors
            self.tree.tag_configure("even", background="#f0f0f0")
            self.tree.tag_configure("odd", background="#ffffff")
            
            conn.close()
            
            self.status_var.set(f"Loaded {len(rows)} records from {table_name}")
        except Exception as e:
            error_msg = f"Error loading data: {str(e)}"
            self.status_var.set(error_msg)
            messagebox.showerror("Database Error", error_msg)
    
    def export_to_csv(self):
        """Export current table view to CSV file"""
        table_name = self.table_var.get()
        if not table_name:
            self.status_var.set("Please select a table to export")
            return
        
        try:
            # Connect to database
            conn = sqlite3.connect('data/users.db')
            cursor = conn.cursor()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            conn.close()
            
            # Create export directory if it doesn't exist
            if not os.path.exists('exports'):
                os.makedirs('exports')
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"exports/{table_name}_{timestamp}.csv"
            
            # Write to CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columns)  # Write header
                writer.writerows(rows)    # Write data
            
            self.status_var.set(f"Exported to {filename}")
            messagebox.showinfo("Export Complete", f"Table exported to {filename}")
        except Exception as e:
            error_msg = f"Error exporting data: {str(e)}"
            self.status_var.set(error_msg)
            messagebox.showerror("Export Error", error_msg)


def main():
    root = tk.Tk()
    root.title("AI Emotion Detector Learning Tool")
    root.geometry("700x600")
    root.configure(bg=COLORS["background"])
    
    # Set application icon if available
    try:
        # If you have an icon file, you can set it here
        # root.iconbitmap("assets/icon.ico")
        pass
    except:
        pass
    
    # Create a menu bar with colorful styling
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    
    # Create File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Exit", command=root.quit)
    
    # Create Admin menu
    admin_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Admin", menu=admin_menu)
    
    # Add Database Viewer option
    admin_menu.add_command(label="Database Viewer", command=lambda: DatabaseViewer(root))
    
    # Add Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
        "About", "AI Emotion Detector Learning Tool\nA fun way for kids to learn about AI!"))
    
    # Define what happens after successful login
    def after_login(user):
        # Initialize the main app with the user data
        app = EmotionDetectorApp(root, user=user)
        app.show()
    
    # Create and show authentication system first
    auth_system = AuthenticationSystem(root, on_successful_login=after_login)
    auth_system.show_login()
    
    root.mainloop()

if __name__ == "__main__":
    main()