import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
from typing import Dict, List, Optional
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import io
import threading
import webbrowser
from urllib.request import urlopen

class ModernRecipeFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Recipe Finder 🍳")
        self.root.geometry("1000x800")
        
        # API credentials
        self.app_id = "a48acaa6"
        self.app_key = "c07eaa0f26a60eb33c1b5c747ccb1785"
        
        # Style configuration
        self.style = ttk.Style("darkly")
        
        self.create_widgets()
        self.current_recipes = []
        
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=BOTH, expand=YES)
        
        # Search section
        search_frame = ttk.LabelFrame(main_container, text="Search Recipes", padding="10")
        search_frame.pack(fill=X, pady=(0, 10))
        
        # Ingredients entry
        ttk.Label(search_frame, text="Ingredients:").pack(anchor=W)
        self.ingredients_entry = ttk.Entry(search_frame)
        self.ingredients_entry.pack(fill=X, pady=(0, 10))
        
        # Filters frame
        filters_frame = ttk.Frame(search_frame)
        filters_frame.pack(fill=X)
        
        # Calories filter
        calories_frame = ttk.Frame(filters_frame)
        calories_frame.pack(side=LEFT, padx=(0, 10))
        ttk.Label(calories_frame, text="Max Calories:").pack(side=LEFT)
        self.calories_entry = ttk.Entry(calories_frame, width=10)
        self.calories_entry.pack(side=LEFT, padx=(5, 0))
        
        # Diet preference filter
        diet_frame = ttk.Frame(filters_frame)
        diet_frame.pack(side=LEFT)
        ttk.Label(diet_frame, text="Diet:").pack(side=LEFT)
        self.diet_var = tk.StringVar()
        diet_options = ['', 'balanced', 'high-protein', 'low-fat', 'low-carb']
        self.diet_combobox = ttk.Combobox(diet_frame, textvariable=self.diet_var, values=diet_options, width=15)
        self.diet_combobox.pack(side=LEFT, padx=(5, 0))
        
        # Search button
        self.search_button = ttk.Button(
            search_frame, 
            text="Search", 
            command=self.search_recipes,
            style="primary.TButton"
        )
        self.search_button.pack(pady=(10, 0))
        
        # Create paned window for results and details
        self.paned_window = ttk.PanedWindow(main_container, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=YES)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.paned_window, text="Results", padding="10")
        self.paned_window.add(results_frame, weight=1)
        
        # Results treeview
        self.results_tree = ttk.Treeview(
            results_frame, 
            columns=("name", "calories"),
            show="headings",
            selectmode="browse"
        )
        self.results_tree.heading("name", text="Recipe Name")
        self.results_tree.heading("calories", text="Calories")
        self.results_tree.column("name", width=200)
        self.results_tree.column("calories", width=100)
        self.results_tree.pack(fill=BOTH, expand=YES)
        self.results_tree.bind('<<TreeviewSelect>>', self.show_recipe_details)
        
        # Details frame
        details_frame = ttk.LabelFrame(self.paned_window, text="Recipe Details", padding="10")
        self.paned_window.add(details_frame, weight=2)
        
        # Details text
        self.details_text = scrolledtext.ScrolledText(
            details_frame, 
            wrap=tk.WORD, 
            width=50, 
            height=20
        )
        self.details_text.pack(fill=BOTH, expand=YES)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            main_container, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=X, pady=(10, 0))
        
    def search_recipes(self):
        """Perform recipe search"""
        self.search_button.config(state="disabled")
        self.status_var.set("Searching...")
        self.results_tree.delete(*self.results_tree.get_children())
        self.details_text.delete(1.0, tk.END)
        
        # Start search in a separate thread
        thread = threading.Thread(target=self._perform_search)
        thread.daemon = True
        thread.start()
        
    def _perform_search(self):
        """Perform the actual API search"""
        try:
            ingredients = self.ingredients_entry.get()
            url = "https://api.edamam.com/search"
            
            params = {
                'q': ingredients,
                'app_id': self.app_id,
                'app_key': self.app_key,
                'from': 0,
                'to': 20
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            self.current_recipes = data.get('hits', [])
            self._filter_and_display_results()
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.search_button.config(state="normal"))
            
    def _filter_and_display_results(self):
        """Filter and display the search results"""
        filtered_recipes = self.current_recipes.copy()
        
        # Apply calories filter
        max_calories = self.calories_entry.get()
        if max_calories:
            try:
                max_cal = float(max_calories)
                filtered_recipes = [
                    recipe for recipe in filtered_recipes
                    if recipe["recipe"]["calories"] / recipe["recipe"]["yield"] <= max_cal
                ]
            except ValueError:
                pass
                
        # Apply diet filter
        diet_preference = self.diet_var.get()
        if diet_preference:
            filtered_recipes = [
                recipe for recipe in filtered_recipes
                if diet_preference.lower() in [label.lower() for label in recipe["recipe"].get("dietLabels", [])]
            ]
            
        # Update treeview
        self.root.after(0, lambda: self._update_treeview(filtered_recipes))
        
    def _update_treeview(self, recipes):
        """Update the treeview with filtered recipes"""
        self.results_tree.delete(*self.results_tree.get_children())
        
        for i, recipe in enumerate(recipes):
            recipe_info = recipe["recipe"]
            calories_per_serving = recipe_info["calories"] / recipe_info["yield"]
            
            self.results_tree.insert(
                "",
                tk.END,
                values=(recipe_info["label"], f"{calories_per_serving:.1f}"),
                iid=str(i)
            )
            
        self.status_var.set(f"Found {len(recipes)} recipes")
        
    def show_recipe_details(self, event):
        """Display detailed information about the selected recipe"""
        selection = self.results_tree.selection()
        if not selection:
            return
            
        recipe_idx = int(selection[0])
        recipe_info = self.current_recipes[recipe_idx]["recipe"]
        
        # Clear previous details
        self.details_text.delete(1.0, tk.END)
        
        # Format and display recipe details
        details = f"""📗 {recipe_info['label']}\n
🔗 Source: {recipe_info['source']}
👥 Serves: {recipe_info['yield']} people
🔥 Calories per serving: {recipe_info['calories'] / recipe_info['yield']:.1f}

Diet Labels: {', '.join(recipe_info.get('dietLabels', ['None']))}
Health Labels: {', '.join(recipe_info.get('healthLabels', ['None']))}

📝 Ingredients:
"""
        for i, ingredient in enumerate(recipe_info['ingredientLines'], 1):
            details += f"{i}. {ingredient}\n"
            
        details += "\n📊 Key Nutrients (per serving):\n"
        if 'totalNutrients' in recipe_info:
            nutrients = recipe_info['totalNutrients']
            servings = recipe_info['yield']
            key_nutrients = ['PROCNT', 'FAT', 'CHOCDF', 'FIBTG']
            
            for nutrient_id in key_nutrients:
                if nutrient_id in nutrients:
                    nutrient = nutrients[nutrient_id]
                    amount = nutrient['quantity'] / servings
                    unit = nutrient['unit']
                    details += f"• {nutrient['label']}: {amount:.1f}{unit}\n"
                    
        details += f"\n🌐 Recipe URL: {recipe_info['url']}"
        
        self.details_text.insert(1.0, details)
        
def main():
    root = ttk.Window()
    app = ModernRecipeFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()
