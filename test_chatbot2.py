import json
import chatbot
import re

# Load test cases from a separate JSON file
# Make sure to update the values in the JSON value to reflect concurrent company challenges!
with open("test_cases2.json", "r") as f:
    test_cases = json.load(f)

# Function to test the chatbot
def test_chatbot2():
    total_tests = 0
    correct_predictions = 0

    for case in test_cases:
        company = case["company"]
        challenges = case["challenges"]

        # Formulate the question
        question = f"What are the most significant challenges {company} is currently facing based on recent news and trends? Focus on industry-related, financial, and operational issues."
        
        # Get chatbot response
        chatbot_response = chatbot.rag(question)
        chatbot_response = chatbot_response.strip()

        # Print detailed results for each test case
        print(f"Question: {question}")
        print(f"Chatbot Response: {chatbot_response}")
        print(f"Correct Challenges: {challenges}")
        print("---")

        # Compare chatbot response with correct challenges
        for challenge in challenges:
            total_tests += 1

            # Check if the challenge is a list (synonyms)
            if isinstance(challenge, list):
                # Match any synonym in the list
                if any(re.search(rf'\b{re.escape(word.lower())}s?\b', chatbot_response.lower()) for word in challenge):
                    print(f"'{challenge}' found via synonym. Accuracy Score +1")
                    correct_predictions += 1
                else:
                    print(f"'{challenge}' not found in response. Incorrect")
            else:
                # Handle single challenges
                if re.search(rf'\b{re.escape(challenge.lower())}s?\b', chatbot_response.lower()):
                    print(f"'{challenge}' found. Accuracy Score +1")
                    correct_predictions += 1
                else:
                    print(f"'{challenge}' not found in response. Incorrect")

    # Calculate and print accuracy
    accuracy = f"{correct_predictions}/{total_tests}"
    print(f"Accuracy: {accuracy}")

# Run the test
if __name__ == "__main__":
    test_chatbot2()