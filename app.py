from flask import Flask, request, render_template, redirect, flash, session
from surveys import satisfaction_survey, surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "skey000"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True 
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['FLASK_DEBUG'] = True
app.config['FLASK_ENV'] = 'development'
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():    
    survey = surveys['satisfaction']
    session['responses'] = []
    return render_template('index.html', question_num=0, survey=survey)
 
@app.route('/question/<int:question_num>', methods=['GET', 'POST'])
def show_question(question_num):
    survey = surveys['satisfaction']
    responses = session.get('responses', [])

    if len(responses) == len(survey.questions):
        # If all questions have been answered, redirect to thank you page
        return redirect('/thanks')
    
    if question_num != len(responses):
        # If the user tries to access a question out of order, redirect to the appropriate question
        flash("We'd prefer you to take the survey in a linear fashion.")
        return redirect(f"/question/{len(responses)}")
    
    question = survey.questions[question_num]
    
    if request.method == 'POST':
        # Check if a choice has been selected
        choice = request.form.get('choice')
        if not choice:
            flash('Please select an answer before submitting.')
            return redirect(f'/question/{question_num}')
        
        # Save the response and redirect to the next question or the thank you page
        responses.append(choice)
        session['responses'] = responses
        
        if len(responses) == len(survey.questions):
            # If the user has answered all of the questions, redirect to the thank you page
            return redirect('/thanks')
        else:
            next_question_num = question_num + 1
            return redirect(f"/question/{next_question_num}")

    return render_template('question.html', question=question, question_num=question_num, survey=survey)
  
@app.route('/answer', methods=['POST'])
def handle_answer():
    # get the current question number from the form data
    question_num = int(request.form['question_num'])
    
    # get the selected answer from the form data
    answer = request.form.get('choice')
    if answer is None:
        flash('Please select an answer before submitting.')
        return redirect(f'/question/{question_num}')
    
    # get the survey object
    survey = surveys['satisfaction']

    # add the answer to the list of responses
    # responses.append(answer)
    responses = session.get('responses', [])
    responses.append(answer)
    session['responses'] = responses
    
    # check if there are more questions
    if question_num < len(survey.questions) - 1:
        # if there are more questions, redirect to the next question's URL
        next_question_num = question_num + 1
        return redirect(f'/question/{next_question_num}')
    else:
        # if there are no more questions, redirect to the survey complete page
        return redirect('/complete')


@app.route('/complete')
def complete():
    return render_template('complete.html', survey=surveys['satisfaction'], responses=session['responses'])


@app.route('/session', methods=['POST'])
def reset_session():
    session['responses'] = []
    flash('Survey session reset.')
    return redirect('/')


if __name__ == '__main__':
    app.run()

 