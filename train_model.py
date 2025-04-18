import json
import random
import pickle
import string
from pathlib import Path

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


# Expanded and labeled dataset (now 240 examples across 12 categories)
X = [
    # Love (expanded from 10 to 20)
    "Send a love message to Sarah",
    "Text my girlfriend that I love her",
    "Say I miss you to Emma",
    "Tell Anna she's the best part of my day",
    "Text John that he makes me smile",
    "Tell Claire I can't stop thinking about her",
    "Let Sam know I love him",
    "Say 'I adore you' to Mia",
    "Send a sweet note to Lily",
    "Message Olivia that I'm in love",
    "Tell David my heart belongs to him",
    "Send romantic words to Sophia",
    "Whisper sweet nothings to Ethan",
    "Text my partner how much they mean to me",
    "Tell Jessica she's my everything",
    "Send a heart emoji to Michael",
    "Write a love poem for Rachel",
    "Tell my sweetheart I cherish them",
    "Send a loving thought to Daniel",
    "Text my beloved goodnight with love",
    
    # Apology (expanded from 10 to 20)
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
    "Text Sarah my sincere apologies",
    "Tell John I messed up and I'm sorry",
    "Send an apology note to my boss",
    "Say sorry to mom for forgetting",
    "Apologize to David for the delay",
    "Tell Emma I owe her an apology",
    "Send a formal apology to Mr. Smith",
    "Text my roommate sorry for the mess",
    "Tell the team I regret my actions",
    "Apologize to my sister for being mean",
    
    # Birthday (expanded from 10 to 20)
    "Wish happy birthday to Amanda",
    "Send birthday wishes to Mike",
    "Tell Joseph happy birthday",
    "Text Lisa a birthday greeting",
    "Say birthday message to grandma",
    "Wish Emma a fabulous birthday",
    "Send a happy birthday text to Noah",
    "Greet Ryan on his birthday",
    "Say cheers to Jane's birthday",
    "Tell Sophia happy birthday with love",
    "Wish dad a wonderful birthday",
    "Send birthday blessings to aunt Mary",
    "Text my nephew happy birthday",
    "Say happy birthday to my best friend",
    "Send cake emojis to birthday boy Tom",
    "Wish my colleague a happy birthday",
    "Text birthday greetings to the team",
    "Say happy birthday to my neighbor",
    "Send a virtual birthday card to Lisa",
    "Wish my teacher a happy birthday",
    
    # Funny (expanded from 10 to 20)
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
    "Text Chris a funny GIF",
    "Send a comedy clip to Emma",
    "Tell a knock-knock joke to Noah",
    "Share a funny story with Olivia",
    "Send a ridiculous meme to James",
    "Text a sarcastic comment to Sophia",
    "Tell Ethan something absurd",
    "Send a witty remark to Jessica",
    "Text a funny observation to Mike",
    "Share a comedy reel with Anna",
    
    # Motivational (expanded from 10 to 20)
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
    "Text words of encouragement to Sarah",
    "Tell Alex they're capable of great things",
    "Send an uplifting quote to James",
    "Motivate the team for the big project",
    "Tell my sister she's stronger than she thinks",
    "Send a power message to my workout buddy",
    "Text my mentee some encouragement",
    "Tell my friend to believe in themselves",
    "Send a positive affirmation to Rachel",
    "Text a boost of confidence to Daniel",
    
    # Greetings (expanded from 10 to 20)
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
    "Send good night wishes to grandma",
    "Text a cheerful hello to the group",
    "Say hi to my new neighbor",
    "Send morning greetings to the office",
    "Text a friendly hello to my professor",
    "Greet my long-lost friend",
    "Say hi to my childhood buddy",
    "Send a formal greeting to the client",
    "Text a casual hey to my cousin",
    "Greet everyone in the family chat",
    
    # Thank you (expanded from 10 to 20)
    "Thank Melissa",
    "Send a thank you to grandma",
    "Say I appreciate you to John",
    "Text Sarah thanks for helping",
    "Tell James thank you for yesterday",
    "Let Emma know I'm grateful",
    "Send appreciation to Max",
    "Say cheers to Lucy for her help",
    "Tell Ava thanks a lot",
    "Text thank you to Robert",
    "Send a thank you note to my teacher",
    "Express gratitude to my doctor",
    "Thank the delivery person",
    "Send thanks to the support team",
    "Text my parents how much I appreciate them",
    "Thank my colleague for covering my shift",
    "Send a gratitude message to my mentor",
    "Text thanks for the birthday gift",
    "Thank my friend for listening",
    "Send a heartfelt thank you to my partner",
    
    # Casual (expanded from 10 to 20)
    "Text Jess what's up",
    "Send a message to Daniel saying how are you",
    "Ask Tobi how he's doing",
    "Check in with Claire",
    "Say yo to Ben",
    "Text Alex just to chat",
    "Send 'what's new' to Emma",
    "Say howdy to Luke",
    "Ping Mia to say hi",
    "Drop a casual message to Josh",
    "Text my brother to see what he's up to",
    "Send a quick 'you there?' to Sarah",
    "Ask mom if she's free to talk",
    "Hit up my old friend to reconnect",
    "Text the group chat with a random thought",
    "Send a 'thinking of you' to my cousin",
    "Drop a line to my college roommate",
    "Text my coworker about lunch plans",
    "Send a casual check-in to my neighbor",
    "Message my gym buddy about workouts",
    
    # New category: Plans (20 examples)
    "Ask Sarah if she wants to meet up",
    "Text the group about weekend plans",
    "See if Alex wants to grab coffee",
    "Check with Emma about dinner tonight",
    "Ask John if he's free tomorrow",
    "Invite Mia to the movies",
    "Text David about the project meeting",
    "See what time mom wants to meet",
    "Ask Lisa if she's coming to the party",
    "Check with James about the game night",
    "Text my team about the schedule",
    "Ask my sister if she needs help",
    "See if Noah wants to study together",
    "Check with Olivia about travel plans",
    "Ask my neighbor about the package",
    "Text my friend about concert tickets",
    "See if dad needs anything from the store",
    "Ask my roommate about rent payment",
    "Check with my boss about the deadline",
    "Text my cousin about family reunion",
    
    # New category: Reminders (20 examples)
    "Remind mom about her appointment",
    "Text James not to forget the keys",
    "Tell Sarah about the meeting at 3",
    "Remind the team about the deadline",
    "Send a reminder to dad about dinner",
    "Text my sister to call me back",
    "Remind Alex about the documents",
    "Tell Emma to bring her laptop",
    "Send a reminder about the payment",
    "Text John to pick up milk",
    "Remind myself to call the doctor",
    "Tell my roommate about the guest",
    "Send a medication reminder to grandma",
    "Text my coworker about the report",
    "Remind my friend about our plans",
    "Tell my brother it's trash day",
    "Send a birthday reminder for Lisa",
    "Text my partner about dry cleaning",
    "Remind the group about the event",
    "Tell my neighbor about parking rules",
    
    # New category: Questions (20 examples)
    "Ask Sarah how her day was",
    "Text mom what she's cooking",
    "Ask John if he needs anything",
    "See what Emma thinks about the idea",
    "Ask David for his opinion",
    "Text my boss when I should come in",
    "Ask my sister how her trip was",
    "See if Alex finished the project",
    "Ask Lisa where she wants to eat",
    "Text my friend why he's upset",
    "Ask the group what time to meet",
    "See what my teacher said about homework",
    "Ask my roommate who's coming over",
    "Text my dad how his doctor visit went",
    "Ask my neighbor about the noise",
    "See what my coworker thinks of the plan",
    "Ask my partner what they want to watch",
    "Text my cousin when she's arriving",
    "Ask my mentor for advice",
    "See what my client needs changed"
]

y = (
    ["love"] * 20 +
    ["apology"] * 20 +
    ["birthday"] * 20 +
    ["funny"] * 20 +
    ["motivational"] * 20 +
    ["greeting"] * 20 +
    ["thank_you"] * 20 +
    ["casual"] * 20 +
    ["plans"] * 20 +
    ["reminder"] * 20 +
    ["question"] * 20
)


# Enhanced preprocessing function
def preprocess(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    # Remove extra whitespace
    text = " ".join(text.split())
    return text


X = [preprocess(text) for text in X]

# Split for evaluation (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    stratify=y, 
    test_size=0.2, 
    random_state=42
)

# Enhanced Pipeline with better parameters
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),  # Consider unigrams and bigrams
        min_df=2,            # Ignore terms that appear in only 1 document
        max_df=0.8           # Ignore terms that appear in >80% of documents
    )),
    ('clf', LogisticRegression(
        max_iter=1000,
        class_weight='balanced',  # Handle class imbalance
        C=0.5,                    # Regularization strength
        solver='liblinear'         # Good for small datasets
    ))
])

# Train the model
pipeline.fit(X_train, y_train)

# Evaluation
y_pred = pipeline.predict(X_test)

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# Confusion matrix visualization
def plot_confusion_matrix(y_true, y_pred, classes):
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.close()

plot_confusion_matrix(y_test, y_pred, pipeline.classes_)
print("Confusion matrix saved as 'confusion_matrix.png'")

# Save model pipeline
MODEL_PATH = Path("model_pipeline.pkl")
with open(MODEL_PATH, "wb") as f:
    pickle.dump(pipeline, f)

# Enhanced templates with more variety
templates = {
    "love": [
        "Hey {name}, just wanted to say I love you ❤️",
        "Thinking about you, {name} 💕 You mean the world to me.",
        "You make every day better, {name}. I'm so grateful for you.",
        "Can't stop smiling because of you, {name} 😊",
        "My heart belongs to you, {name} 💘",
        "Just a reminder: You're amazing, {name} 💖",
        "Missing you extra today, {name} 💌",
        "You're my favorite person, {name} 💑",
        "Sending you all my love, {name} 💞",
        "Forever yours, {name} 💍"
    ],
    "apology": [
        "Hey {name}, I'm really sorry. Can we talk?",
        "I regret what I said, {name}. Please forgive me.",
        "Sorry for being off lately, {name}. I'll do better.",
        "My sincerest apologies, {name}. I was wrong.",
        "{name}, I messed up and I want to make it right.",
        "I owe you an apology, {name}. I'm truly sorry.",
        "Please accept my apology, {name}. It won't happen again.",
        "{name}, I was out of line and I'm sorry.",
        "I feel terrible about what happened, {name}. Can we start over?",
        "My behavior was unacceptable, {name}. I apologize."
    ],
    "birthday": [
        "Happy Birthday {name}! 🎉🎂 Wishing you an amazing year ahead!",
        "Wishing you all the best today, {name}! Hope it's filled with joy!",
        "Enjoy your special day, {name}! 🎁🎈",
        "To many more candles, {name} 🎂🎉 Happy Birthday!",
        "Another year wiser! Happy Birthday {name} 🥳",
        "Celebrate yourself today, {name}! Happy Birthday 🎊",
        "Wishing you health, happiness and success, {name}! 🎂",
        "Hope your birthday is as wonderful as you are, {name}! 💝",
        "Age is just a number! Happy Birthday young {name} 🎁",
        "Sending virtual cake your way, {name} 🍰 Happy Birthday!"
    ],
    "funny": [
        "Hey {name}, why don't scientists trust atoms? Because they make up everything! 😂",
        "You always brighten my day, {name}. Even more than a meme!",
        "Here's a joke for you, {name}: Parallel lines have so much in common. It's a shame they'll never meet 😅",
        "{name}, what do you call fake spaghetti? An impasta! 🍝",
        "Why don't eggs tell jokes? They'd crack each other up! 🥚😂 - for you {name}",
        "{name}, I told my dog a joke. He said it was ruff. 🐶",
        "What's brown and sticky? A stick! 😆 - thought you'd like this {name}",
        "{name}, why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
        "I'm reading a book about anti-gravity, {name}. It's impossible to put down! 📚",
        "{name}, what's the best thing about Switzerland? I don't know but the flag is a big plus! 🇨🇭"
    ],
    "motivational": [
        "You've got this, {name}! 💪 Keep pushing forward!",
        "Keep pushing, {name}. Greatness awaits just around the corner.",
        "Just a reminder that you're awesome, {name}. Believe in yourself!",
        "Every step counts, {name}. Keep going! You're making progress.",
        "Challenges are what make life interesting, {name}. Overcoming them is what makes life meaningful.",
        "You're stronger than you think, {name}. 💫",
        "Success is the sum of small efforts repeated daily, {name}. Keep at it!",
        "Your potential is endless, {name}. Go after what you deserve!",
        "Tough times don't last, tough people do, {name}. Stay strong!",
        "The only limit is the one you set yourself, {name}. Dream bigger!"
    ],
    "greeting": [
        "Good morning, {name}! ☀️ Hope you have a wonderful day!",
        "Hey {name}, just saying hello 👋 How's your day going?",
        "Hope you're having a great day, {name}! 😊",
        "Hello {name}, thinking of you today! 💭",
        "Good evening, {name}! 🌙 Sleep well when you do!",
        "Hi there {name}! Just checking in 💌",
        "Greetings {name}! Sending positive vibes your way ✨",
        "Hey you! Yes you, {name}! Hope all is well 😄",
        "Hi {name}! Just wanted to brighten your day ☀️",
        "Good afternoon, {name}! Hope you're having a productive day 📚"
    ],
    "thank_you": [
        "Thanks a ton, {name}! I really appreciate it 🙏",
        "I really appreciate you, {name}. Thank you for everything!",
        "Couldn't have done it without you, {name}! Many thanks!",
        "Just wanted to say thank you, {name} 🙏 Means a lot!",
        "From the bottom of my heart, thank you {name} 💖",
        "Your help was invaluable, {name}. Thank you so much!",
        "I'm so grateful for your support, {name}. Thank you!",
        "Thanks for being there, {name}. It means everything to me.",
        "A big thank you, {name}! You're amazing!",
        "Thank you thank you thank you, {name}! 🎉"
    ],
    "casual": [
        "Hey {name}, what's up? How's life treating you?",
        "How's it going, {name}? Long time no chat!",
        "Yo {name}, everything good? Just checking in!",
        "Just checking in on you, {name}. Hope all is well!",
        "Hey hey {name}! What's new in your world?",
        "Howdy {name}! Been thinking about you lately.",
        "Hey there {name}! Got a minute to chat?",
        "What's cooking, {name}? How's life?",
        "Long time no see, {name}! How have you been?",
        "Hey {name}! Just wanted to say hi 👋"
    ],
    "plans": [
        "Hey {name}, are you free to meet up this weekend?",
        "Want to grab coffee soon, {name}?",
        "{name}, are you available for dinner tonight?",
        "Thinking of going to the movies, {name}. Want to join?",
        "Hey {name}, when are you free to catch up?",
        "{name}, let's plan something fun soon! When works for you?",
        "Are you around this weekend, {name}? Would love to meet!",
        "{name}, want to hang out soon? What's your schedule like?",
        "We should plan a get-together, {name}! When are you free?",
        "Hey {name}, are you up for an adventure this weekend?"
    ],
    "reminder": [
        "Just a reminder, {name}: Don't forget about your appointment!",
        "Hey {name}, remember to bring the documents today!",
        "{name}, this is your friendly reminder about our meeting at 3pm.",
        "Don't forget to call me back, {name}!",
        "{name}, reminder: It's trash day tomorrow!",
        "Hey {name}, just reminding you about the deadline!",
        "{name}, don't forget to pick up milk on your way home!",
        "Quick reminder, {name}: Your prescription needs refilling.",
        "{name}, remember we have guests coming over tonight!",
        "Don't forget to water the plants, {name}!"
    ],
    "question": [
        "Hey {name}, how was your day?",
        "What are your thoughts on this, {name}?",
        "{name}, do you need any help with anything?",
        "How did your presentation go, {name}?",
        "{name}, what's your opinion on this matter?",
        "Where would you like to eat, {name}?",
        "Why did you decide to do that, {name}?",
        "When are you available to meet, {name}?",
        "What time should we arrive, {name}?",
        "How's your new project coming along, {name}?"
    ]
}

# Save templates
with open("categories.json", "w") as f:
    json.dump(templates, f, indent=2)

# Function to load the model (for future use)
def load_model(model_path="model_pipeline.pkl"):
    with open(model_path, "rb") as f:
        return pickle.load(f)

# Function to predict message category
def predict_message_category(message, model=None):
    if model is None:
        model = load_model()
    processed = preprocess(message)
    return model.predict([processed])[0]

# Test the prediction function
test_message = "can you remind john about the meeting tomorrow"
predicted_category = predict_message_category(test_message)
print(f"\nTest prediction: '{test_message}' → {predicted_category}")

print("\n✅ Enhanced model trained and saved:")
print(f"- Model pipeline: {MODEL_PATH}")
print("- Categories templates: categories.json")
print("- Confusion matrix: confusion_matrix.png")