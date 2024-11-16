from app import app


@app.route("/")
@app.route("/index")
def index():
    user = {"username": "Sakhile"}
    return (
        """
        <html>
            <head>
                <title>Home Page - Flask Chronicles</title>
            </head>
            <body>
                <h1>Hello, """
                + user["username"]
                + """!</h1>
            </body>
        </html>
    """
    )
