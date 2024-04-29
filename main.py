import serpapi
import logging
from datetime import datetime
from openai import OpenAI
import resend
import time

##load env vars or def here##
SERP_KEY = ""
OPENAI_KEY = ""
RESEND_KEY = ""
RESEND_EMAIL = ""
GOOGLE_PLACE_ID = ""
LLM = ""

##EMAIL##


##EMAIL##
##build hmtl from review##
def buildHMTL(reviewsDict):

    reviews_data = """
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Review Table</title>
        </head>
        <body>
    """

    consultation_counter = 0

    for review in reviewsDict:
        if "extracted_snippet" in review:
            snippet = review["extracted_snippet"]["original"]
        else:
            snippet = "Sin descripción"

        detailsText = ""

        if "details" in review:
            details = review["details"]
            for key, value in details.items():
                detailsText += "<strong>{}:</strong> {} - ".format(key, value)
        else:
            detailsText = "Sin detalles"

        raw_date = review["iso_date"]
        date_obj = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
        review["iso_date"] = date_obj.strftime("%Y-%m-%d")

        reviews_data += """
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px; font-family: Arial, sans-serif;">
            <thead style="background-color: #f2f2f2;">
                <tr>
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 10px; color: #333;">Usuario</th>
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 10px; color: #333;">Fecha</th>
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 10px; color: #333;">Reseña</th>
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 10px; color: #333;">Detalles</th>
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 10px; color: #333;">Rating</th>
                    <th style="border: 1px solid #dddddd; text-align: left; padding: 10px; color: #333;">Enlace</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 10px;">{}</td>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 10px;">{}</td>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 10px;">{}</td>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 10px;">{}</td>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 10px;">{}</td>
                    <td style="border: 1px solid #dddddd; text-align: left; padding: 10px;"><a href="{}" style="color: #007bff; text-decoration: none;">Link</a></td>
                </tr>
            </tbody>
        </table>
        """.format(
            review["user"]["name"].upper(),
            review["iso_date"],
            snippet,
            detailsText.replace("_", " "),
            review["rating"],
            review["link"],
        )

        print("Review Rating: {}".format(review["rating"]))

        if float(review["rating"]) <= 4.0:
            reviews_data += "<h2><strong>Evita estas reseñas:</strong></h2>"
            if "extracted_snippet" in review:
                if consultation_counter >= 3:
                    print(
                        "Fetch Limit reached for AI, sleeping 60 seconds before next fetch..."
                    )
                    time.sleep(60)
                    consultation_counter = 1
                advice = aiAdvice(review["extracted_snippet"]["original"])
                consultation_counter += 1
                reviews_data += "<p>{}</p>".format(advice)
            else:
                reviews_data += "<p>Sin Detalles</p>"

    reviews_data += """
        </body>
    </html>
    """
    return reviews_data


##filter reviews##
def filterReviews(reviewsDict):  # Define a function to filter reviews
    filteredData = []  # Initialize an empty list to store filtered data
    today = datetime.today().strftime(
        "%Y-%m-%d"
    )  # Get today's date in the format YYYY-MM-DD
    print(
        "Checking for reviews from: {}".format(today)
    )  # Print a message indicating what we're doing

    for review in reviewsDict:  # Iterate over each review in the input dictionary
        raw_date = review["iso_date"]  # Extract the ISO-formatted date from the review
        date_obj = datetime.strptime(
            raw_date, "%Y-%m-%dT%H:%M:%SZ"
        )  # Convert the ISO date to a Python datetime object
        formatted_date = date_obj.strftime(
            "%Y-%m-%d"
        )  # Format the datetime object as YYYY-MM-DD

        if formatted_date == today:  # Check if the review's date matches today's date
            filteredData.append(
                review
            )  # If it does, add the review to our filtered data list

    return filteredData  # Return the filtered list of reviews


##fetch reviews##
def fetchReviews():
    logging.basicConfig(level=logging.INFO)  # Configuring logging

    serp_client = serpapi.Client(api_key=SERP_KEY)
    search_params = {
        "engine": "google_maps_reviews",
        "place_id": GOOGLE_PLACE_ID,
        "hl": "es",
        "sort_by": "newestFirst",
    }

    try:
        results = serp_client.search(params=search_params)
        logging.info("Reviews Fetched")
        # print(results["reviews"])
        return results["reviews"]

    except Exception as e:
        logging.error("Error while fetching reviews. Err: %s", e)
        return None  # Or raise an exception if appropriate


##AI Consultation##
def aiAdvice(reviewText):
    logging.basicConfig(level=logging.INFO)  # Configuring logging
    openai_client = OpenAI(api_key=OPENAI_KEY)
    helperContent = """
    Your task is to be an expert in providing advice on preventing negative reviews for my restaurant.
    I'll share the text of the negative review, and I'd like you to analyze it and offer actionable
    suggestions. Please note that empathy is not necessary; I'm solely interested in receiving clear
    advice. As the reviews may be in various languages, please consider the customer's cultural
    background when giving suggestions. All advice should be provided in Spanish-Latino."
    """

    try:
        response = openai_client.chat.completions.create(
            model=LLM,
            messages=[
                {"role": "system", "content": helperContent},
                {"role": "user", "content": reviewText},
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error("Error while fetching AI advice: {}".format(e))
        return "Error Fetching AI advice - Unknown Error"


##send email##
def sendMail(content):
    logging.basicConfig(level=logging.INFO)  # Configuring logging
    resend.api_key = RESEND_KEY
    params = {
        "from": "REVIEWS BOT <onboarding@resend.dev>",
        "to": [RESEND_EMAIL],
        "subject": "Reviews",
        "html": content,
    }

    try:
        resend.Emails.send(params)
        return None

    except Exception as e:
        logging.error("Error sending email: {}".format(e))
        return None


##Main##
def main():
    print("Starting to Fetch for reviews.")
    # fetch reviews#
    reviews_dictionary = fetchReviews()

    filtered_data = filterReviews(reviewsDict=reviews_dictionary)
    email_html = ""
    # if fetching reviews returns any relevant reviews or not #
    if filtered_data == []:
        print("No reviews today...")
        email_html = """
        <h1>Nada por ahora!</h1>
        """
    else:
        email_html = buildHMTL(reviewsDict=filtered_data)

    # sendEmail(content)
    sendMail(email_html)
    print("Today's email has been sent!")


if __name__ == "__main__":
    main()
