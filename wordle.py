import random
from collections import Counter, defaultdict
import tkinter as tk
from tkinter import messagebox, simpledialog
import math

# --- Configuration ---
WORD_LENGTH = 5
MAX_ATTEMPTS = 6
# Recommended: Download a comprehensive list of 5-letter words.
# e.g., from https://raw.githubusercontent.com/tabatkins/wordle-list/main/words
# or https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt (filter for 5-letter words)
# Save it as "wordle_words.txt" in the same directory as this script.
WORD_LIST_FILENAME = "wordle_words.txt" 
EXAMPLE_WORD_LIST = [
    "cigar", "rebut", "sissy", "humph", "awake", "blush", "focal", "evade", 
    "naval", "serve", "heath", "dwarf", "model", "karma", "stink", "grade", 
    "quiet", "bench", "abate", "feign", "major", "death", "fresh", "crust", 
    "stool", "colon", "abase", "marry", "react", "batty", "pride", "floss", 
    "helix", "croak", "staff", "paper", "unfed", "whelp", "trawl", "outdo", 
    "adobe", "crazy", "sower", "repay", "digit", "crate", "cluck", "spike", 
    "mimic", "pound", "maxim", "linen", "unmet", "flesh", "booby", "forth", 
    "first", "stand", "belly", "ivory", "seedy", "print", "yearn", "drain", 
    "bribe", "stout", "panel", "crass", "flume", "offal", "agree", "error", 
    "swirl", "argue", "bleed", "delta", "flick", "totem", "wooer", "front", 
    "shrub", "parry", "biome", "lapel", "start", "greet", "goner", "golem", 
    "lusty", "loopy", "round", "audit", "lying", "gamma", "labor", "islet", 
    "civic", "forge", "corny", "moult", "basic", "salad", "agate", "spicy", 
    "spray", "essay", "fjord", "spend", "kebab", "guild", "aback", "motor", 
    "alone", "hatch", "hyper", "thumb", "dowry", "ought", "belch", "dutch", 
    "pilot", "tweed", "comet", "jaunt", "enema", "steed", "abyss", "growl", 
    "fling", "dozen", "boozy", "erode", "world", "gouge", "click", "briar", 
    "great", "altar", "pulpy", "blurt", "coast", "duchy", "groin", "fixer", 
    "group", "rogue", "badly", "smart", "pithy", "gaudy", "chill", "heron", 
    "vodka", "finer", "surer", "radio", "rouge", "perch", "retch", "wrote", 
    "clock", "tilde", "store", "prove", "bring", "solve", "cheat", "grime", 
    "exult", "usher", "epoch", "triad", "break", "rhino", "viral", "conic", 
    "masse", "sonic", "vital", "trace", "using", "peach", "champ", "baton", 
    "brake", "pluck", "craze", "gripe", "weary", "picky", "acute", "ferry", 
    "aside", "tapir", "troll", "unify", "rebus", "boost", "truss", "siege", 
    "tiger", "banal", "slump", "crank", "gorge", "query", "drink", "favor", 
    "abbey", "tangy", "panic", "solar", "shire", "proxy", "point", "robot", 
    "prick", "wince", "crimp", "knoll", "sugar", "whack", "mount", "perky", 
    "could", "wrung", "light", "those", "moist", "shard", "pleat", "aloft", 
    "skill", "elder", "frame", "humor", "pause", "ulcer", "ultra", "robin", 
    "cynic", "agora", "aroma", "caulk", "shake", "pupal", "dodge", "swill", 
    "tacit", "other", "thorn", "trove", "bloke", "vivid", "spill", "chant", 
    "choke", "ruder", "movie", "swear", "panic", "study", "crane", "slate"
] # A small list for example if file not found

# --- Core Logic ---

def calculate_feedback_pattern(guess, actual_word):
    """
    Calculates the feedback pattern that would be given for a guess against an actual word.
    This must accurately mimic Wordle's feedback rules, especially for duplicate letters.
    
    Returns a string of 5 characters:
    'g' = green (correct letter, correct position)
    'y' = yellow (correct letter, wrong position)  
    'b' = black/grey (letter not in word or all instances accounted for)
    
    Examples:
    calculate_feedback_pattern("CRANE", "APART") -> "gbbbb" (C correct, others not in word)
    calculate_feedback_pattern("SPEED", "ERASE") -> "bbybb" (P->E yellow, E->E yellow, others not in word)
    calculate_feedback_pattern("BOOKS", "FLOOD") -> "bbyyb" (O at pos 1 yellow, O at pos 2 yellow)
    """
    if len(guess) != len(actual_word):
        raise ValueError("Guess and actual word must be same length")
    
    feedback = ['b'] * len(guess)  # Start with all black/grey
    actual_counts = Counter(actual_word)
    
    # Green pass: Mark exact position matches first
    for i in range(len(guess)):
        if guess[i] == actual_word[i]:
            feedback[i] = 'g'
            actual_counts[guess[i]] -= 1  # Remove this letter from available count
    
    # Yellow pass: Check remaining letters for presence in wrong positions
    for i in range(len(guess)):
        if feedback[i] != 'g':  # Only consider non-green letters
            if guess[i] in actual_word and actual_counts.get(guess[i], 0) > 0:
                feedback[i] = 'y'
                actual_counts[guess[i]] -= 1  # Remove this letter from available count
    
    return "".join(feedback)

def filter_words(word_pool, all_guesses_feedback):
    """
    Filters the word list based on accumulated feedback.
    all_guesses_feedback: list of {'guess': str, 'feedback': list_of_feedback_items}
    feedback_item: {'char': str, 'color': str ('g'/'y'/'b'), 'position': int}
    """
    if not all_guesses_feedback:
        return word_pool

    # Aggregate constraints
    green_chars = {}  # {position: char}
    yellow_char_info = {} # {char: {present_min_count: int, forbidden_positions: set()}}
    # For grey letters, we determine max counts. If a letter is purely grey, its max count is 0.
    # If grey appears with green/yellow for same char in a guess (e.g. guess BOOKS, target GHOSTS -> B(grey) O(yellow) O(grey) K(grey) S(green))
    # this means the count of 'O' is exactly 1.
    letter_max_counts = {} # {char: max_allowed_count}
    
    # Min counts are derived from the sum of green and yellow for a char in any single guess
    letter_min_counts = Counter() 

    for guess_info in all_guesses_feedback:
        guess = guess_info['guess']
        feedback = guess_info['feedback']
        
        current_guess_char_colors = {} # Store colors for each char instance in this guess
        for i, fb_item in enumerate(feedback):
            current_guess_char_colors[(fb_item['char'], i)] = fb_item['color']

        # Process greens first to establish known letters/positions
        for fb_item in feedback:
            char, color, pos = fb_item['char'], fb_item['color'], fb_item['position']
            if color == 'g':
                green_chars[pos] = char
        
        # Process yellows and greys to refine counts and positions
        # Count green and yellow instances for each char *in the current guess*
        guess_green_counts = Counter()
        guess_yellow_counts = Counter()
        for fb_item in feedback:
            if fb_item['color'] == 'g':
                guess_green_counts[fb_item['char']] += 1
            elif fb_item['color'] == 'y':
                guess_yellow_counts[fb_item['char']] += 1
        
        for char_code in set(guess): # Iterate over unique chars in the guess
            # Min count for this char based on this guess
            current_min_for_char = guess_green_counts[char_code] + guess_yellow_counts[char_code]
            letter_min_counts[char_code] = max(letter_min_counts[char_code], current_min_for_char)

            # Max count (due to grey letters)
            # If any instance of char_code in the guess is grey, it implies a max count
            num_grey_instances_of_char = sum(1 for fb_item in feedback if fb_item['char'] == char_code and fb_item['color'] == 'b')
            
            if num_grey_instances_of_char > 0:
                # If a char has grey feedback, its total count in the target is exactly its green+yellow count in this guess
                max_count_for_char_this_guess = guess_green_counts[char_code] + guess_yellow_counts[char_code]
                if char_code in letter_max_counts:
                    letter_max_counts[char_code] = min(letter_max_counts[char_code], max_count_for_char_this_guess)
                else:
                    letter_max_counts[char_code] = max_count_for_char_this_guess
        
        # Update yellow_char_info (forbidden positions)
        for fb_item in feedback:
            char, color, pos = fb_item['char'], fb_item['color'], fb_item['position']
            if color == 'y':
                if char not in yellow_char_info:
                    yellow_char_info[char] = {'present_min_count': 0, 'forbidden_positions': set()} # min_count updated by letter_min_counts
                yellow_char_info[char]['forbidden_positions'].add(pos)

    # Now, filter the word_pool
    next_possible_words = []
    for word in word_pool:
        possible = True
        word_counter = Counter(word)

        # 1. Green letter check
        for pos, char_val in green_chars.items():
            if word[pos] != char_val:
                possible = False
                break
        if not possible: continue

        # 2. Yellow letter check (presence and forbidden positions)
        for char_val, info in yellow_char_info.items():
            if char_val not in word_counter or word_counter[char_val] == 0: # Must contain the char
                possible = False
                break
            for forbidden_pos in info['forbidden_positions']:
                if word[forbidden_pos] == char_val: # Must not be at these positions
                    possible = False
                    break
            if not possible: break
        if not possible: continue
        
        # 3. Letter count checks (min and max)
        # Min counts (must have at least this many)
        for char_val, min_count in letter_min_counts.items():
            if word_counter[char_val] < min_count:
                possible = False
                break
        if not possible: continue

        # Max counts (cannot have more than this many)
        # This also handles purely grey letters (max_count = 0 if never green/yellow in a guess)
        for char_val, max_count in letter_max_counts.items():
            if word_counter[char_val] > max_count:
                possible = False
                break
        if not possible: continue
        
        # An additional check for purely grey letters not covered by letter_max_counts
        # (i.e., a letter was grey, and never green/yellow in *any* guess)
        # This should be covered if letter_max_counts[char_val] = 0 was set correctly.
        # Let's ensure: if a char was grey AND has no min_count > 0 AND not in green_chars values, it shouldn't be in word.
        for char_val_in_word in word_counter:
            if char_val_in_word not in letter_min_counts and char_val_in_word not in green_chars.values():
                # This char was never green or yellow. If it appeared as grey, it should have max_count = 0.
                if char_val_in_word in letter_max_counts and letter_max_counts[char_val_in_word] == 0:
                    pass # Correctly handled
                elif char_val_in_word in letter_max_counts and letter_max_counts[char_val_in_word] > 0:
                    # This case should not happen if logic is right; means it was grey but also allowed.
                    pass
                elif char_val_in_word not in letter_max_counts:
                    # This char was never green, yellow, or explicitly grey-constrained.
                    # If it was *ever* purely grey in a guess, it should be out.
                    # This check is tricky to add here without iterating all feedback again.
                    # The current letter_max_counts should handle it if a char is truly "eliminated".
                    pass


        if possible:
            next_possible_words.append(word)
            
    return next_possible_words


def choose_next_guess_advanced(possible_words, all_words, strategy="entropy", is_first_guess=False, top_n=5):
    """
    Advanced guess selection using Minimax or Entropy strategies.
    
    Args:
        possible_words: List of words that could still be the answer
        all_words: Full word list to consider as potential guesses
        strategy: "minimax" or "entropy"
        is_first_guess: Whether this is the first guess
        top_n: Number of top suggestions to return
    
    Returns:
        List of tuples: [(word, score), ...] ranked from best to worst
    """
    if is_first_guess:
        # For first guess, use pre-computed optimal words to avoid expensive calculation
        starters = ["soare", "crane", "slate", "raise", "adieu", "audio", "least", "trace"]
        valid_starters = [s for s in starters if len(s) == WORD_LENGTH and s in all_words]
        if valid_starters:
            return [(word, 1.0) for word in valid_starters[:top_n]]  # Return top starters with dummy scores
        fallback = [random.choice(all_words)] if all_words else []
        return [(word, 1.0) for word in fallback]

    if not possible_words:
        return []
    if len(possible_words) == 1:
        return [(possible_words[0], 1.0)]

    candidate_scores = []  # List of (word, score) tuples
    
    # Determine candidate guesses - balance between thoroughness and performance
    if len(possible_words) < 20:
        # If few possibilities remain, prioritize guessing potential answers
        candidate_pool = possible_words + [w for w in all_words[:1000] if w not in possible_words]  # Add some extra options
    else:
        # With many possibilities, focus on information-gathering words
        candidate_pool = all_words[:2000]  # Limit to first 2000 for performance
    
    print(f"Evaluating {len(candidate_pool)} candidate guesses against {len(possible_words)} possible words...")

    for i, candidate_guess in enumerate(candidate_pool):
        if len(candidate_guess) != WORD_LENGTH:
            continue
            
        # Show progress for long calculations
        if i % 500 == 0 and i > 0:
            print(f"Progress: {i}/{len(candidate_pool)} candidates evaluated...")

        # Group possible words by the feedback pattern they would produce with this guess
        feedback_groups = defaultdict(list)
        for secret_word_candidate in possible_words:
            try:
                pattern = calculate_feedback_pattern(candidate_guess, secret_word_candidate)
                feedback_groups[pattern].append(secret_word_candidate)
            except Exception as e:
                print(f"Error calculating feedback for {candidate_guess} vs {secret_word_candidate}: {e}")
                continue

        if not feedback_groups:
            continue

        if strategy == "minimax":
            # Find the largest group size (worst case) - lower is better
            max_group_size = max(len(group) for group in feedback_groups.values())
            # Convert to score where higher is better (invert the group size)
            score = 1.0 / max_group_size if max_group_size > 0 else 1.0
            
            # Tie-breaking bonus: prefer words that are possible answers
            if candidate_guess in possible_words:
                score += 0.001  # Small bonus for tie-breaking
        
        else:  # entropy strategy
            # Calculate expected information gain (entropy) - higher is better
            score = 0.0
            total_possible = len(possible_words)
            
            for pattern_group in feedback_groups.values():
                if len(pattern_group) > 0:
                    p_pattern = len(pattern_group) / total_possible
                    score -= p_pattern * math.log2(p_pattern)
            
            # Tie-breaking bonus: prefer words that are possible answers
            if candidate_guess in possible_words:
                score += 0.001  # Small bonus for tie-breaking

        candidate_scores.append((candidate_guess, score))

    if not candidate_scores:
        # Fallback to original heuristic if advanced strategy fails
        print("Advanced strategy failed, falling back to heuristic...")
        fallback_suggestions = choose_next_guess_heuristic(possible_words, all_words, False, top_n)
        return fallback_suggestions

    # Sort by score (descending - higher scores are better)
    candidate_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N suggestions
    top_suggestions = candidate_scores[:top_n]
    print(f"Top {len(top_suggestions)} suggestions (Strategy: {strategy}):")
    for i, (word, score) in enumerate(top_suggestions):
        print(f"  {i+1}. {word.upper()} (score: {score:.3f})")
    
    return top_suggestions

def choose_next_guess_heuristic(possible_words, all_words, is_first_guess, top_n=5):
    """
    Original heuristic-based guess selection (renamed from choose_next_guess).
    
    Returns:
        List of tuples: [(word, score), ...] ranked from best to worst
    """
    if is_first_guess:
        starters = ["crane", "slate", "soare", "adieu", "audio", "raise", "least", "trace"]
        valid_starters = [s for s in starters if len(s) == WORD_LENGTH and s in all_words]
        if valid_starters:
            return [(word, 1.0) for word in valid_starters[:top_n]]
        fallback = [random.choice(all_words)] if all_words else []
        return [(word, 1.0) for word in fallback]

    if not possible_words:
        return []
    if len(possible_words) == 1:
        return [(possible_words[0], 1.0)]

    candidate_scores = []  # List of (word, score) tuples

    # Determine search space
    if len(possible_words) < 15:
        search_space_for_guess = possible_words
    else:
        search_space_for_guess = all_words

    # Calculate letter frequencies
    current_letter_freq = Counter()
    for word in possible_words:
        for char_val in set(word):
            current_letter_freq[char_val] += 1

    if not search_space_for_guess:
        fallback = possible_words[:1] if possible_words else (all_words[:1] if all_words else [])
        return [(word, 1.0) for word in fallback]

    for candidate_word in search_space_for_guess:
        if len(candidate_word) != WORD_LENGTH:
            continue
            
        current_score = 0.0
        unique_letters_in_candidate = set(candidate_word)

        for char_val in unique_letters_in_candidate:
            current_score += current_letter_freq[char_val]
        
        # Apply penalties and bonuses
        if search_space_for_guess is all_words and candidate_word not in possible_words:
            current_score *= 0.85
        
        if len(unique_letters_in_candidate) == WORD_LENGTH:
            current_score *= 1.05

        # Tie-breaking bonus: prefer words that are possible answers
        if candidate_word in possible_words:
            current_score += 0.001

        candidate_scores.append((candidate_word, current_score))

    # Sort by score (descending - higher scores are better)
    candidate_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N suggestions
    return candidate_scores[:top_n]

# Main choose_next_guess function - now routes to appropriate strategy
def choose_next_guess(possible_words, all_words, is_first_guess, use_advanced=False, strategy="entropy", top_n=5):
    """
    Main function to choose the next guess. Routes to either advanced or heuristic strategy.
    
    Args:
        possible_words: Words that could still be the answer
        all_words: Full word list
        is_first_guess: Whether this is the first guess
        use_advanced: Whether to use minimax/entropy (slower but more optimal)
        strategy: "minimax" or "entropy" (only used if use_advanced=True)
        top_n: Number of top suggestions to return
        
    Returns:
        List of tuples: [(word, score), ...] ranked from best to worst
    """
    if use_advanced and len(possible_words) > 1:
        return choose_next_guess_advanced(possible_words, all_words, strategy, is_first_guess, top_n)
    else:
        return choose_next_guess_heuristic(possible_words, all_words, is_first_guess, top_n)

def load_word_list(filename=WORD_LIST_FILENAME):
    """Loads a list of 5-letter words from a file."""
    try:
        with open(filename, 'r') as f:
            words = [line.strip().lower() for line in f if len(line.strip()) == WORD_LENGTH and line.strip().isalpha()]
        if not words:
            print(f"Warning: '{filename}' is empty or contains no valid {WORD_LENGTH}-letter words. Using example word list.")
            return EXAMPLE_WORD_LIST
        return words
    except FileNotFoundError:
        print(f"Warning: '{filename}' not found. Using example word list.")
        return EXAMPLE_WORD_LIST

class WordleGUI:
    def __init__(self, master):
        self.master = master
        master.title("Wordle Solver GUI - Advanced")

        self.WORD_LENGTH = 5
        self.MAX_ATTEMPTS = 6

        self.full_word_list = load_word_list()
        if not self.full_word_list:
            messagebox.showerror("Error", "Word list could not be loaded. Exiting.")
            master.destroy()
            return

        self.feedback_colors = {
            'b': "#787c7e",  # Grey
            'y': "#c9b458",  # Yellow
            'g': "#6aaa64",  # Green
            'default': "#d3d6da" # Light grey for empty/unguessed
        }
        self.text_color = "white"

        self.current_attempt = 0
        self.guess_history_gui = [] 
        self.solver_guess_history = [] 
        self.known_green_letters = {}
        
        # Advanced strategy settings
        self.use_advanced_strategy = tk.BooleanVar(value=False)
        self.strategy_type = tk.StringVar(value="entropy")
          # Multiple suggestions
        self.current_suggestions = []  # List of (word, score) tuples
        self.selected_suggestion = tk.StringVar(value="")
        self.current_guess_word = ""  # Current word to be guessed (from suggestion or custom input)

        self.setup_ui()
        self.start_new_game()

    def setup_ui(self):
        # --- Strategy Selection ---
        self.strategy_frame = tk.Frame(self.master, pady=5)
        self.strategy_frame.pack()
        
        tk.Label(self.strategy_frame, text="Strategy:", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.advanced_checkbox = tk.Checkbutton(self.strategy_frame, text="Use Advanced (Slower)", 
                                               variable=self.use_advanced_strategy, font=('Helvetica', 9))
        self.advanced_checkbox.pack(side=tk.LEFT, padx=5)
        
        self.entropy_radio = tk.Radiobutton(self.strategy_frame, text="Entropy", 
                                           variable=self.strategy_type, value="entropy", font=('Helvetica', 9))
        self.entropy_radio.pack(side=tk.LEFT, padx=2)
        
        self.minimax_radio = tk.Radiobutton(self.strategy_frame, text="Minimax", 
                                           variable=self.strategy_type, value="minimax", font=('Helvetica', 9))
        self.minimax_radio.pack(side=tk.LEFT, padx=2)
        
        # --- Guess Grid ---
        self.guess_grid_frame = tk.Frame(self.master, pady=10)
        self.guess_grid_frame.pack()
        self.letter_boxes = []
        for i in range(self.MAX_ATTEMPTS):
            row_frame = tk.Frame(self.guess_grid_frame)
            row_frame.pack()
            row_labels = []
            for j in range(self.WORD_LENGTH):
                lbl = tk.Label(row_frame, text="", width=4, height=2, 
                               font=('Helvetica', 16, 'bold'), borderwidth=2, relief="solid",
                               bg=self.feedback_colors['default'], fg=self.text_color)
                lbl.pack(side=tk.LEFT, padx=2, pady=2)
                row_labels.append(lbl)
            self.letter_boxes.append(row_labels)        # --- Suggested Word & Feedback Input ---
        self.suggestion_frame = tk.Frame(self.master, pady=10)
        self.suggestion_frame.pack()
        
        tk.Label(self.suggestion_frame, text="Top 5 Suggestions:", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, padx=5)
        
        # Frame for suggestion radio buttons
        self.suggestions_list_frame = tk.Frame(self.suggestion_frame)
        self.suggestions_list_frame.pack(anchor=tk.W, padx=20)
          # --- Custom Word Entry ---
        self.custom_entry_frame = tk.Frame(self.master, pady=10)
        self.custom_entry_frame.pack()
        
        tk.Label(self.custom_entry_frame, text="Or enter your own word:", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W, padx=5)
        
        self.custom_word_input_frame = tk.Frame(self.custom_entry_frame)
        self.custom_word_input_frame.pack(anchor=tk.W, padx=20, pady=5)
        
        tk.Label(self.custom_word_input_frame, text="Your word:", font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        self.custom_word_entry = tk.Entry(self.custom_word_input_frame, font=('Helvetica', 12), width=8, 
                                         validate='key', validatecommand=(self.master.register(self.validate_word_input), '%P'))
        self.custom_word_entry.pack(side=tk.LEFT, padx=5)
        self.custom_word_entry.bind('<Return>', self.use_custom_word)
        
        self.use_custom_button = tk.Button(self.custom_word_input_frame, text="Use This Word", 
                                          font=('Helvetica', 10), command=self.use_custom_word)
        self.use_custom_button.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        tk.Label(self.custom_entry_frame, text="Enter a 5-letter word you tried, then set feedback colors below", 
                 font=('Helvetica', 9), fg='gray').pack(anchor=tk.W, padx=20)
        
        # Current selected word display
        self.current_word_frame = tk.Frame(self.master, pady=5)
        self.current_word_frame.pack()
        
        tk.Label(self.current_word_frame, text="Selected Word:", font=('Helvetica', 12)).pack(side=tk.LEFT, padx=5)
        self.suggested_word_label = tk.Label(self.current_word_frame, text="-----", font=('Helvetica', 14, 'bold'), 
                                           width=10, bg="#e0e0e0", relief="sunken")
        self.suggested_word_label.pack(side=tk.LEFT, padx=5)

        self.feedback_input_frame = tk.Frame(self.master, pady=5)
        self.feedback_input_frame.pack()
        self.feedback_buttons = []
        for i in range(self.WORD_LENGTH):
            fb_btn_frame = tk.Frame(self.feedback_input_frame) 
            fb_btn_frame.pack(side=tk.LEFT, padx=3)

            char_label = tk.Label(fb_btn_frame, text="-", font=('Helvetica', 16, 'bold'), width=2)
            char_label.pack()
            
            btn = tk.Button(fb_btn_frame, text=" ", width=3, height=1, 
                            bg=self.feedback_colors['b'], relief=tk.RAISED,
                            command=lambda idx=i: self.cycle_feedback_color(idx))
            btn.pack()
            self.feedback_buttons.append({'button': btn, 'char_label': char_label, 'current_color_key': 'b'})

        self.submit_feedback_button = tk.Button(self.master, text="Submit Feedback", font=('Helvetica', 12), command=self.process_feedback)
        self.submit_feedback_button.pack(pady=5)
        self.submit_feedback_button.config(state=tk.DISABLED)

        # --- Status and Controls ---
        self.status_label = tk.Label(self.master, text="Welcome! Select strategy and click 'Start New Game'.", font=('Helvetica', 10), pady=10)
        self.status_label.pack()

        self.controls_frame = tk.Frame(self.master, pady=10)
        self.controls_frame.pack()
        self.restart_button = tk.Button(self.controls_frame, text="Restart Game", font=('Helvetica', 12), command=self.start_new_game)
        self.restart_button.pack(side=tk.LEFT, padx=10)
        
        self.possibilities_label = tk.Label(self.controls_frame, text="", font=('Helvetica', 10))
        self.possibilities_label.pack(side=tk.LEFT, padx=10)
    def validate_word_input(self, new_value):
        """Validate the custom word input."""
        if len(new_value) > self.WORD_LENGTH:
            return False
        if not all(c.isalpha() or c.isspace() for c in new_value):
            return False
        return True

    def use_custom_word(self, event=None):
        """Use the custom word entered by the user."""
        custom_word = self.custom_word_entry.get().strip().lower()
        if len(custom_word) != self.WORD_LENGTH:
            messagebox.showerror("Error", f"Custom word must be exactly {self.WORD_LENGTH} letters.")
            return
        if custom_word in self.full_word_list:
            messagebox.showinfo("Info", "Custom word accepted.")
            self.current_possible_words = [custom_word]  # Directly set as the only possibility
            self.solver_guess_history = []  # Clear history as this is a new word
            
            # Reset UI elements
            self.current_attempt = 0
            self.guess_history_gui = []
            self.known_green_letters = {}
            self.selected_suggestion.set("")  # Clear selection
            
            # Clear feedback buttons
            for fb in self.feedback_buttons:
                fb['button'].config(bg=self.feedback_colors['b'])
                fb['char_label'].config(text="-")
                fb['current_color_key'] = 'b'
            
            # Clear letter boxes
            for row in self.letter_boxes:
                for lbl in row:
                    lbl.config(text="", bg=self.feedback_colors['default'])
            
            self.status_label.config(text="Custom word set. Start guessing!")
            self.possibilities_label.config(text=f"{len(self.current_possible_words)} possibility")
            self.submit_feedback_button.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "Custom word not in word list.")

    def cycle_feedback_color(self, button_index):
        current_key = self.feedback_buttons[button_index]['current_color_key']
        if current_key == 'b':
            next_key = 'y'
        elif current_key == 'y':
            next_key = 'g'
        else: # current_key == 'g'
            next_key = 'b'
        
        self.feedback_buttons[button_index]['button'].config(bg=self.feedback_colors[next_key])
        self.feedback_buttons[button_index]['current_color_key'] = next_key

    def update_suggestions_display(self):
        """Update the GUI to show the top 5 suggestions"""
        # Clear existing suggestion radio buttons
        for widget in self.suggestions_list_frame.winfo_children():
            widget.destroy()
        
        if not self.current_suggestions:
            tk.Label(self.suggestions_list_frame, text="No suggestions available", 
                    font=('Helvetica', 10)).pack(anchor=tk.W)
            return
        
        # Create radio buttons for each suggestion
        for i, (word, score) in enumerate(self.current_suggestions):
            rank_text = f"{i+1}. {word.upper()}"
            if len(self.current_suggestions) > 1:  # Only show scores if multiple suggestions
                rank_text += f" (score: {score:.3f})"
            
            rb = tk.Radiobutton(self.suggestions_list_frame, text=rank_text, 
                               variable=self.selected_suggestion, value=word,
                               font=('Helvetica', 10), anchor=tk.W,
                               command=self.on_suggestion_selected)
            rb.pack(anchor=tk.W, pady=1)
        
        # Select the first (best) suggestion by default
        if self.current_suggestions:
            self.selected_suggestion.set(self.current_suggestions[0][0])
            self.on_suggestion_selected()
    
    def on_suggestion_selected(self):
        """Handle when user selects a different suggestion"""
        selected_word = self.selected_suggestion.get()
        if selected_word:
            self.current_guess_word = selected_word.lower()
            self.suggested_word_label.config(text=selected_word.upper())
            
            # Update feedback button characters and set their colors
            for i in range(self.WORD_LENGTH):
                char_in_suggestion = self.current_guess_word[i]
                self.feedback_buttons[i]['char_label'].config(text=char_in_suggestion.upper())
                  # Check if this letter at this position is a known green
                if i in self.known_green_letters and self.known_green_letters[i] == char_in_suggestion:
                    self.feedback_buttons[i]['button'].config(bg=self.feedback_colors['g'])
                    self.feedback_buttons[i]['current_color_key'] = 'g'
                else:
                    self.feedback_buttons[i]['button'].config(bg=self.feedback_colors['b'])
                    self.feedback_buttons[i]['current_color_key'] = 'b'   
                    
    def start_new_game(self):
        self.current_attempt = 0
        self.guess_history_gui = []
        self.solver_guess_history = []
        self.known_green_letters = {} # Reset known green letters for a new game
        self.current_possible_words = list(self.full_word_list)
        self.current_suggestions = []  # Reset suggestions
        self.selected_suggestion.set("")  # Clear selection
        self.current_guess_word = ""  # Clear current guess word

        for i in range(self.MAX_ATTEMPTS):
            for j in range(self.WORD_LENGTH):
                self.letter_boxes[i][j].config(text="", bg=self.feedback_colors['default'])
        
        # Clear custom word entry
        self.custom_word_entry.delete(0, tk.END)
        
        self.status_label.config(text="New game started. Good luck!")
        self.possibilities_label.config(text=f"{len(self.current_possible_words)} possibilities")
        self.submit_feedback_button.config(state=tk.NORMAL)
        self.make_suggestion()

        for i in range(self.MAX_ATTEMPTS):
            for j in range(self.WORD_LENGTH):
                self.letter_boxes[i][j].config(text="", bg=self.feedback_colors['default'])
        
        # Clear custom word entry
        self.custom_word_entry.delete(0, tk.END)
        
        self.status_label.config(text="New game started. Good luck!")
        self.possibilities_label.config(text=f"{len(self.current_possible_words)} possibilities")
        self.submit_feedback_button.config(state=tk.NORMAL)
        self.make_suggestion()

    def make_suggestion(self):
        if self.current_attempt >= self.MAX_ATTEMPTS:
            self.status_label.config(text="Max attempts reached!")
            self.submit_feedback_button.config(state=tk.DISABLED)
            messagebox.showinfo("Game Over", "Max attempts reached. Start a new game.")
            return

        is_first = self.current_attempt == 0
        use_advanced = self.use_advanced_strategy.get()
        strategy = self.strategy_type.get()
        
        # Update status to show thinking for advanced strategies
        if use_advanced and len(self.current_possible_words) > 1:
            self.status_label.config(text=f"Thinking... (using {strategy} strategy)")
            self.master.update()  # Force GUI update to show thinking message
        
        # Get top 5 suggestions
        suggestions = choose_next_guess(self.current_possible_words, self.full_word_list, 
                                      is_first_guess=is_first, use_advanced=use_advanced, 
                                      strategy=strategy, top_n=5)

        if not suggestions:
            self.status_label.config(text="No more words possible or error.")
            self.submit_feedback_button.config(state=tk.DISABLED)
            messagebox.showwarning("Solver", "Could not find any possible words based on feedback.")
            return

        # Store suggestions and update display
        self.current_suggestions = suggestions
        self.update_suggestions_display()

        # Update status
        strategy_text = f" ({strategy})" if use_advanced else " (heuristic)"
        self.status_label.config(text=f"Suggestions ready{strategy_text}. Select one and set feedback.")
        
        self.submit_feedback_button.config(state=tk.NORMAL)


    def process_feedback(self):
        if not self.current_guess_word:
            messagebox.showerror("Error", "No guess has been made yet.")
            return

        feedback_str_for_solver = ""
        user_feedback_for_solver = [] # For the solver's filter_words function

        # Update GUI grid for the current guess
        for j in range(self.WORD_LENGTH):
            char = self.current_guess_word[j]
            color_key = self.feedback_buttons[j]['current_color_key']
            feedback_str_for_solver += color_key # 'g', 'y', or 'b'
            
            self.letter_boxes[self.current_attempt][j].config(text=char.upper(), 
                                                              bg=self.feedback_colors[color_key],
                                                              fg=self.text_color)
            user_feedback_for_solver.append({'char': char, 'color': color_key, 'position': j})
            
            # Update known green letters
            if color_key == 'g':
                self.known_green_letters[j] = char

        # Check for win
        if all(fb['color'] == 'g' for fb in user_feedback_for_solver):
            self.status_label.config(text=f"Word '{self.current_guess_word.upper()}' found in {self.current_attempt + 1} attempts!")
            self.submit_feedback_button.config(state=tk.DISABLED)
            messagebox.showinfo("Congratulations!", f"You found the word: {self.current_guess_word.upper()}")
            return

        # Add to solver history and filter
        self.solver_guess_history.append({'guess': self.current_guess_word, 'feedback': user_feedback_for_solver})
        self.current_possible_words = filter_words(self.current_possible_words, self.solver_guess_history)
        
        self.possibilities_label.config(text=f"{len(self.current_possible_words)} possibilities")

        if not self.current_possible_words:
            self.status_label.config(text="No words match the feedback. Check input or restart.")
            self.submit_feedback_button.config(state=tk.DISABLED)
            messagebox.showwarning("Hmm...", "No possible words left based on your feedback.")
            return

        self.current_attempt += 1
        if self.current_attempt >= self.MAX_ATTEMPTS:
            self.status_label.config(text=f"Game over! Word not found. Possibilities: {len(self.current_possible_words)}")
            self.submit_feedback_button.config(state=tk.DISABLED)
            if self.current_possible_words:
                 messagebox.showinfo("Game Over", f"Word not found. Possible words were: {', '.join(self.current_possible_words[:5])}{'...' if len(self.current_possible_words) > 5 else ''}")
            else:
                 messagebox.showinfo("Game Over", "Word not found.")
            return
        
        self.make_suggestion()

# Remove or comment out the old play_wordle_solver and get_feedback_from_user functions
# def get_feedback_from_user(guess): ...
# def play_wordle_solver(): ...

if __name__ == "__main__":
    root = tk.Tk()
    gui = WordleGUI(root)
    root.mainloop()
