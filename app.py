from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    

# Poll model 
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100), nullable=False)
    options = db.relationship('PollOption', backref='poll', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Poll {self.id}>'
    
    
# PollOption model
class PollOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    option_text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<PollOption {self.id}>'
    

# ROUTES FOR REGISTER USER
@app.route('/register', methods=['POST'])
def register():
    user_data = request.json  
    # Validate required fields
    if 'username' not in user_data or 'password' not in user_data or 'email' not in user_data:
        return jsonify({'error': 'Missing required fields'})
    
    user = User(
        username=user_data['username'],
        password=user_data['password'],
        email=user_data['email']
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'})


#ROUTES FOR LOGIN USER
@app.route('/login', methods=['POST'])
def login():
    user_data = request.json  
    # Validate required fields
    if 'username' not in user_data or 'password' not in user_data:
        return jsonify({'error': 'Missing required fields'})

    # Find the user by username
    user = User.query.filter_by(username=user_data['username']).first()
    if user and user.password == user_data['password']:
        return jsonify({'message': 'User logged in successfully'})
    else:
        return jsonify({'error': 'Invalid credentials'})
    

# ROUTES FOR USER LIST
@app.route('/user/list', methods=['GET'])
def list_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify({'users': user_list})


#ROUTES FOR GET THE USER BY ID
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        user_data = {'id': user.id, 'username': user.username, 'email': user.email}
        return jsonify({'user': user_data})
    else:
        return jsonify({'error': 'User not found'})
    

#ROUTES FOR DELETE THE USER BY ID
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    else:
        return jsonify({'error': 'User not found'})
    

#ROUTES FOR UPDATE THE USER BY ID
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_data = request.json
    # Update user fields if provided
    if 'username' in user_data:
        user.username = user_data['username']
    if 'password' in user_data:
        user.password = user_data['password']
    if 'email' in user_data:
        user.email = user_data['email']

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})


# ROUTES FOR ADD THE POLL
@app.route('/poll/add', methods=['POST'])
def add_poll():
    poll_data = request.json
    # Validate required fields
    if 'question' not in poll_data or 'options' not in poll_data:
        return jsonify({'error': 'Missing required fields'}), 400

    question = poll_data['question']
    options = poll_data['options']
    
    # Create poll
    poll = Poll(question=question)
    db.session.add(poll)
    db.session.commit()

    # Create poll options
    for option_text in options:
        poll_option = PollOption(poll=poll, option_text=option_text)
        db.session.add(poll_option)
    
    db.session.commit()

    return jsonify({'message': 'Poll added successfully'})


# ROUTES FOR GET THE POLL LIST
@app.route('/poll/list', methods=['GET'])
def list_polls():
    polls = Poll.query.all()
    poll_list = [{'id': poll.id, 'question': poll.question} for poll in polls]
    return jsonify({'polls': poll_list})


#ROUTES FOR GET THE POLL BY ID
@app.route('/poll/<id>', methods=['GET'])
def get_poll(id):
    poll = Poll.query.get(id)
    if poll:
        poll_data = {'id': poll.id, 'question': poll.question, 'options': []}
        for option in poll.options:
            poll_data['options'].append({'id': option.id, 'option_text': option.option_text, 'votes': option.votes})
        return jsonify({'poll': poll_data})
    else:
        return jsonify({'error': 'Poll not found'})
    

#ROUTES FOR UPDATE THE POLL BY ID
@app.route('/poll/<id>', methods=['PUT'])
def update_poll(id):
    poll = Poll.query.get(id)
    if not poll:
        return jsonify({'error': 'Poll not found'}), 404

    poll_data = request.json
    # Update poll fields if provided
    if 'question' in poll_data:
        poll.question = poll_data['question']

    db.session.commit()
    return jsonify({'message': 'Poll updated successfully'})


#ROUTES FOR DELETE THE POLL BY ID
@app.route('/poll/<id>', methods=['DELETE'])
def delete_poll(id):
    poll = Poll.query.get(id)
    if poll:
        db.session.delete(poll)
        db.session.commit()
        return jsonify({'message': 'Poll deleted successfully'})
    else:
        return jsonify({'error': 'Poll not found'})
    

# ROUTES FOR UPDATE THE POLL OPTION BY OPTION ID
@app.route('/poll/option/<option_id>', methods = ['PUT'])
def update_poll_options(option_id):
    poll_option = PollOption.query.get(option_id)
    if not poll_option:
        return jsonify({'message' : 'Poll option not Found'})
    
    option_data = request.json
    #Update the poll_option if provided 
    if 'option_text' in option_data:
        poll_option.option_text = option_data['option_text']
    
    db.session.commit()

    return jsonify({'message':'Poll Option updated successfully'})


# ROUTES FOR DELETE THE POLL OPTION BY OPTION ID
@app.route('/poll/option/<option_id>',methods = ['DELETE'])
def delete_poll_option(option_id):
    option = PollOption.query.get(option_id)
    if option:
        db.session.delete(option)
        db.session.commit()
        return jsonify({'message':'Poll Opton Delete successfully'})
    else:
        return jsonify({'error':'Poll Option Not Found'})
    
    
# ROUTES FOR VOTE THE POLL OPTION BY OPTION ID
@app.route('/poll/<poll_id>/option/<option_id>', methods=['POST'])
def vote_poll(poll_id, option_id):
    poll_option = PollOption.query.get(option_id)
    if not poll_option:
        return jsonify({'error': 'Poll option not found'}), 404

    poll_option.votes += 1
    db.session.commit()
    return jsonify({'message': 'Vote added successfully'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
