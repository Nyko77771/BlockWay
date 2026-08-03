import psutil

print("CPU Information: ", psutil.cpu_percent())
print("Memory Used Information: ", psutil.virtual_memory().percent)
print("Memory Available Information: ", round(100 - psutil.virtual_memory().percent, 1))
