from flask import Flask, render_template, redirect, request, jsonify
from flask import session as b_session
import model
import json
import ast
import correlation

app = Flask(__name__)

app.secret_key = 'a4c96d59-57a8-11e4-8b97-80e6501ee2f6'

@app.route("/")
def welcome():
    # render the welcome html, which offers log in or sign up buttons
    return render_template("welcome.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

#function to create new user
@app.route("/new-user", methods=['POST'])
def create_new_user():

    email = request.form.get("new-user-email")
    pw = request.form.get("new-user-pw")
    age = request.form.get("new-user-age")
    zipcode = request.form.get("new-user-zipcode")
    ## check for validity of information passed into the form
    print 'new user:', email, pw, zipcode, age
    ## updating the database
    user = model.User(email=email, password=pw, age=age, zipcode=zipcode)
    model.session.add(user)
    model.session.commit()

    return "/index.html"

@app.route("/log-in", methods=['POST'])
def log_in():

    email = request.form.get("user-email")
    pw = request.form.get("user-pw")
    print 'log in request for:', email, pw

    query = model.session.query(model.User).filter_by(email=email).one()
    if query.password == pw:
        b_session.setdefault("user", {}) #if there is no user key yet, add one
        if query.id not in b_session["user"]: #if name is not in session already
            b_session["user"] = query.id #puts in the session
        return json.dumps({ "result": "/index.html" })

    return json.dumps({ "error": "try again"})

@app.route("/get-user-ratings")
def get_user_ratings(id = None):
    id = request.args.get("id")
    if id == None:
        id = b_session["user"]

    rating_object = model.session.query(model.Rating).filter_by(user_id=id).all()
    ratings_list = {}

    for rating in rating_object:
        ratings_list[rating.movie.name] = [rating.rating, rating.movie_id]

    return jsonify(**ratings_list) ## JSONIFY!!!

@app.route("/get-user-list")
def get_user_list():

    user_list = model.session.query(model.User).limit(20).all()
    user_dict = {'users': []}

    for user in user_list:
        # user_dict[str(user.id)] = "name"
        user_dict['users'].append(user.id)

    print user_dict
    return jsonify(**user_dict)

@app.route("/update_ratings", methods=['POST'])
def update_ratings():

    updates_dict = ast.literal_eval(request.form.get("updates")) #DICTIFY!!!!

    for movie_id, updated_rating in updates_dict.iteritems():
        query = model.session.query(model.Rating).filter_by(user_id=b_session["user"], movie_id=movie_id).one()
        print "old rating", query.rating
        query.rating = updated_rating
        print "new rating", query.rating
    model.session.commit()
    
    return  json.dumps({ "success": "all movie ratings were updated" })

@app.route("/log-out", methods=['POST'])
def log_out():

    b_session["user"] = {}
    return "/"

@app.route("/movie", methods=["GET"])
def view_movie():

    id = request.args.get("id")
    print "this is for id: ", id

    movie = model.session.query(model.Movie).get(id)

    print "movie obj: ", movie

    ratings = movie.ratings
    rating_nums = []
    
    # print "ratings: ", ratings

    user_rating = None
    for r in ratings:
        if r.user_id == b_session['user']:
            user_rating = r
        rating_nums.append(r.rating)
    avg_rating = float(sum(rating_nums))/len(rating_nums)
    print "avg rating is: ", avg_rating
    print "user rating obj is: ", user_rating
    # print "user rating is: ", user_rating.rating

    user = model.session.query(model.User).get(b_session['user'])

    print "we have a user", user

    prediction = None
    if not user_rating:
        prediction = user.predict_rating(movie)
        effective_rating = prediction
    else:
        effective_rating = user_rating.rating

    print "prediction is: ", prediction
    print "effective rating is: ", effective_rating

    the_eye = model.session.query(model.User).filter_by(email="theeye@ofjudgement.com").one()
    eye_rating = model.session.query(model.Rating).filter_by(user_id=the_eye.id, movie_id=movie.id).first()
    print "the_eye object:", the_eye
    print "eye rating object is: ", eye_rating
    print "the eye's prediction of movie rating", the_eye.predict_rating(movie)

    if not eye_rating:
        print "THERE IS NO EYE RATING"
        eye_rating = the_eye.predict_rating(movie) # returns None because no similarities
    else:
        eye_rating = eye_rating.rating

    print " eye rating: ", eye_rating
    print "effective rating: ", effective_rating

    difference = abs(eye_rating - effective_rating)
    print "difference", difference

    messages = [ "I suppose you don't have such bad taste after all.",
             "I regret every decision that I've ever made that has brought me to listen to your opinion.",
             "Words fail me, as your taste in movies has clearly failed you.",
             "That movie is great. For a clown to watch. Idiot.", ]

    beratement = messages[int(difference)]
    print "beratement: ", beratement

    # End prediction
    # create a list, jsonify it, and return it to the get requester
    results = {
        'movie id': movie.id,
        'avg rating': avg_rating,
        'user rating': None,
        'prediction': prediction,
        'beratement': beratement,
        'movie title': movie.name
        }
    if user_rating:
        results['user rating'] = user_rating.rating

    print "RESULTS", results
    return jsonify(**results)

    # return render_template("movie.html", movie=movie, 
    #         average=avg_rating, user_rating=user_rating,
    #         prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)

