init:
#TODO check make, pip, python is installed
	pip install -r requirements.txt

run:
	bash -c "./predict_batch.sh data/chemical_list.csv"
	python3 metabolite_predicted_structure.py
	python3 metabolite_tentative_structure.py

.PHONY: init