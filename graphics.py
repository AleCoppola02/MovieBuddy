import tkinter as tk
from tkinter import messagebox, ttk
import datareader as dr
from datareader import getMovieParameterList, extractRating, extractList

root = None

class RangeSlider(tk.Canvas):
    def __init__(self, master, min_val, max_val, init_vals, width=300, height=60,
                 value_callback=None, **kwargs):
        """Create a dual-handle range slider widget.

        Args:
            master: Parent tkinter widget.
            min_val: Minimum selectable value.
            max_val: Maximum selectable value.
            init_vals: Tuple (start, end) initial values.
            width, height: Canvas size.
            value_callback: Optional callable called with (val1, val2) when handles move.
        """
        super().__init__(master, width=width, height=height, bg="white", **kwargs)

        self.min_val = min_val
        self.max_val = max_val
        self.width = width
        self.height = height

        self.value_callback = value_callback   # NEW

        # Values
        self.val1 = init_vals[0]
        self.val2 = init_vals[1]

        # Drawing parameters
        self.pad = 15
        self.handle_radius = 8

        # Track
        self.track = self.create_line(
            self.pad, height // 2, width - self.pad, height // 2,
            fill="#888", width=4
        )

        # Handles
        self.handle1 = self.create_oval(0, 0, 0, 0, fill="#0078D7")
        self.handle2 = self.create_oval(0, 0, 0, 0, fill="#0078D7")

        self.active = None
        self.update_positions()

        # Events
        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)

    def value_to_x(self, value):
        """Convert a numeric value into an x coordinate on the canvas."""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.pad + ratio * (self.width - 2 * self.pad)

    def x_to_value(self, x):
        """Convert an x coordinate back into a numeric value (clamped)."""
        ratio = (x - self.pad) / (self.width - 2 * self.pad)
        ratio = max(0, min(1, ratio))
        return int(self.min_val + ratio * (self.max_val - self.min_val))

    def update_positions(self):
        """Update handle positions on the canvas and call callback if present."""
        y = self.height // 2
        x1 = self.value_to_x(self.val1)
        x2 = self.value_to_x(self.val2)
        r = self.handle_radius

        self.coords(self.handle1, x1 - r, y - r, x1 + r, y + r)
        self.coords(self.handle2, x2 - r, y - r, x2 + r, y + r)

        # NEW: update callback
        if self.value_callback:
            self.value_callback(self.val1, self.val2)

    def click(self, event):
        """Handle mouse-down events to activate the nearest handle."""
        if self.is_on_handle(event.x, event.y, self.handle1):
            self.active = "left"
        elif self.is_on_handle(event.x, event.y, self.handle2):
            self.active = "right"

    def drag(self, event):
        """Handle mouse-drag events to move the active handle and update values."""
        if not self.active:
            return

        x = min(max(event.x, self.pad), self.width - self.pad)
        val = self.x_to_value(x)

        if self.active == "left":
            self.val1 = min(val, self.val2)
        else:
            self.val2 = max(val, self.val1)

        self.update_positions()

    def is_on_handle(self, x, y, handle):
        """Return True if the (x,y) point lies within the given handle's bounding box."""
        x1, y1, x2, y2 = self.coords(handle)
        return x1 <= x <= x2 and y1 <= y <= y2

    def get_values(self):
        """Return the current (start, end) values for the slider."""
        return self.val1, self.val2



def promptGeneticInputs():
    """Show a dialog to collect high-level genetic-algorithm preferences.

    Presents genre checkboxes, a length slider and a year-range selector.

    Returns:
        A dict suitable for the GA evaluator, or None if the user closed the window.
    """
    root = getRoot()
    root.title("Movie Preference Input")
    root.geometry("800x600")

    # --- HANDLE WINDOW CLOSE ---
    def on_close():
        root.userInput = None
        root.destroy()

    # ---- FIXED WINDOW SIZE ----


    root.protocol("WM_DELETE_WINDOW", on_close)

    genres_available = [
        "Action", "Adventure", "Animation", "Comedy", "Crime", "Drama",
        "Fantasy", "Historical", "Horror", "Mystery", "Romance", "Sci-Fi",
        "Sport", "Thriller", "War", "Western"
    ]

    # ------------------------
    # GENRES (CHECKBOXES)
    # ------------------------
    tk.Label(root, text="Select Genres:", font=("Arial", 13, "bold")).pack(pady=10)
    genre_vars = {}
    frame = tk.Frame(root)
    frame.pack()

    for i, g in enumerate(genres_available):
        var = tk.BooleanVar()
        tk.Checkbutton(frame, text=g, variable=var).grid(row=i//2, column=i%2, sticky="w")
        genre_vars[g] = var

    # ------------------------
    # LENGTH SLIDER
    # ------------------------
    tk.Label(root, text="Movie Length (40–240):", font=("Arial", 13, "bold")).pack(pady=15)
    length_var = tk.IntVar(value=90)
    tk.Scale(root, from_=40, to=240, resolution=5,
             orient=tk.HORIZONTAL, length=350,
             variable=length_var).pack()

    # ------------------------
    # YEAR RANGE (DUAL SLIDER)
    # ------------------------
    tk.Label(root, text="Publication Period:", font=("Arial", 13, "bold")).pack(pady=20)

    # --- NEW: live year label ---
    year_label = tk.Label(root, text="2000 - 2020", font=("Arial", 12))
    year_label.pack()

    # Callback updates the label
    def update_year_label(val1, val2):
        year_label.config(text=f"{val1} - {val2}")

    range_slider = RangeSlider(
        root, min_val=1920, max_val=2025,
        init_vals=(2000, 2025),
        value_callback=update_year_label  # NEW
    )
    range_slider.pack(pady=10)
    # ------------------------
    # SUBMIT BUTTON
    # ------------------------
    def submit():
        genres = [g for g, v in genre_vars.items() if v.get()]
        if not genres:
            messagebox.showerror("Error", "Select at least one genre.")
            return

        start, end = range_slider.get_values()

        userInput = {
            "Periodo": range(start, end + 1),
            "Lunghezza": length_var.get(),
            "Generi": genres
        }

        root.userInput = userInput
        root.destroy()

    tk.Button(root, text="Submit", font=("Arial", 13),
              command=submit).pack(pady=25)

    root.mainloop()
    return getattr(root, "userInput", None)


import tkinter as tk
import random
from functools import partial



class MovieRaterGUI:
    def __init__(self, root, firstPhaseResult):
        """GUI for letting the user rate a small set of candidate movies.

        The GUI shows up to five candidate movies (from `firstPhaseResult`)
        and collects 'like'/'dislike' choices to be used in the second phase.

        Args:
            root: Tk root window.
            firstPhaseResult: Iterable of movie indices to sample from.
        """
        self.root = root
        self.root.title("Movie Rater")

        # ---- FIXED WINDOW SIZE ----
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.root.choices = None  # where results will be returned

        # Select five random distinct indexes
        self.selected_indexes = random.sample(firstPhaseResult, 5)
        self.current = 0

        # ---- CHOICES STRUCTURE ----
        self.choices = {
            "like": [],
            "dislike": []
        }

        # ----- TITLE -----
        self.title_label = tk.Label(
            root, text="",
            font=("Arial", 18, "bold"),
            wraplength=650,
            justify="center"
        )
        self.title_label.pack(pady=15)

        # ----- MOVIE INFO -----
        self.info_frame = tk.Frame(root, width=650, height=460)
        self.info_frame.pack()
        self.info_frame.pack_propagate(False)

        self.info_label = tk.Label(
            self.info_frame,
            text="",
            wraplength=600,
            justify="center",
            font=("Arial", 12)
        )
        self.info_label.pack(expand=True)

        # ----- BUTTONS -----
        button_frame = tk.Frame(root)
        button_frame.pack(pady=15)

        self.like_button = tk.Button(
            button_frame, text="I like it", width=12,
            command=partial(self.rate_movie, "like")
        )
        self.like_button.grid(row=0, column=0, padx=10)

        self.dislike_button = tk.Button(
            button_frame, text="I don't like it", width=12,
            command=partial(self.rate_movie, "dislike")
        )
        self.dislike_button.grid(row=0, column=1, padx=10)

        self.next_button = tk.Button(
            button_frame, text="Next", width=12,
            command=self.next_movie
        )
        self.next_button.grid(row=0, column=2, padx=10)

        self.show_movie()

    # -------- FORMAT MOVIE DETAILS --------
    def format_movie_info(self, info):
        """Format a movie info tuple into a readable multi-line string.

        Args:
            info: Tuple containing (title, duration, rating, description, directors, release_date, genres).

        Returns:
            A string describing the movie suitable for display.
        """
        title, duration, rating, description, directors, release_date, genres = info
        if(duration == None):
            duration = '?'
        rating = extractRating(rating)
        if(rating == 0):
            rating = '?'
        if(not release_date or not release_date.strip()):
            release_date = '?'
        if(not directors):
            director = '?'
        if(not genres):
            genres = '?'
        if (not description):
            description = '?'
        return (f"Duration: {duration}\n"
                f"Rating: {rating}\n"
                f"Description: {description}\n"
                f"Directors: {directors}\n"
                f"Release Date: {release_date}\n"
                f"Genres: {genres}")

    # -------- SHOW MOVIE --------
    def show_movie(self):
        """Display the current movie in the rating sequence, or finish if done."""
        if self.current < len(self.selected_indexes):
            idx = self.selected_indexes[self.current]
            info = getMovieParameterList(idx, [
                "title", "duration", "rating", "description",
                "directors", "release_date", "genres"
            ])

            self.title_label.config(text=info[0])
            self.info_label.config(text=self.format_movie_info(info))
        else:
            self.finish_and_close()

    # -------- RATE MOVIE --------
    def rate_movie(self, rating):
        """Record a 'like' or 'dislike' for the current movie and advance."""
        idx = self.selected_indexes[self.current]
        self.choices[rating].append(idx)
        self.current += 1
        self.show_movie()

    # -------- SKIP MOVIE --------
    def next_movie(self):
        """Skip the current movie without recording a preference and advance."""
        self.current += 1
        self.show_movie()

    # -------- CLOSE AND RETURN DATA --------
    def finish_and_close(self):
        """Store collected choices on the root and close the window."""
        self.root.choices = self.choices
        self.root.destroy()

    def get_choices(self):
        """Return the collected like/dislike choices as a dict."""
        return self.choices


def getRoot():
    """Return a shared Tk root, creating one if necessary."""
    if root == None:
        return tk.Tk()
    else:
        return root

def promptUserPreference(firstPhaseResult):
    """Display the movie rater GUI and return user's ratings.

    Args:
        firstPhaseResult: Iterable of candidate movie indices to present.

    Returns:
        A dict with keys 'like' and 'dislike' mapping to lists of indices.
    """
    root = getRoot()
    app = MovieRaterGUI(root, firstPhaseResult)
    root.mainloop()
    results = app.get_choices()
    return results

# Add this to graphics.py
class SimpleLoadingScreen:
    def __init__(self):
        """A minimal loading window with an indeterminate progress bar."""
        self.root = tk.Tk()
        self.root.title("Processing")
        self.root.geometry("300x120")
        
        tk.Label(self.root, text="Calculating recommendations...", font=("Arial", 10)).pack(pady=10)
        
        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=200)
        self.progress.pack(pady=10)
        self.progress.start(10)
        
    def close(self):
        """Close the loading window and stop its UI loop."""
        self.root.destroy()
        
    def update(self):
        """Pump the loading window's event loop once (non-blocking)."""
        self.root.update()

        import tkinter as tk
from tkinter import ttk
from datareader import getMovieParameterList, extractRating

class MovieExplanationGUI:
    def __init__(self, movie: int, preferences: dict):
        """Show an explanation window describing why a movie was recommended.

        Args:
            movie: Movie index.
            preferences: User preferences used to build the explanation.
        """
        self.root = tk.Tk()
        self.root.title("Why this movie?")
        self.root.geometry("700x600")
        self.root.resizable(False, False)

        info = getMovieParameterList(
            movie,
            ["title", "release_date", "duration", "rating",
             "description", "genres", "directors", "stars", "keywords"]
        )

        (
            title, release_date, duration, rating,
            description, genres, directors, stars, keywords
        ) = info

        rating = extractRating(rating)
        genres =extractList(genres)
        directors =extractList(directors)
        stars =extractList(stars)
        keywords =extractList(keywords)
        print(title)
        print(keywords)
        print(stars)
        print(directors)
        print(preferences)
        # -------- TITLE --------
        tk.Label(
            self.root, text=title,
            font=("Arial", 18, "bold"),
            wraplength=650,
            justify="center"
        ).pack(pady=15)

        # -------- MOVIE INFO --------
        info_text = (
            f"Release date: {release_date or '?'}\n"
            f"Duration: {duration or '?'}\n"
            f"Rating: {rating or '?'}\n\n"
            f"{description or 'No description available.'}\n\n"
            f"Genres: {genres or '?'}"
        )

        tk.Label(
            self.root,
            text=info_text,
            wraplength=650,
            justify="center",
            font=("Arial", 12)
        ).pack(pady=10)

        # -------- EXPLANATION --------
        explanation = self.build_explanation(
            directors, stars, keywords, preferences
        )

        ttk.Separator(self.root).pack(fill="x", pady=10)

        tk.Label(
            self.root,
            text="Why this movie was recommended:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        tk.Label(
            self.root,
            text=explanation,
            wraplength=650,
            justify="center",
            font=("Arial", 12),
            fg="#333"
        ).pack(pady=10)

        # -------- CLOSE --------
        tk.Button(
            self.root, text="Close",
            command=self.root.destroy,
            width=12
        ).pack(pady=15)

        self.root.mainloop()

    def build_explanation(self, directors, stars, keywords, preferences):
        """Generate a short textual explanation based on matched attributes.

        Looks for matches in directors, actors (stars) and keywords using
        the provided `preferences` dictionary and returns a human-readable
        explanation string.
        """
        lines = []

        def match(values, pref_key):
            if not values:
                return []
            if isinstance(values, str):
                values = [v.strip() for v in values.split(",")]
            return [v for v in values if v in preferences.get(pref_key, [])]

        # ---- Directors ----
        matched_directors = match(directors, "directors+")
        if matched_directors:
            names = ", ".join(matched_directors)
            lines.append(f"Because you liked movies by {names}")

        # ---- Actors ----
       # matched_actors = match(stars, "actors+")
      #  if matched_actors:
      #      names = ", ".join(matched_actors)
      #      lines.append(f"Because you liked movies starring {names}")

        # ---- Keywords ----
        matched_keywords = match(keywords, "keywords+")
        if matched_keywords:
            tags = ", ".join(f"'{k}'" for k in matched_keywords)
            lines.append(f"Because you liked movies tagged {tags}")

        if not lines:
            return "This movie matches your general preferences."

        return "\n".join(lines)