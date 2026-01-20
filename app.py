# importing necessary libraries
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
# Flask and socketio are used to make websites and make it real time(so that they can take up and updat instant changes)
from flask_sqlalchemy import SQLAlchemy
# SQLAlchemy: used to talk to database
from datetime import datetime
# datetime is used to record the time when token is generated and added to queue.
# calculates tentaive time for each next token and also display the join time of each token in queue.
import os
#initialise app and socket io
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# basedir: holds the full path to the directory where your Python script
basedir = os.path.abspath(os.path.dirname(__file__))

# 2. Tell Flask to create queue.db exactly in that folder
# file 'queue.db' stores and keeps track record of real time updates of tokens being generated
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'queue.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initializes the SQLAlchemy database instance, connecting it to the Flask app....for interacting with database
db = SQLAlchemy(app)
socketio = SocketIO(app)
# Initializes the Flask-SocketIO extension, enabling real-time communication.
# --- Token content
# In Full Stack, you define what your data looks like in the DB
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    join_time = db.Column(db.String(20), nullable=False)
    is_urgent = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="waiting")  # waiting, serving, done

#creating the database file if it doesn't exist
with app.app_context():
    db.create_all()

# --- AI CORE  ---
class AICore:
    def check_priority(self, reason_text):
        urgent_keywords = ['emergency', 'urgent', 'critical', 'severe']
        if any(word in reason_text.lower() for word in urgent_keywords):
            return True
        return False
        # NLP LOGIC: Scans the input for keywords to decide priority.If it finds 'emergency' or 'urgent', it returns True.
        # Convert text to lowercase to match 'Emergency' or 'emergency'
    def calculate_wait_time(self, is_priority, queue_count):
        if is_priority:
            return 0
        return (queue_count * 5) + 5
    # if priority is true and one of the words from urgent_keywords has been used than wait time becomes 0 making the system treat them as a priority
    # Normal Logic: the queue length and 5 minutes per person
    """
    REGRESSION LOGIC: Calculates time based on queue length.
    If priority is True, wait time is 0.
    """
ai_core = AICore()


# --- ROUTES ---used to get user and admin view
@app.route('/')
def user_view():
    return render_template('user.html')

@app.route('/admin')
def admin_view():
    return render_template('admin.html')

# --- API ENDPOINTS ---

@app.route('/get_token', methods=['POST'])
def get_token():
    name = request.form.get('name')
    visit_reason = request.form.get('reason')
    # receives data from user end...name and reason and checks the urgency condition
    # AI Logic:  ai asks for urgnet keywords and how long is it suppose to wait
    is_urgent = ai_core.check_priority(visit_reason)
    # Count how many are waiting in DB
    # if its urgent we apply function check_priority from class aicore
    # if not urgent than we use function calculate_wait_time from class ai_core
    queue_count = Token.query.filter_by(status='waiting').count()
    wait_time = ai_core.calculate_wait_time(is_urgent, queue_count)
    # Save to Database (Persist Data)
    new_token = Token(
        name=name,
        reason=visit_reason,
        join_time=datetime.now().strftime("%H:%M:%S"),
        is_urgent=is_urgent,
        status="waiting"
    )
    db.session.add(new_token)
    db.session.commit()  # Commits change to queue.db file

    # Data for User...user visibility
    response_data = {
        'id': new_token.id,
        'estimated_wait': wait_time
    }

    update_all_clients()
    return jsonify(response_data)

@app.route('/next_token', methods=['POST'])
def next_token():
    # Logic: Find someone "serving" and mark them "done"
    current_serving = Token.query.filter_by(status='serving').first()
    if current_serving:
        current_serving.status = 'done'
        db.session.commit()

    # Find next person
    # If priority exists, get them first. If not, get by ID (FIFO)
    urgent_next = Token.query.filter_by(status='waiting', is_urgent=True).order_by(Token.id).first()

    if urgent_next:
        next_person = urgent_next
        # assigning immediately token 0

    else:
        # assign according to priority list 5 mins from the last token
        next_person = Token.query.filter_by(status='waiting').order_by(Token.id).first()

    if next_person:
        next_person.status = 'serving'
        db.session.commit()
        # next_person's status updated to serving
        # Convert DB object to Dictionary for JSON response
        person_dict = {
            'id': next_person.id,
            'name': next_person.name,
            'reason': next_person.reason
        }
        update_all_clients()
        return jsonify({'status': 'success', 'serving': person_dict}) # json response if the queue still has people
    else:
        update_all_clients()
        return jsonify({'status': 'empty'}) # json response if there is no one remaining in the queue
# REAL-TIME UPDATES public announcement system
def update_all_clients():
    # 1. Waiting Counts & List
    queue_count = Token.query.filter_by(status='waiting').count()
    waiting_list_objs = Token.query.filter_by(status='waiting').order_by(Token.is_urgent.desc(), Token.id).all()
    waiting_list = [{'id': t.id, 'name': t.name, 'join_time': t.join_time, 'urgent': t.is_urgent} for t in
                    waiting_list_objs]

    # 2. Currently Serving
    serving_person = Token.query.filter_by(status='serving').first()

    # 3. Recently Done (New Logic) - Get the last 10 finished people
    # We send this so their phones know to show the "Thank You" message
    done_objs = Token.query.filter_by(status='done').order_by(Token.id.desc()).limit(10).all()
    done_list = [t.id for t in done_objs]

    data = {
        'queue_length': queue_count,
        'current_serving': serving_person.id if serving_person else "None",
        'queue_list': waiting_list,
        'done_list': done_list  # <--- Sending this to the frontend
    }
    socketio.emit('queue_update', data)
    # data is the packet information that is been sent and emit means to broadcast
if __name__ == '__main__': # verifies that script is the main entry point
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
    # socketio.run(app, ...) starting the socket server which handles websocket connections and http requests
    # debug=true...enables easy developing and dugging
    #  allow_unsafe_werkzeug=True...allows development server to run even if its not secure
