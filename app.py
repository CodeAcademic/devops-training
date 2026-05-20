from flask import Flask, jsonify
import random
import string

app = Flask(__name__)


# ── Helper functions ──────────────────────────────────────────────────────────

def random_number():
    """Returns a random integer between 1 and 9999."""
    return random.randint(1, 9999)


def random_word():
    """Returns a random lowercase word of 4–8 characters."""
    length = random.randint(4, 8)
    return "".join(random.choices(string.ascii_lowercase, k=length))


def random_name():
    """Returns a random English first name from a fixed list."""
    names = [
        "Alice", "Bob", "Charlie", "Diana", "Edward",
        "Fatima", "George", "Hannah", "Ivan", "Julia",
    ]
    return random.choice(names)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    """Health check endpoint used by the CI pipeline."""
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    """Main endpoint — returns all three random values as JSON."""
    return jsonify({
        "number": random_number(),
        "word":   random_word(),    # comment out in iteration 2
        "name":   random_name(),    # comment out in iteration 3
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
