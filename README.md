# DigiChat: A Nutrition AI Chatbot

DigiChat is a next-generation chatbot designed to deliver precise nutritional insights and health suggestions by leveraging advanced AI models and integrations. It seamlessly integrates with the Nutrition endpoint from API Ninjas, Edamam Meal Planning API, along with mock FitBit, providing accurate nutritional data, meal plans, and personalized health recommendations.

## Features
1. **Nutritional Information Retrieval:** Retrieves accurate nutritional data for a wide range of food items using the Nutrition endpoint of API Ninjas.
2. **Personalized Meal Planning:** Generates customized meal plans based on individual dietary needs, preferences, and health goals through the Edamam Meal Planning API.
3. **Activity and Health Tracking:** Incorporates mock FitBit data to provide insights on physical activity, sleep patterns, and overall health metrics.
4. **Health Calculations:** Computes Basal Metabolic Rate (BMR), Total Daily Energy Expenditure (TDEE), Ideal Body Weight (IBW), and more.
5. **Intelligent Recommendations:** Offers personalized health and nutrition advice by analyzing data from multiple sources.
6. **User-Friendly Interaction:** Features a chat-like interface that is easy to use and interact with.

## Setup and Installation

To get FitBot up and running, follow these steps:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/[YourUsername]/ams-691-project.git
   cd DigiChat

2. **Setup Virtual Environment (Optional)**

    It's recommended to create a virtual environment to keep the dependencies required by this project separate.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. **Install Dependencies**

    Install the required packages using pip:

    ```bash
    pip install -r requirements.txt

4. **Run the Project**

    You're all set! Run the project with:

    ```bash
    python run_chatbot.py

## Usage

Once the chatbot is up and running, you can start asking queries. Here's an example of how to interact with it:

   ```bash
   What is the TDEE of a 30-year-old man, who is 180 cm tall, weighs 80 kg, and exercises 3 times a week?
   ```

DigiChat will generate a meal plan based on the information provided and also inform the person's BMI.

## Support

If you encounter any issues or have any questions about the project, feel free to open an issue on this GitHub repository.

## License

DigiChat is open-source software licensed under the MIT license.
