path = r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\contador\balance.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Line 1:", lines[0].strip())
print("Line 2:", lines[1].strip())
print("Line 3:", lines[2].strip())
print("Line 471:", lines[470].strip())
print("Line 472:", lines[471].strip())

