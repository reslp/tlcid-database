#!/usr/bin/env python3

import sys
from itertools import chain
import re

# Class mappings for Path and GroupName derivation (from reference data)
CLASS_MAPPINGS = {
    "3,4-benzocoumarins": {
        "path": "acetyl-polymalonyl pathway",
        "group": "coumarins"
    },
    "[structure not known]": {
        "path": "unknown",
        "group": "unknown"
    },
    "[unknown]": {
        "path": "unknown",
        "group": "unknown"
    },
    "aliphatic acids": {
        "path": "acetyl-polymalonyl pathway",
        "group": "aliphatic acids & aliphatic compounds"
    },
    "aliphatic acids [unknown structure]": {
        "path": "acetyl-polymalonyl pathway",
        "group": "aliphatic acids & aliphatic compounds"
    },
    "aliphatic compound": {
        "path": "acetyl-polymalonyl pathway",
        "group": "aliphatic acids & aliphatic compounds"
    },
    "aliphatic compounds": {
        "path": "acetyl-polymalonyl pathway",
        "group": "aliphatic acids & aliphatic compounds"
    },
    "amino acid derivative": {
        "path": "shikimic acid pathway",
        "group": "amino-acid derivatives"
    },
    "amino acid derivatives": {
        "path": "shikimic acid pathway",
        "group": "amino-acid derivatives"
    },
    "amino-acid derivatives": {
        "path": "shikimic acid pathway",
        "group": "amino-acid derivatives"
    },
    "anthraquinones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "antrhaquinones": {  # Typo in source
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "benzyl ester": {
        "path": "acetyl-polymalonyl pathway",
        "group": "benzyl esters"
    },
    "benzyl esters": {
        "path": "acetyl-polymalonyl pathway",
        "group": "benzyl esters"
    },
    "biphenyls": {
        "path": "shikimic acid pathway",
        "group": "biphenyls"
    },
    "chromanes": {
        "path": "mevalonic acid pathway",
        "group": "chromanes"
    },
    "chromones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "chromones"
    },
    "depsido-depsones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsones"
    },
    "depsidones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "depsones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsones"
    },
    "dibenzofurans": {
        "path": "acetyl-polymalonyl pathway",
        "group": "furans & furanones"
    },
    "diphenyl ether": {
        "path": "acetyl-polymalonyl pathway",
        "group": "diphenyl ethers"
    },
    "diphenyl ethers": {
        "path": "acetyl-polymalonyl pathway",
        "group": "diphenyl ethers"
    },
    "ergochromes": {
        "path": "acetyl-polymalonyl pathway",
        "group": "xanthones & ergochromes"
    },
    "furoquinones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "isocoumarins": {
        "path": "acetyl-polymalonyl pathway",
        "group": "coumarins"
    },
    "monocyclic aromatic compounds": {
        "path": "shikimic acid pathway",
        "group": "monocyclic aromatic derivatives & compounds"
    },
    "monocyclic aromatic derivatives": {
        "path": "shikimic acid pathway",
        "group": "monocyclic aromatic derivatives & compounds"
    },
    "monocyclic aromatic derivatives & compounds": {
        "path": "acetyl-polymalonyl pathway",
        "group": "monocyclic aromatic derivatives & compounds"
    },
    "naphthaquinone": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "naphthaquinones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "naphthopyrone": {
        "path": "acetyl-polymalonyl pathway",
        "group": "naphthopyrones"
    },
    "naphthopyrones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "naphthopyrones"
    },
    "orcinol depsides": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsides"
    },
    "orcinol depsidones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "orcinol m-depsides": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsides"
    },
    "orcinol tetradepsides": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsides"
    },
    "orcinol tridepsides": {
        "path": "",
        "group": "depsides"
    },
    "orcinol β-orcinol depsides": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsides"
    },
    "orcinol β-orcinol depsidone": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "orcinol β–orcinol depsidones": {  # Typo in source
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "p-terphenyls": {
        "path": "shikimic acid pathway",
        "group": "p-terphenyls"
    },
    "perylenequinones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "phenalenones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "phenalenones"
    },
    "phenanthraperylenequinones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "phenanthraquinones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "phenanthroperylenequinones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "quinones"
    },
    "pulvinic acid derivatives": {
        "path": "shikimic acid pathway",
        "group": "pulvinic acid derivatives"
    },
    "pulvinic acids": {
        "path": "shikimic acid pathway",
        "group": "pulvinic acid derivatives"
    },
    "spirobenzofuranones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "furans & furanones"
    },
    "steroids": {
        "path": "mevalonic acid pathway",
        "group": "terpenoids & steroids"
    },
    "terpene + polyketide": {
        "path": "terpenoids & steroids",
        "group": "terpenoids"
    },
    "terpenoids": {
        "path": "mevalonic acid pathway",
        "group": "terpenoids & steroids"
    },
    "terphenyl quinones": {
        "path": "shikimic acid pathway",
        "group": "terphenylquinones"
    },
    "terphenylquinones": {
        "path": "shikimic acid pathway",
        "group": "terphenylquinones"
    },
    "unknown": {
        "path": "unknown",
        "group": "unknown"
    },
    "unknown [depsidone?]": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "usnic acid derivatives": {
        "path": "acetyl-polymalonyl pathway",
        "group": "usnic acid derivatives"
    },
    "xanthones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "xanthones & ergochromes"
    },
    "β-orcinol depsides": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsides"
    },
    "β-orcinol depsidones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "β-orcinol m-depsides": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsides"
    },
    "orcinol β-orcinol depsidones": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "orcinol β–orcinol depsidones": {  # Typo in source
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "orcinol β-orcinol depsidone": {
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    },
    "orcinol β–orcinol depsidone": {  # Typo in source
        "path": "acetyl-polymalonyl pathway",
        "group": "depsidones"
    }
}

filename = sys.argv[1]

with open(filename, "r") as infile:
	raw_data = ""
	for line in infile:
		line = line.replace("'", "´")
		line = line.replace('"', "´´")
		if not line.startswith("Cortex"):
			raw_data += line

entries = raw_data.split("\n\n")
def flatten(nested):
	return [x for item in nested for x in (item if isinstance(item, list) else [item])]


def parse_rf_line(line):
	elements = line.split(" ")
	elements = [element.replace(" ", "") for element in elements if element != ""]
	elements = [element.replace(":", "") for element in elements if element] 
	return [element for element in elements if element.isdigit() or element in ["x", "?"]]

def parse_hplc_line(line):
	line = line.strip()
	element = line.split(":")[1]
	if "TLC" in element or "Rf" in element:
		element= element.split(" ")[0]
	if element == "":
		element = "x"
	return element.strip()

def parse_color_line(line):
	elements = line.split(" ")
	elements = [element.replace(" ", "") for element in elements if element != ""]
	elements = [element.replace(":", "") for element in elements]
	elements = [element for element in elements if element not in ["V", "UV"]]
	return elements

def parse_spray_line(line):
	line = re.sub(r' {2,}', ';', line) 
	elements = line.split(";")
	elements = [element.split(":") for element in elements]
	elements = flatten(elements)
	elements = [element.strip() for element in elements if element not in ["Acid Spray", "LW UV"]]
	return elements

def parse_archers_line(line):
	elements = line.split(":")
	elements = [element.strip() for element in elements if "Archers" not in element]
	return elements

def parse_spot_test_line(line):
	line = re.sub(r' {2,}', ';', line) 
	elements = line.split(":")
	elements = [element.split(";") if ";" in element else element for element in elements]
	elements = flatten(elements)
	elements = [element.strip() for element in elements if element not in ["K", "KC", "PD", "C"]]
	elements = ["No Result" if element == "" else element for element in elements]
	return elements

def parse_mass_spectrum_line(line):
	elements = line.split(":")
	elements = elements[-1].split(",")
	elements = [element.strip() if element != "" else "x" for element in elements]
	if len(elements) < 4:
		for i in range(1, 5-len(elements)):
			elements.append("x")
	if len(elements) > 4: # sometimes there are 5 values, not sure what they mean.
		elements = ["x", "x", "x", "x"]
	return elements

def parse_substance_class_line(line):
	el = line.split(":")
	el = el[-1].strip().lower()
	elements = []

	if el in CLASS_MAPPINGS:
		elements.append(CLASS_MAPPINGS[el]["path"])
	else: 
		elements.append("")
	if el in CLASS_MAPPINGS:
		elements.append(CLASS_MAPPINGS[el]["group"])
	else: 
		elements.append("")
	elements.append(el)
	return elements

def parse_notes_line(line):
	elements = line.replace("\n", "").strip()
	return [elements]

def parse_related_substances_line(line):
	element = ""
	if "Reference:" in line:
		element = line.split("Reference:")[0].strip()
	if "References:" in line:
		element = line.split("References:")[0].strip()
	if element == "" or element == " " or element == None:
		element = "?"
	element = element.replace("\n", "")
	return [element]

def parse_reference_line(line):
	element = line.split("Note:")[0]
	element = line.split("Notes:")[0]
	element = element.split("Acid Spray:")[0]
	element = element.replace("\n", "")
	element = element.strip()
	element = element.replace("/", "")
	return [element]
# name	A	B	Bprime	C	E	F	G	HPLC	BefVis	BefUVS	BefUVL	Archers	AftVis	AftUV	M	F1	F2	F3	KResult	CResult	KCResult	PDResult	Cortex	Medulla	Notes	Related	Reference	Lichens	Synonyms	Path	GroupName	Class	GLossID

print("name,A,B,Bprime,C,E,F,G,HPLC,BefVis,BefUVS,BefUVL,Archers,AftVis,AftUV,M,F1,F2,F3,KResult,CResult,KCResult,PDResult,Cortex,Medulla,Notes,Related,Reference,Lichens,Synonyms,Path,GroupName,Class,GLossID")
i = 0
for entry in entries:
	i += 1
	outlist = []

	name = entry.split("\n")[1]
	#if i == 1:
	#	name = entry.split("\n")[0]

	outlist.append(name) # 1 - name
	outlist += parse_rf_line(entry.split("\n")[2]) # 7 - Rf values
	outlist.append(parse_hplc_line(entry.split("\n")[3])) # 1 - HPLC	
	outlist += parse_color_line(entry.split("\n")[4]) # 2 - BefVis, BefUVS
	outlist += ["?"] # BefUVL - this is only present for one substance in the mytabolits database and not in Elix.
	outlist += parse_archers_line(entry.split("\n")[6]) # 1 - Archers
	outlist += parse_spray_line(entry.split("\n")[5]) # 2 - AftVis, AftUV
	outlist += parse_mass_spectrum_line(entry.split("\n")[8]) # 4 - M, F1, F2, F3
	outlist += parse_spot_test_line(entry.split("\n")[7]) # 4 - KResult, CResult, KCResult, PDResult
	outlist += ["?", "?"] # 2 - stub entry for Cortex/Medulla reactions in Elix PDF is is empty throughout (and so in mytabolites) 
	outlist += parse_notes_line(entry.split("Notes:")[-1]) # 1 -notes
	outlist += parse_related_substances_line(entry.split("Biosynthetically Related Compounds:")[-1]) # 1 - related
	# 1 - reference
	## due to inconsistency in Elix PDF need if here:
	if "Reference:" in entry:
		outlist += parse_reference_line(entry.split("Reference:")[-1])
	elif "References:" in entry:
		outlist += parse_reference_line(entry.split("References:")[-1])
	else:
		outlist += ["no reference"]
	outlist += [""]# 1 - lichens, should be filled from lichen substance data table.
	## 1 - synonyms:
	if "[" in name:
		outlist += [name.split("[")[-1].split("]")[0]] # 1 - synonyms
	else:
		outlist += [""]
	outlist += parse_substance_class_line(entry.split("\n")[9]) # 3 - path, group, class
	outlist += [""] # 1 - GlossID: Not in Elix PDF, therefore left empty
	# now check if elements contain csv delimiter: ,
	processed_outlist = []
	for e in outlist:
		if "," in e:
			e = '"' + e + '"'
		processed_outlist.append(e)
	#if "Pseudoplacodiolic acid" in name:
	#	print(processed_outlist)
	#	print(len(processed_outlist))
	#if "Psoromic acid" in name:
	#	print(processed_outlist)
	#	print(len(processed_outlist))
	if len(processed_outlist) != 34: # to debug
		continue
		print(name, len(processed_outlist))
		print(processed_outlist)
		print()
	
	print(",".join(processed_outlist))
