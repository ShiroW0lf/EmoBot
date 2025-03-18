import tkinter as tk
from tkinter import messagebox
from sklearn.neural_network import MLPRegressor
import numpy as np
from PIL import Image, ImageTk
import random
import matplotlib.pyplot as plt

# Real-Time AI Model for Plant Growth Learning
class PlantGrowthModel:
    def __init__(self):
        self.model = MLPRegressor(hidden_layer_sizes=(5,), max_iter=1000)
        self.training_data = []  # Store the history of inputs and outputs
        self._train_model()

    def _train_model(self):
        # Initial training data (water, sunlight) -> growth prediction (growth rate)
        X = np.array([[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]])
        y = np.array([1, 2, 3, 4, 5])  # Growth prediction
        self.model.fit(X, y)

    def predict_growth(self, water, sunlight):
        return self.model.predict([[water, sunlight]])

    def improve_model(self, water, sunlight, growth):
        # Continuously improve the model with new data from user input
        self.training_data.append([water, sunlight, growth])
        self.model.partial_fit([[water, sunlight]], [growth])

    def get_learning_curve(self):
        # Generate the learning curve (growth prediction vs. training data size)
        if len(self.training_data) < 2:
            return [], []
        X = np.array([data[:2] for data in self.training_data])
        y = np.array([data[2] for data in self.training_data])
        predictions = self.model.predict(X)
        return list(range(1, len(self.training_data) + 1)), predictions.tolist()

# Gardening Game with Real-Time Neural Network Learning
class GardenGame:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Gardening Game")
        self.root.geometry("800x600")
        self.root.config(bg="#d3f4f0")

        self.model = PlantGrowthModel()

        # Initial plant state
        self.water_level = 0
        self.sunlight_level = 0
        self.growth = 0

        # Canvas for UI elements
        self.canvas = tk.Canvas(self.root, width=800, height=500, bg="#d3f4f0")
        self.canvas.pack()

        # Background and plant images
        self.bg_image = ImageTk.PhotoImage(Image.open("garden_background.jpg").resize((800, 500)))
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

        self.plant_images = {
            "seed": ImageTk.PhotoImage(Image.open("seed.png").resize((100, 100))),
            "small_plant": ImageTk.PhotoImage(Image.open("small_plant.png").resize((100, 100))),
            "medium_plant": ImageTk.PhotoImage(Image.open("medium_plant.png").resize((100, 100))),
            "large_plant": ImageTk.PhotoImage(Image.open("large_plant.png").resize((100, 100))),
        }
        self.plant_image = self.canvas.create_image(400, 350, image=self.plant_images["seed"])

        # AI learning feedback text
        self.ai_feedback_label = tk.Label(self.root, text="AI is learning from your inputs!", font=("Arial", 14), bg="#d3f4f0")
        self.ai_feedback_label.pack(pady=10)

        # Sliders for water and sunlight
        self.water_slider_label = tk.Label(self.root, text="Water Level (0-5)", font=("Arial", 12), bg="#d3f4f0")
        self.water_slider_label.pack(pady=5)
        self.water_slider = tk.Scale(self.root, from_=0, to=5, orient=tk.HORIZONTAL, length=300)
        self.water_slider.pack(pady=5)

        self.sunlight_slider_label = tk.Label(self.root, text="Sunlight Level (0-5)", font=("Arial", 12), bg="#d3f4f0")
        self.sunlight_slider_label.pack(pady=5)
        self.sunlight_slider = tk.Scale(self.root, from_=0, to=5, orient=tk.HORIZONTAL, length=300)
        self.sunlight_slider.pack(pady=5)

        # Apply changes button
        self.apply_button = tk.Button(self.root, text="Apply Changes", command=self.apply_changes, bg="#8BC34A", fg="white", font=("Arial", 14))
        self.apply_button.pack(pady=20)

        # Growth status
        self.growth_label = tk.Label(self.root, text="Growth: 0", font=("Arial", 16), bg="#d3f4f0")
        self.growth_label.pack(pady=10)

        # AI learning progress
        self.learning_progress = tk.Label(self.root, text="AI Learning Progress: 0%", font=("Arial", 12), bg="#d3f4f0")
        self.learning_progress.pack(pady=5)

        # How AI Works button
        self.ai_explanation_button = tk.Button(self.root, text="How AI Works", command=self.explain_ai, bg="#FFC107", fg="black", font=("Arial", 14))
        self.ai_explanation_button.pack(pady=10)

        # Show Learning Curve button
        self.show_learning_curve_button = tk.Button(self.root, text="Show Learning Curve", command=self.show_learning_curve, bg="#4CAF50", fg="white", font=("Arial", 14))
        self.show_learning_curve_button.pack(pady=10)

        # Reset AI button
        self.reset_button = tk.Button(self.root, text="Reset AI", command=self.reset_ai, bg="#9E9E9E", fg="white", font=("Arial", 14))
        self.reset_button.pack(pady=10)

        # Finish the game button
        self.end_game_button = tk.Button(self.root, text="Finish the Game", command=self.end_game, bg="#F44336", fg="white", font=("Arial", 14))
        self.end_game_button.pack(pady=20)

    def apply_changes(self):
        # Get values from sliders
        self.water_level = self.water_slider.get()
        self.sunlight_level = self.sunlight_slider.get()

        # AI predicts growth and learns from it
        predicted_growth = self.model.predict_growth(self.water_level, self.sunlight_level)[0]
        self.growth = predicted_growth
        self.model.improve_model(self.water_level, self.sunlight_level, self.growth)

        # Update plant image and growth label
        self.update_growth()

        # Provide AI feedback
        self.ai_feedback_label.config(text=f"AI predicted and learned: {predicted_growth:.2f} growth.")
        self.update_learning_progress()

    def update_growth(self):
        # Visualize the plant based on growth
        if self.growth < 2:
            self.canvas.itemconfig(self.plant_image, image=self.plant_images["seed"])
        elif self.growth < 4:
            self.canvas.itemconfig(self.plant_image, image=self.plant_images["small_plant"])
        elif self.growth < 6:
            self.canvas.itemconfig(self.plant_image, image=self.plant_images["medium_plant"])
        else:
            self.canvas.itemconfig(self.plant_image, image=self.plant_images["large_plant"])

        # Update growth label
        self.growth_label.config(text=f"Growth: {self.growth:.2f}")

    def update_learning_progress(self):
        progress = min(len(self.model.training_data) / 10 * 100, 100)  # Progress based on data points
        self.learning_progress.config(text=f"AI Learning Progress: {progress:.0f}%")

    def explain_ai(self):
        explanation = (
            "AI is like a brain that learns from your choices!\n\n"
            "When you adjust water and sunlight, the AI predicts how much the plant will grow.\n"
            "Over time, it gets better at predicting by learning from your inputs.\n\n"
            "This is called 'machine learning'!"
        )
        messagebox.showinfo("How AI Works", explanation)

    def show_learning_curve(self):
        # Generate and show learning curve for AI improvement
        x, y = self.model.get_learning_curve()
        if x:
            plt.plot(x, y, label="AI Learning Progress")
            plt.xlabel("Training Data Points")
            plt.ylabel("Predicted Growth")
            plt.title("AI Learning Curve")
            plt.legend()
            plt.show()
        else:
            messagebox.showinfo("No Data", "There is not enough data to show the learning curve.")

    def reset_ai(self):
        self.model = PlantGrowthModel()
        self.growth = 0
        self.update_growth()
        self.ai_feedback_label.config(text="AI has been reset! Start teaching it again.")
        self.learning_progress.config(text="AI Learning Progress: 0%")

    def end_game(self):
        # Post-survey question on AI
        response = messagebox.askquestion("Post-Survey", "Do you think AI can help plants grow better?")
        print(f"Post-survey answer: {response}")

        # Show a summary of what the AI learned
        summary = (
            "Great job! Here's what the AI learned:\n\n"
            f"- You provided {len(self.model.training_data)} data points.\n"
            f"- The AI's final growth prediction was {self.growth:.2f}.\n\n"
            "Fun Fact: AI is used in real life to help farmers grow crops more efficiently!"
        )
        messagebox.showinfo("Game Summary", summary)

        self.root.quit()

# Start the game
def start_game():
    root = tk.Tk()
    game = GardenGame(root)
    root.mainloop()

if __name__ == "__main__":
    start_game()