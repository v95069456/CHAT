from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

app = Flask(__name__)

source = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatBot App</title>

    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #000;
            color: #fff;
            margin: 0;
            padding: 0;
        }

        h1 {
            text-align: center;
            color: #fff;
        }

        #chat-container {
            max-width: 600px;
            margin: 20px auto;
            background-color: #446;
            border: 1px solid #000;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        #chat {
            height: 300px;
            overflow-y: scroll;
            padding: 10px;
            border-bottom: 1px solid #555;
        }

        .user-message, .bot-message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 5px;
        }

        .user-message {
            color: #f8f;
        }

        .bot-message {
            color: #ff0000;
        }

        #userInput {
            width: calc(100% - 60px);
            padding: 8px;
            margin: 0;
            border: 1px solid #555;
            border-radius: 3px;
            color: #333;
            background-color: #fff;
        }

        button {
            width: 50px;
            padding: 8px;
            margin-left: 10px;
            border: none;
            background-color: #007bff;
            color: #fff;
            cursor: pointer;
            border-radius: 3px;
        }

        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>ChatBot App</h1>

    <div id="chat-container">
        <div id="chat"></div>
        <input type="text" id="userInput" placeholder="Type your message...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function sendMessage() {
            var userInput = document.getElementById("userInput").value;
            var chatDiv = document.getElementById("chat");
            var userMessage = document.createElement("div");
            userMessage.className = "user-message";
            userMessage.innerHTML = "<strong>You:</strong> " + userInput;
            chatDiv.appendChild(userMessage);

            document.getElementById("userInput").value = "";

            // AJAX request to get response from the bot
            var xhr = new XMLHttpRequest();
            xhr.open("GET", "/get?msg=" + userInput, true);
            xhr.onreadystatechange = function () {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var botMessage = document.createElement("div");
                    botMessage.className = "bot-message";
                    botMessage.innerHTML = "<strong>Bot:</strong> " + xhr.responseText;
                    chatDiv.appendChild(botMessage);
                }
            };
            xhr.send();
        }
    </script>
</body>
</html>
'''




generic_responses = ["Hello!", "Hi there!", "How are you?", "I'm good, thanks. How about you?", "I'm doing well too.", "What do you do for a living?", "I'm a chatbot created for demonstration purposes.", "That's interesting!", "Thank you! How can I help you today?", "Tell me a joke.", "Why did the computer go to therapy? It had too many bytes of emotional baggage!", "What's your favorite programming language?", "I don't have preferences, but I was built using Python!", "Tell me about artificial intelligence.", "Artificial intelligence (AI) is a branch of computer science that deals with creating machines capable of intelligent behavior.", "Do you like movies?", "I don't have personal preferences, but I can recommend some popular movies. What genre do you enjoy?", "What's your favorite book?", "I don't read books, but I can suggest some popular ones. Do you prefer fiction or non-fiction?", "How's the weather today?", "I'm sorry, I don't have real-time information. You can check a weather website or app for the current conditions.", "What's the meaning of life?", "The meaning of life is a philosophical question. Different people have different perspectives on it.", "Can you help me with my homework?", "Of course! What subject are you working on, and what specific help do you need?", "Tell me something interesting.", "Did you know that honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible!", "How do I stay motivated?", "Staying motivated can be challenging. Setting small, achievable goals and celebrating your progress can help keep you motivated.", "What's the best programming joke you know?", "Why do programmers prefer dark mode? Because light attracts bugs!", "Are you familiar with the concept of love?", "Love is a complex and profound emotion experienced by humans. It can take many forms, including romantic, platonic, and familial love.", "What's your favorite kind of music?", "I don't have personal preferences, but I can recommend music based on your taste. What genre are you into?", "I'm here to assist you. What can I help you with?", "That's interesting! Tell me more about it.", "Feel free to share your thoughts. I'm here to listen.", "I'm ready to help. What's on your mind?", "Interesting! How can I be of service?", "Let's dive into that topic. What specific information are you looking for?", "I'm here for you. What do you need assistance with?", "That's a great point! How can I support you further?", "Your input is valuable. Please share more details.", "I'm here to make your experience better. How can I assist you today?", "Thanks for reaching out. What can I do for you?", "Let's explore that together. What else can you tell me?", "I appreciate your engagement. What else would you like to discuss?", "Your questions are important. Ask away, and I'll do my best to help.", "I'm all ears. Feel free to share your thoughts or questions.",]
conclusion = ["Thank you!", "You're most welcome!", "Thanks!", "Of course!"]
engaging_responses = ["That's a thought-provoking perspective! How did you come up with it?", "I'm intrigued! Can you share more details about that?", 'Fascinating! Have you ever considered writing about your experiences?', 'Wow, I never thought about it that way. What inspired your viewpoint?', 'Impressive! Can you tell me more about your journey or discovery?', 'Your creativity knows no bounds! How do you stay inspired?', 'I love learning from different viewpoints. What other insights do you have?', 'You have a unique way of looking at things. What other interests or hobbies do you have?', "That's truly fascinating! How did you first discover that?", "I'm genuinely interested! Can you share more insights on that topic?", 'Impressive perspective! Have you considered exploring this idea further?', "Wow, that's a unique take! What inspired you to think in that direction?", 'Your creativity shines! How do you nurture your imaginative side?', 'Intriguing! Are there other areas where you apply such innovative thinking?', "I'm captivated by your ideas! Tell me, what other interests do you have?", 'You have a knack for originality. Can you elaborate on your thought process?', "That's fascinating! Tell me more.", "I never thought about it that way. What's your perspective?", 'Interesting! How did that make you feel?', "Wow, that's a unique point of view. Can you elaborate?", 'I love learning new things. What else can you share?', 'Your experiences are valuable. Keep the conversation flowing!', "I appreciate your creativity. Let's explore that idea further."]

bot = ChatBot(
    'Ghost',
    preprocessors=['chatterbot.preprocessors.convert_to_ascii', 'chatterbot.preprocessors.unescape_html', 'chatterbot.preprocessors.clean_whitespace'],
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        'chatterbot.logic.MathematicalEvaluation'
    ],
    statement_comparison_function='chatterbot.comparisons.levenshtein_distance',
    response_selection_method='chatterbot.response_selection.get_first_response',
    maximum_similarity_threshold=0.8,
    default_response='I am sorry, but I do not understand.'
)

trainer = ListTrainer(bot)
trainer.train(generic_responses + conclusion + engaging_responses)

@app.route("/")
def home():
    return source

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    response = str(bot.get_response(user_text)).replace('I need your assistance regarding my order', 'Hello!')
    return response

if __name__ == "__main__":
    app.run()
