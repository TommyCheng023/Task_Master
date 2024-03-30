from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__) # reference to the file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # tell the app where our database is located
db = SQLAlchemy(app) # initialize the database


class Todo(db.Model):
    """
        Create a model for the database.
    """
    id = db.Column(db.Integer, primary_key=True) # an integer, make every id be unique by setting `primary_key` to True
    content = db.Column(db.String(200), nullable=False) # a string that cannot be blank, and has a maximum limit of 200 characters
    date_created = db.Column(db.DateTime, default=datetime.utcnow) # import datetime dependence

    def __repr__(self):
        """
            Tell what should be returned every time when a new element is created.
            return: <Task id>
        """
        return '<Task %r>' % self.id  # `%r` acts like a placeholder.
    
with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    # do different actions based on the request type
    if request.method == 'POST':
        task_content = request.form['content'] # the name of the form is set to `content`, check it in `index.html`
        new_task = Todo(content=task_content) # create a Todo object that is prepared to be pushed to the database

        # push to the database
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/') # redirect() helps send us back to the index page
        except:
            return "An issue happens when adding the task."
        
    else:
        tasks = Todo.query.order_by(Todo.date_created).all() # look at all the database contents in the order they were created and return all of them
        recent = Todo.query.order_by(Todo.date_created).first() # first() grabs the most recent one based on this order
        return render_template('index.html', tasks=tasks) # pass in `tasks` and store as a parameter, now view it in `index.html`

# fetch id, which is a unique element for every task, direct url to the specific task
@app.route('/delete/<int:id>')
def delete(id):
    """
        Delete the task based on the passed in `id` parameter.
    """
    task_to_delete = Todo.query.get_or_404(id)  # attempt to get the object by ID, returns 404 otherwise
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Failed to delete."
    # Once the function is completed at this point, update `index.html` by setting delete to the correct `href`.

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    """
        Update the task based on the passed in `id` parameter.
    """
    task = Todo.query.get_or_404(id) # create a `task` variable that is needed for update page

    if request.method == 'POST':
        # update logic here
        task.content = request.form['content'] # set content to the content in this form
        try:
            db.session.commit()  # nothing to add, since changes have made already
            return redirect('/') # send the user back to the home page
        except:
            return "Commit failed. :("
    else:
        return render_template('update.html', task=task)

# run the app
if __name__ == "__main__":
    app.run(debug=True)