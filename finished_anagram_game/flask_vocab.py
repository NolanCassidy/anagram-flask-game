"""
Flask web site with vocabulary matching game
(identify vocabulary words that can be made 
from a scrambled string)
"""

import flask
import logging

# Our own modules
from letterbag import LetterBag
from vocab import Vocab
from jumble import jumbled
import config

###
# Globals
###
app = flask.Flask(__name__)

CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY  # Should allow using session variables

#
# One shared 'Vocab' object, read-only after initialization,
# shared by all threads and instances.  Otherwise we would have to
# store it in the browser and transmit it on each request/response cycle,
# or else read it from the file on each request/responce cycle,
# neither of which would be suitable for responding keystroke by keystroke.

WORDS = Vocab(CONFIG.VOCAB)

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    """The main page of the application"""
    flask.g.vocab = WORDS.as_list()                     # Create a global var with all the words in it
    flask.session["target_count"] = min(                # Create a session variable called target_count and store it with the number of correct answers the user must get (defined in credentials.ini)
        len(flask.g.vocab), CONFIG.SUCCESS_AT_COUNT)    # Retrieve the success count value. If the number of words in the list is less than that value, use the number of words instead
    flask.session["jumble"] = jumbled(                  # Creat an anagram that scrambles 'target_count' number of words together from the word list
        flask.g.vocab, flask.session["target_count"])
    flask.session["matches"] = []                       # Define an empty veriable to store the matches once we have them
    flask.session["input_letters"] = []                 # Define an empty veriable to store the letters in #attempt
    app.logger.debug("Session variables have been set") 
    assert flask.session["matches"] == []
    assert flask.session["target_count"] > 0
    app.logger.debug("At least one seems to be set correctly")
    return flask.render_template('vocab.html')


@app.route("/keep_going")
def keep_going():
    """
    After initial use of index, we keep the same scrambled
    word and try to get more matches
    """
    flask.g.vocab = WORDS.as_list()
    return flask.render_template('vocab.html')


@app.route("/success")
def success():
    return flask.render_template('success.html')


###############
# AJAX request handlers
#   These return JSON, rather than rendering pages.
###############

@app.route("/_check")
def check():
    app.logger.debug("Entering AJAX check")
    text = flask.request.args.get("text", type=str)         # Get the text provided from vocab.html where check was called
    jumble = flask.session["jumble"]                        # Set jumble equal to the anagram from the session value jumble
    matches = flask.session.get("matches", [])              # Set matches to the empty session value for matches
    flask.session["input_letters"] = text                   # Update the session variable input_letters with the local one
    next_url = 0                                            # Default case where the user still needs to get more matches and the current word is not a match
    # Check if input letter is valid
    input_key = text[(len(text)-1)]                         # Most recent letter pressed
    valid_key = LetterBag(jumble).contains(input_key)       # valid_key is a bool that tells us if the key the user just pressed is in the anagram
    if not valid_key:                                       # If the key the user input isn't in the anagram
        next_url = 1                                        # Code for html to "undo" that keystroke
    # Check if the input was already used
    txt_instances = jumble_instances = 0;                   # Number of times the new key is present in txt and in jumble
    for letter in text:
        if letter == input_key:
            txt_instances += 1                              # Should be >0
    for letter in jumble:
        if letter == input_key:
            jumble_instances += 1                           # Should be >0
    if txt_instances > jumble_instances:                    # The letter has been used more times than it exists in jumble
        if next_url == 0:                                   # The letter was in the jumble
        	next_url = 1
    # Is it good?
    in_jumble = LetterBag(jumble).contains(text)            # in_jumble is a bool that tells us if the text the user entered is in the anagram
    matched = WORDS.has(text)                               # matched is a bool that tells us if text is in the words list
    # Respond appropriately
    if matched and in_jumble and not (text in matches):     # Cool, they found a new word
        matches.append(text)                                # Add text to the local matches variable
        flask.session["matches"] = matches                  # Update the session variable matches with the local one
        next_url = flask.url_for("keep_going")              # Set next
    # Choose page:  Solved enough, or keep going?
    if len(matches) >= flask.session["target_count"]:       # If you have as many matches as defined by your target_count
       next_url = flask.url_for("success")                  # Define the target url as success
    rslt = {"new_url": next_url}                            # Define a list to for the return data
    return flask.jsonify(result=rslt)                       # Send the data back to vocab.html


#################
# Functions used within the templates
#################

@app.template_filter('filt')
def format_filt(something):
    """
    Example of a filter that can be used within
    the Jinja2 code
    """
    return "Not what you asked for"

###################
#   Error handlers
###################


@app.errorhandler(404)
def error_404(e):
    app.logger.warning("++ 404 error: {}".format(e))
    return flask.render_template('404.html'), 404


@app.errorhandler(500)
def error_500(e):
    app.logger.warning("++ 500 error: {}".format(e))
    assert not True  # I want to invoke the debugger
    return flask.render_template('500.html'), 500


@app.errorhandler(403)
def error_403(e):
    app.logger.warning("++ 403 error: {}".format(e))
    return flask.render_template('403.html'), 403


####

if __name__ == "__main__":
    if CONFIG.DEBUG:
        app.debug = True
        app.logger.setLevel(logging.DEBUG)
        app.logger.info(
            "Opening for global access on port {}".format(CONFIG.PORT))
        app.run(port=CONFIG.PORT, host="0.0.0.0")
