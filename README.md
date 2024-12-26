Python Business Review Bot

This Python bot automates checking for new business reviews, filtering them for the latest updates, and sending a formatted email summary. For negative reviews, it leverages OpenAI's API to provide actionable advice, saving time and enhancing customer satisfaction.
Features

    Automatically fetches business reviews daily via SerpAPI.
    Filters reviews to display only today's updates.
    Formats reviews into an HTML table for easy readability.
    Analyzes negative reviews using OpenAI, generating actionable advice in Spanish.
    Sends a compiled email with reviews and insights.

Getting Started
Prerequisites

    Python 3.8+
    Install the required Python libraries:

    pip install serpapi openai resend

    Generate API keys for the following services:
        SerpAPI
        OpenAI
        Resend Email API

Environment Variables

Set up a .env file or define the following variables in your environment:

SERP_KEY=your_serpapi_key
OPENAI_KEY=your_openai_key
RESEND_KEY=your_resend_key
RESEND_EMAIL=recipient_email_address
GOOGLE_PLACE_ID=your_google_place_id
LLM=gpt-4

Running the Script

    Clone this repository:

git clone https://github.com/your_username/repo_name.git
cd repo_name

Ensure your environment variables are properly set.
Execute the script:

    python review_bot.py

How It Works

    Fetching Reviews: The bot retrieves reviews for the business using SerpAPI and Google Place ID.

    Filtering: Reviews are filtered to include only posts from the current day.

    HTML Formatting: A clean HTML table is generated, showing user details, date, rating, and comments.

    AI Analysis: Reviews with ratings of 4.0 or lower are analyzed using OpenAI, generating actionable advice in Spanish.

    Email Delivery: The bot compiles and sends the reviews and AI feedback via the Resend API.

Code Overview

    fetchReviews: Retrieves reviews from SerpAPI.
    filterReviews: Filters reviews based on the posting date.
    buildHTML: Creates a structured HTML table from the reviews.
    aiAdvice: Utilizes OpenAI to generate advice for negative feedback.
    sendMail: Sends the email with reviews and insights.

Example Output

The email includes:

    A table summarizing the latest reviews with user details, dates, ratings, and comments.
    Suggestions for addressing negative reviews if any are found.

Future Improvements

    Add support for multiple languages for OpenAI advice.
    Include a dashboard to view review trends over time.
    Provide sentiment analysis for all reviews, not just negative ones.
    Allow configuration of the threshold for "bad" reviews.

License

This project is licensed under the MIT License. See the LICENSE file for details.
Contributing

Feel free to open issues or submit pull requests if you have ideas for improvement.
Acknowledgments

Special thanks to my brother for inspiring this project by sharing the challenges businesses face with managing online reviews.
