#!/usr/bin/env bash
BACKBONE=$1
OUTPUTS_DIR=$2
if ! ([[ -n "${BACKBONE}" ]] && [[ -n "${OUTPUTS_DIR}" ]]); then
    echo "Argument BACKBONE or OUTPUTS_DIR is missing"
    exit
fi

python train.py -s=jun_voc -b=${BACKBONE} -o=${OUTPUTS_DIR} -d /data1/Jun/datasets/faster_rcnn --batch_size=8 --learning_rate=0.002 --step_lr_sizes="[25000, 35000]" --num_steps_to_snapshot=5000 --num_steps_to_finish=45000