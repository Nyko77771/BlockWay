
# Importing App Creating Method
from block_app import make_blockway

app = make_blockway()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
