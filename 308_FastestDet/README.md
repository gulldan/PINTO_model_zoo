# How to generate post-processing ONNX
Simply change the following parameters and run all shells.

https://github.com/PINTO0309/PINTO_model_zoo/blob/main/308_FastestDet/convert_script.txt
```bash
OPSET=11
BATCHES=1
BOXES=240
CLASSES=80
```

# How to change NMS parameters
![image](https://user-images.githubusercontent.com/33194443/178145616-be4d3c94-8785-4d6a-bf89-17b31b2a348d.png)

https://github.com/PINTO0309/simple-onnx-processing-tools

Run the script below to directly rewrite the parameters of the ONNX file.
```bash
H=180
W=320

### max_output_boxes_per_class
sam4onnx \
--op_name main01_nonmaxsuppression11 \
--input_onnx_file_path fastestdet_post_${H}x${W}.onnx \
--output_onnx_file_path fastestdet_post_${H}x${W}.onnx \
--input_constants main01_max_output_boxes_per_class int64 [10]

### iou_threshold
sam4onnx \
--op_name main01_nonmaxsuppression11 \
--input_onnx_file_path fastestdet_post_${H}x${W}.onnx \
--output_onnx_file_path fastestdet_post_${H}x${W}.onnx \
--input_constants main01_iou_threshold float32 [0.6]

### score_threshold
sam4onnx \
--op_name main01_nonmaxsuppression11 \
--input_onnx_file_path fastestdet_post_${H}x${W}.onnx \
--output_onnx_file_path fastestdet_post_${H}x${W}.onnx \
--input_constants main01_score_threshold float32 [0.7]
```
