from flask import Flask, request, render_template, send_file, Response
from flask_csv import send_csv
import pandas as pd
import openai

app = Flask(__name__)
openai.api_key = "PUT YOUR OPENAI API KEY HERE"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the uploaded file
        file = request.files["file"]

        # Use pandas to load the dataframe from the file
        df = pd.read_csv(file, header=0)

        #drop rows missing "Videos Transcript" column
        df = df[pd.notnull(df['Videos Transcript'])]

        #create a function for openAI while limiting the max cost per line to about 5 cents with max_tokens
        def generate_text(prompt):
            completions = openai.Completion.create(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=2500,
                n=1,
                stop=None,
                temperature=0.5,
            )
            message = completions.choices[0].text
            return message

        df = df.assign(Lesson_Plan=df['Videos Transcript'].apply(lambda x: generate_text("Create a lesson plan for this video transcript (which includes an aim, 3 to 4 learning objectives, anticipatory set, modeled practice, guided practice, independent practice, common areas of struggle, and closure): "+x)))
        df = df.assign(Comprehension_Questions=df['Videos Transcript'].apply(lambda x: generate_text("Create 4 comprehension questions for the transcript: "+x)))

        return Response(
            df.to_csv(header=True),
            mimetype="text/csv",
            headers={"Content-disposition":
            "attachment; filename=filename.csv"})

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
