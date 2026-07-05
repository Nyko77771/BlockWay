import logging

# Creating a Logger Variable
logger = logging.getLogger('block_app')
logger.setLevel(logging.DEBUG)

# Creating Specific Logging handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("block_app.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.WARNING)

# Adding Formatter to Handlers
# Create Custom Logging Form
formatter = logging.Formatter(
    "%(asctime) - %(levelname) - %(name) - %(message)",
    datefmt="%d-%m-%Y %H:%M"
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adding Handlers to Logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
