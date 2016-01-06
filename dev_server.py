from os_api.app import create_app

app = create_app()

app.run(port=8000, debug=True)

