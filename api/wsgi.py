from mainapp.app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
    #api.run(threaded=True, debug=True)
