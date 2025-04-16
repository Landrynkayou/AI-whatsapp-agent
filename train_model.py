from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle, json
import random

# Significantly expanded dataset
X = [
    # Love
    "Send a love message to Sarah",
    "Text my girlfriend that I love her",
    "Say I miss you to Emma",
    "Tell Anna she's the best part of my day",
    "Text John that he makes me smile",
    "Tell Claire I can't stop thinking about her",
    "Let Sam know I love him",
    "Say 'I adore you' to Mia",
    "Send a sweet note to Lily",
    "Message Olivia that I’m in love",

    # Apology
    "Tell Michael I'm sorry",
    "Send an apology to James",
    "Say sorry to Lily",
    "Apologize to Mark for being rude",
    "Tell Chloe I regret what I said",
    "Let Alex know I feel terrible",
    "Send a sorry message to Daniel",
    "Say I'm deeply sorry to Ava",
    "Tell Max I wish I could take it back",
    "Apologize to Emily from my heart",

    # Birthday
    "Wish happy birthday to Amanda",
    "Send birthday wishes to Mike",
    "Tell Joseph happy birthday",
    "Text Lisa a birthday greeting",
    "Say birthday message to grandma",
    "Wish Emma a fabulous birthday",
    "Send a happy birthday text to Noah",
    "Greet Ryan on his birthday",
    "Say cheers to Jane’s birthday",
    "Tell Sophia happy birthday with love",

    # Funny
    "Send a funny message to Daniel",
    "Text Sarah a joke",
    "Tell Alex something hilarious",
    "Send a pun to Kate",
    "Make John laugh",
    "Say something funny to Lily",
    "Share a dad joke with Tom",
    "Send meme-like message to Mia",
    "Tell Ava a hilarious one-liner",
    "Say something goofy to Max",

    # Motivational
    "Send a motivational message to Emma",
    "Tell Ben to keep going",
    "Inspire Mia with a message",
    "Send a pep talk to David",
    "Motivate Sam today",
    "Tell Chris to chase his dreams",
    "Encourage Olivia to stay strong",
    "Say 'you can do it' to Luke",
    "Push Hannah to keep grinding",
    "Send strength to Noah",

    # Greetings
    "Say good morning to mom",
    "Send a hello to Adam",
    "Text Naomi good afternoon",
    "Greet Peter",
    "Say hi to Laura",
    "Wish Alex a good evening",
    "Send a warm greeting to Emma",
    "Text hi to James",
    "Say hello to Jack",
    "Greet Sarah today",

    # Thank you
    "Thank Melissa",
    "Send a thank you to grandma",
    "Say I appreciate you to John",
    "Text Sarah thanks for helping",
    "Tell James thank you for yesterday",
    "Let Emma know I’m grateful",
    "Send appreciation to Max",
    "Say cheers to Lucy for her help",
    "Tell Ava thanks a lot",
    "Text thank you to Robert",

    # Casual
    "Text Jess what's up",
    "Send a message to Daniel saying how are you",
    "Ask Tobi how he's doing",
    "Check in with Claire",
    "Say yo to Ben",
    "Text Alex just to chat",
    "Send ‘what’s new’ to Emma",
    "Say howdy to Luke",
    "Ping Mia to say hi",
    "Drop a casual message to Josh"
]

# Corresponding categories
y = (
    ["love"] * 10 +
    ["apology"] * 10 +
    ["birthday"] * 10 +
    ["funny"] * 10 +
    ["motivational"] * 10 +
    ["greeting"] * 10 +
    ["thank_you"] * 10 +
    ["casual"] * 10
)

# Train the vectorizer and model
vectorizer = TfidfVectorizer()
X_vect = vectorizer.fit_transform(X)

model = LogisticRegression()
model.fit(X_vect, y)

# Save model and vectorizer in current directory
with open("generator.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

# Templates
templates = {
    "love": [
        "Hey {name}, just wanted to say I love you ❤️",
        "Thinking about you, {name} 💕",
        "You make every day better, {name}",
        "Can't stop smiling because of you, {name}"
    ],
    "apology": [
        "Hey {name}, I’m really sorry. Can we talk?",
        "I regret what I said, {name}. Please forgive me.",
        "Sorry for being off lately, {name}. I’ll do better.",
        "My sincerest apologies, {name}."
    ],
    "birthday": [
        "Happy Birthday {name}! 🎉🎂",
        "Wishing you all the best today, {name}!",
        "Enjoy your special day, {name}!",
        "To many more candles, {name} 🎂🎉"
    ],
    "funny": [
        "Hey {name}, why don’t scientists trust atoms? Because they make up everything! 😂",
        "You always brighten my day, {name}. Even more than a meme!",
        "Here’s a joke for you, {name}: Parallel lines have so much in common. It’s a shame they’ll never meet 😅"
    ],
    "motivational": [
        "You’ve got this, {name}! 💪",
        "Keep pushing, {name}. Greatness awaits.",
        "Just a reminder that you're awesome, {name}.",
        "Every step counts, {name}. Keep going!"
    ],
    "greeting": [
        "Good morning, {name}! ☀️",
        "Hey {name}, just saying hello 👋",
        "Hope you're having a great day, {name}!",
        "Hello {name}, thinking of you today!"
    ],
    "thank_you": [
        "Thanks a ton, {name}!",
        "I really appreciate you, {name}.",
        "Couldn't have done it without you, {name}!",
        "Just wanted to say thank you, {name} 🙏"
    ],
    "casual": [
        "Hey {name}, what’s up?",
        "How’s it going, {name}?",
        "Yo {name}, everything good?",
        "Just checking in on you, {name}."
    ]
}

# Save templates
with open("categories.json", "w") as f:
    json.dump(templates, f)

print("✅ Model trained and saved in the current directory with an expanded dataset.")
