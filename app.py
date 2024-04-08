import app

if __name__ == '__main__':

    app = app.create_app()
    app.secret_key = 'badguy'
    app.run(debug=True)

