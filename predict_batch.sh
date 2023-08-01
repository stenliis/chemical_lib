#!/bin/bash

predict()
{
	RAW=$(echo -n "${1}" | tr -d '\n'| tr -d '\r')
	CHEMICAL_STUFF="'"${RAW}"'"
	THRESHOLD=0.001
	#MODEL_FOLDER="/trained_models_cfmid4.0/[M+H]+" #inside docker folder
	MODEL_FOLDER="${2}"
	ANNOTATE_FRAGMENTS=1 #1-yes, 0-no

	sudo docker run --rm=true -v $(pwd):/cfmid/public/ -i wishartlab/cfmid:latest sh -c "cfm-predict ${CHEMICAL_STUFF} ${THRESHOLD} ${MODEL_FOLDER}/param_output.log ${MODEL_FOLDER}/param_config.txt ${ANNOTATE_FRAGMENTS}"
}

prediction_batch_run()
{
	FILE=${1}
	FOLDER=${2}
	MODEL=${3}

	#load input file
	LINES=$(cat "${FILE}")

	#number of loaded lines
	LINES_CNT=$(echo "$LINES" | wc -l)

	#deliminer
	OLDIFS=${IFS}
	IFS=';'

	#INDEX - number of completed predictions
	INDEX=0

	#prediction start tie - used for calculation of ETA
	PREDICT_START_TIME=$(date +%s)

	#run with batch file
	echo "PREDICT BATCH MODE+ started"
	while read -r -u 666 NUMBER NAME FORMULA MASS MODEL_PLUS MODEL_MINUS SMILE_CODE INCHI SOURCE
	do
		#valid INCHI must start with: InChI=
		if [[ ! "$INCHI" =~ ^InChI=.* ]]
		then
    		continue
		fi

		#OUTFILE
		OUTFILE="${FOLDER}/${NAME}"
		echo "Calculate prediction of ${NAME} and store into ${OUTFILE}"
	
		#increment INDEX
		((INDEX++))

		#run computation for model+ if not cached
		if [ ! -f "${OUTFILE}" ] 
		then
			#run predict for specific chemical MODEL
			RESULT=$(predict "${INCHI}" "${MODEL}")
			#save to file
			{
				echo "${NAME}"
				echo ""
				echo "${INCHI}"
				echo ""
				echo "${RESULT}"
			} >> "${OUTFILE}"
			echo "Calculation completed."
		else
			echo "Already calculated => skipping."
			continue
		fi
	
		#calculate remaining time
		ACTUAL_TIME=$(date +%s)
		SPENT_TIME=$(echo "${ACTUAL_TIME}-${PREDICT_START_TIME}" | bc)
		TIME_PER_CHEMICAL=$(echo "${SPENT_TIME}/${INDEX}" | bc)
		REMAING_LINES=$(echo "${LINES_CNT}-${INDEX}" | bc)
		REMAING_TIME=$(echo "${TIME_PER_CHEMICAL}*${REMAING_LINES}" | bc)
		
		#report progress
		echo "PREDICT MODEL+ BATCH ${INDEX} / ${LINES_CNT}, ETA: ${REMAING_TIME}s"
	
	done 666< "${FILE}"
	echo "PREDICT BATCH MODE+ completed"

	#restore deliminer
	IFS=${OLDIFS}
}

#prepare variable
CHEMICAL_LIST_FILE=$1
FOLDER_PLUS="data/computed+"
FOLDER_MINUS="data/computed-"
MODEL_FOLDER_PLUS="/trained_models_cfmid4.0/[M+H]+"
MODEL_FOLDER_MINUS="/trained_models_cfmid4.0/[M-H]-"

#check that in file exist
[ ! -f "${CHEMICAL_LIST_FILE}" ] && { echo "${CHEMICAL_LIST_FILE} file not found"; exit 99; }

#start docker
sudo docker run --name chemical_predictor --rm=true -v $(pwd):/cfmid/public/ -dit wishartlab/cfmid:latest

#run predictions batches
prediction_batch_run "${CHEMICAL_LIST_FILE}" "${FOLDER_PLUS}" "${MODEL_FOLDER_PLUS}"
prediction_batch_run "${CHEMICAL_LIST_FILE}" "${FOLDER_MINUS}" "${MODEL_FOLDER_MINUS}"

#stop docker
sudo docker kill chemical_predictor
