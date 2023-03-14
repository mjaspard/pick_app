
import re



filename = "/Users/maxime/Project/Pick_Crater/pick_app/input_shape.py"
param = 'R_P2'
new_value= '422'




# # Open the file in 'read' mode and read all the lines into a list
# with open(filename, 'r') as file:
#     lines = file.readlines()
#     print(type(lines))

# # Find the line you want to replace
# for i, line in enumerate(lines):
# 	if re.search(param, line) and re.search(r'^[^#].', line):
# 		# create pattern to extract current parameter value
# 		pattern = r"=\s+[0-9]+"
# 		value = re.search(pattern, line)[0]
# 		print(value)
# 		value = re.search("\d+", value)[0]
# 		print(value)
# 		print("--")
# 		new_line = line.replace(value, new_value)
# 		lines[i] = new_line
			
# # Open the file in 'write' mode and write the updated lines to the file
# with open(filename, 'w') as file:
#     file.writelines(lines)
			

dict = {}


# Open the file in 'read' mode and read all the lines into a list
with open(filename, 'r') as file:
    lines = file.readlines()
    print(type(lines))


for i, line in enumerate(lines):
	if re.search("=", line) and re.search(r'^[^#].', line):

		try:
			pattern = r"^\s*.+="
			param = re.search(pattern, line)[0]
			param = re.search("\w+", param)[0]
			pattern = r"=\s+.+\s*#*"
			value = re.search(pattern, line)[0]
			value = re.search("\w+", value)[0]
			print(param+ " = "+value)
		except:
			print("issue no param or value found: File input shape does not match <param = value>  ")
			break
			# print(value)

		dict[param] = value

print(dict)
