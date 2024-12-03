import os
import logging
import gradio as gr
from fitness_agent import FitnessAgent
from dotenv import load_dotenv
from db import init_db, insert_user, insert_login, validate_login, insert_log, get_user_data
from gradio_modal import Modal
import hashlib


# Initialize the database when starting the app
init_db()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env.list
load_dotenv('.env.list')

# Now you can access the variables using os.environ
openai_api_key = os.getenv('OPENAI_API_KEY')
nut_api_key = os.getenv('NUT_API_KEY')

# Instantiate FitnessAgent here so it remains open
fitness_agent = FitnessAgent(openai_api_key, nut_api_key)

# Global variable to hold the logged-in user's email
logged_in_email = None  # Or use a session-based storage if available


def get_response(message, history):
    logger.info(f'Chat history: {history}')
    # Fetch user data
    # user_info, log_info = get_user_data(logged_in_email)
    # user_summary = summarize_user_data(user_info, log_info)

    formatted_chat_history = [
        {
            'role': 'system',
            'content': (
                'Assistant is a large language model trained by OpenAI.\n\nAssistant is designed to be able to assist with a wide range of tasks, '
                'from answering simple questions to providing in-depth explanations and discussion on a wide range of topics. As a language model, '
                'Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations '
                'and provide responses that are coherent and relevant to the topic at hand.\n\nAssistant is constantly learning and improving, '
                'and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge '
                'to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text '
                'based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.\n\n'
                'Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics.'
            )
        }
    ]

    if history:
        for i, chat in enumerate(history[0]):
            formatted_chat_history.append({
                'role': 'user' if i % 2 == 0 else 'assistant',
                'content': chat
            })

        logger.info(formatted_chat_history)
        fitness_agent.chat_history = formatted_chat_history

        logger.info(fitness_agent.chat_history)

    # Get raw chat response
    res = fitness_agent.ask(message)

    chat_response = res['choices'][0]['message']['content']

    return chat_response

def handle_login(email, password):
    global logged_in_email
    # Validate login credentials
    if validate_login(email, password):
        logged_in_email = email  # Set the email globally
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)
    else:
        # Invalid login, show the signup button
        return "Invalid email or password", gr.update(visible=True), gr.update(visible=False)

def handle_logout():
    global logged_in_email
    logged_in_email = None
    return gr.update(visible=True), gr.update(visible=False)

def handle_signup(name, email, password):
    global logged_in_email
    logger.info(f"Attempting to sign up with: {name}, {email}")
    # Hash the password before saving for security
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password
    }

    try:
        # Insert login data into the login table
        insert_login(user_data)
        logged_in_email = email  # Set the email globally
        return gr.update(visible=False), gr.update(visible=True)
    except Exception as e:
        return gr.update(visible=True), gr.update(visible=False)


def handle_profile_submission(email, age, sex, weight, height, activity_level, goal, health, food):
    # Save profile to database
    user_data = {
        "age": age,
        "sex":sex,
        "weight": weight,
        "height": height,
        "activity_level": activity_level,
        "goal": goal,
        "health":health,
        "food": food
    }
    # Insert profile data into the user_info table, using the email from the login table
    success, message = insert_user(user_data, email)
    return gr.update(visible=False), gr.update(visible=True)


def submit_health_log(email, daily_bp, daily_food):
    """
    Submits the health log for the logged-in user.
    """
    success, message = insert_log(email, daily_bp, daily_food)
    if success:
        return f"Log submitted successfully for {email}!\nMorning BP: {daily_bp}\nFood: {daily_food}"
    else:
        return f"Failed to submit log: {message}"

def submit_and_close(daily_bp, daily_food):
    submit_health_log(logged_in_email, daily_bp, daily_food)
    return gr.update(visible=False)    

# def summarize_user_data(user_info, log_info):
#     bmi, activity_level, goal, food_habits = user_info
#     log_date, bp, recent_food = log_info

#     summary = f"User Profile: BMI= {bmi} Activity Level= {activity_level}, Goal of the user is= {goal}, Food Habits: {food_habits}\n"
#     summary += f"Meal and Blood Pressure on ({log_date}): BP: {bp}, Meal: {recent_food}"
#     return summary

def main():
    with gr.Blocks() as app:
        # Login Page (First Page)
        with gr.Column(visible=True, elem_classes='login_page') as login_page:
            gr.HTML("""
                <div style="text-align: center; padding-top: 150px;">
                    <h2>Welcome to DigiDiet! Please Log In</h2>
                    <p>Enter your email and password to log in:</p>
                </div>
            """)
            email = gr.Textbox(label="Email", placeholder="Enter your email address")
            password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
            login_button = gr.Button("Log In")
            login_status = gr.Label(
                value="Not Registered? Sign up Now!",
                show_label=False, 
                elem_classes="label-status",
            )
            signup_button1 = gr.Button("Sign Up")
        
        # Signup Page (Second Page)
        with gr.Column(visible=False, elem_classes='signup_page') as signup_page:
            gr.HTML("""
                <div style="text-align: center; padding-top: 150px;">
                    <h2>Welcome to DigiDiet! Please Sign Up</h2>
                    <p>Enter your details to create an account:</p>
                </div>
            """)
            name = gr.Textbox(label="Name", placeholder="Enter your full name")
            email_signup = gr.Textbox(label="Email", placeholder="Enter your email address")
            password_signup = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
            signup_button = gr.Button("Sign Up")
            back_to_login_button = gr.Button("Back to Login")

        # Profile Page (Third Page)
        with gr.Column(visible=False, elem_classes='profile_page') as profile_page:
            age = gr.Number(label="Age")
            sex= gr.Dropdown(['Male','Female','Choose Not to Reveal'],label='Sex')
            weight = gr.Number(label="Weight (kg)")
            height = gr.Number(label="Height (cm)")
            activity_level = gr.Dropdown(['sedentary','lightly_active','moderately_active','very_active','super_active'],label="Activity Level")
            goal = gr.Textbox(label="Goal (e.g., weight loss, muscle gain)")
            health = gr.TextArea(label="Input health conditions like Diabetes/ Blood Pressure")
            food = gr.TextArea(label="Mention the food items you like or you generally have")
            submit_button = gr.Button("Submit Profile")
            
        # Chatbot Page
        with gr.Column(visible=False, elem_classes='chatbot_page') as chatbot_page:
            chat_interface = gr.ChatInterface(
                fn=get_response,
                title="Fitness Agent",
                description=(
                    "Welcome to **Fitness Agent**, your AI-powered virtual coach! 🏋️‍♂️\n\n"
                    # "👋 **What can you ask?**\n"
                    # " - Personalized workout routines\n"
                    # " - Nutrition and meal planning\n"
                    # " - Fitness advice and tips\n\n"
                    "🤖 Start your fitness journey today!"
                ),
                theme="compact",
                examples=[
                    "How many calories should I eat to lose weight?",
                    "What are the best exercises for me to build muscle?",
                    "Can you create a weekly workout plan?",
                    "What foods should I avoid for better health?",
                ]
            )
            
            # Log Button and Health Log Modal (no changes here)
            with gr.Column(elem_classes="log-button-container"):
                log_button = gr.Button("Log Health Data", elem_classes="button secondary-button")
            
            with Modal(visible=False, elem_classes='health_log_modal') as health_log_modal:
                gr.Markdown("## Daily Health Log")
                
                with gr.Tab("Daily Log"):
                    daily_bp = gr.Textbox(label="Blood Pressure", placeholder="e.g., 120/80")
                    daily_food = gr.Textbox(label="Food Intake", placeholder="Describe your breakfast")
                
                modal_close = gr.Button("Close", visible=False)
                submit_log = gr.Button("Submit Log", elem_classes="button primary-button")
            
            submit_log.click(
                fn=submit_and_close,
                inputs=[daily_bp, daily_food],
                outputs=[health_log_modal]
            )

        # Button click logic for transitioning between pages
        login_button.click(
            fn=handle_login,
            inputs=[email, password],
            outputs=[login_status, login_page, chatbot_page]
        )
        signup_button1.click(
        fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
        outputs=[login_page, signup_page]
    )
        back_to_login_button.click(
        fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[login_page, signup_page]
    )
        signup_button.click(
            fn=handle_signup,
            inputs=[name, email_signup, password_signup],
            outputs=[signup_page, profile_page]
        )

        submit_button.click(
            fn=lambda age,sex, weight, height, activity_level, goal, health, food: handle_profile_submission(
                logged_in_email, age, sex, weight, height, activity_level, goal, health, food
            ),
            inputs=[age, sex, weight, height, activity_level, goal, health, food],
            outputs=[profile_page, chatbot_page]
        )

        log_button.click(lambda: Modal(visible=True), None, health_log_modal)
        gr.HTML("""
            <style>
            .gradio-container-5-7-1{
                background-color: floralwhite;
                # align-items: center;
            }
            .label-status .output-class{
                font-weight:light !important;
                font-size: 14px !important;
                padding: 0 !important;
            }
            .login_page, .signup_page, .profile_page{
                margin: 0 auto;
                width: 50% !important;
            }
            .chatbot_page .examples{
                position: absolute;
                bottom: 0;
            }
            .chatbot_page{
                width:90% !important;
                margin: 0 auto;
            }
            .chatbot_page .block.svelte-hjh1qu.flex{
                height:450px !important;
            }
            footer.svelte-1rjryqp{
                display:none !important;
            }
            .health_log_modal .block{
                width: 600px !important;
            }
            .chatbot_page .block h1{
                background-color: wheat;
            }
            </style>
            """)

    app.launch()


if __name__ == "__main__":
    main()
