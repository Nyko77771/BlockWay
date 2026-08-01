# Importing os module
import os


def generate_log_data():
    log_file_path = "block_app/logs/block_app.log"
    logs = []

    if os.path.exists(log_file_path):

        with open(log_file_path, "r", encoding="utf-8") as file:

            for line in reversed(file.readlines()):

                try:
                    sections = line.strip().split(" - ")

                    if len(sections) < 6:
                        continue

                    logs.append(
                        {
                            "timestamp": sections[0],
                            "level": sections[1],
                            "component": sections[2],
                            "function": sections[3],
                            "application": sections[4],
                            "message": sections[5]        
                        }
                    )
                except Exception as e:
                    print(f"Exception occured: {e}")

    return logs

results = generate_log_data()
print("Total logs:", len(results))
print("Latest log level: ", results[0]["level"])