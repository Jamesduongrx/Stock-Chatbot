import json
import chatbot
import re

# Load test cases from a separate JSON file
with open("test_cases1.json", "r") as f:
    test_cases = json.load(f)

# Initialize variables for scoring
total_tests = len(test_cases)
correct_predictions = 0

# Function to test the chatbot
def test_chatbot1():
    global correct_predictions

    for case in test_cases:
        company = case["company"]
        source = case["source"]
        recommendation = case["recommendation"]

        # Formulate the question
        question = f"Does {source} recommend {recommendation} for {company}?"

        # Get chatbot response
        chatbot_response = chatbot.rag(question)

        # Compare chatbot recommendation with correct recommendation
        if "no" in chatbot_response.lower() or
            "bearish" in chatbot_response.lower() or
            "overvalued" in chatbot_response.lower():
            continue
        elif ("yes" in chatbot_response.lower() or
            "undervalued" in chatbot_response.lower() or
            "bullish" in chatbot_response.lower() or
            re.search(rf'\b{re.escape(recommendation.lower())}\w*\b', chatbot_response.lower())):
            print("Accuracy Score +1")
            correct_predictions += 1

        # Print detailed results for each test case
        print(f"Question: {question}")
        print(f"Chatbot Recommendation: {chatbot_response}")
        print(f"Correct Recommendation: {recommendation}")
        print("---")

    # Calculate and print accuracy
    accuracy = f"{correct_predictions}/{total_tests}"
    print(f"Accuracy: {accuracy}")

# Run the test
if __name__ == "__main__":
    test_chatbot1()