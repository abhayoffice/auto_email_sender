# # my_sentiment.py
# from transformers import pipeline
#
# # Load the sentiment analysis model
# sentiment_analyzer = pipeline("sentiment-analysis")
#
#
# def generate_reply(email_body):
#     # Analyze sentiment
#     result = sentiment_analyzer(email_body)
#
#     # Determine reply based on sentiment
#     sentiment = result[0]["label"]
#     if sentiment == "POSITIVE":
#         return "I'm happy to know that! Thank you for your positive feedback."
#     elif sentiment == "NEGATIVE":
#         return "I apologize for any inconvenience. We will address your concerns promptly."
#     else:
#         return "Thank you for reaching out. We appreciate your communication."
