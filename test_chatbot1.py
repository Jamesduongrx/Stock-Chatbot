import json
import chatbot
import re

# Load test cases from a separate JSON file
# Make sure to update the values in the JSON value to reflect concurrent source recommendations!
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

        # Print detailed results for each test case
        print(f"Question: {question}")
        print(f"Chatbot Response: {chatbot_response}")
        print(f"Correct Recommendation: {recommendation}")
        print("---")

        # Compare chatbot recommendation with correct recommendation
        if any(keyword in chatbot_response.lower() for keyword in ["no", "bearish", "overvalued"]):
            print("Incorrect")
        else:
            if any(keyword in chatbot_response.lower() for keyword in ["yes", "undervalued", "bullish"]):
                print("Accuracy Score +1")
                correct_predictions += 1
            elif re.search(rf'\b{re.escape(recommendation.lower())}\b', chatbot_response.lower()):
                print("Accuracy Score +1")
                correct_predictions += 1
            else:
                print("Incorrect")

    # Calculate and print accuracy
    accuracy_fraction = f"{correct_predictions}/{total_tests}"
    accuracy_percentage = (correct_predictions / total_tests) * 100
    print(f"Accuracy: {accuracy_fraction} ({accuracy_percentage:.2f}%)")

# Run the test
if __name__ == "__main__":
    test_chatbot1()