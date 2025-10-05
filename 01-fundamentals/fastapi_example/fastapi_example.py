import os

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": os.environ.get("NAME")}


# create a main function to run the app
def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
