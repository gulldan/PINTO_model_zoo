#!/usr/bin/env python

import os
import copy
import time
import argparse
from typing import List
import cv2 as cv
import numpy as np
import onnxruntime


def run_inference(
    onnx_session: onnxruntime.InferenceSession,
    input_name: str,
    input_shape: List[int],
    image: np.ndarray,
) -> np.ndarray:
    h, w, c = image.shape
    # Pre process:Resize, BGR->RGB, Transpose, float32 cast
    input_image = cv.resize(
        src=image,
        dsize=(input_shape[2], input_shape[1]),
    )
    input_image = input_image[..., ::-1]
    input_image = np.expand_dims(input_image, axis=0)
    input_image = input_image.astype('float32')
    input_image = input_image / 127.5 - 1.0

    # Inference
    result = onnx_session.run(
        output_names=None,
        input_feed={input_name: input_image},
    )

    # Post process:squeeze, RGB->BGR, Transpose, uint8 cast
    output_image = np.squeeze(result[0])
    output_image = (output_image + 1) * 127.5
    output_image = np.clip(output_image, 0, 255)
    output_image = output_image.astype(np.uint8)
    output_image = output_image[..., ::-1]
    output_image = cv.resize(
        src=output_image,
        dsize=(w, h),
    )

    return output_image


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-d',
        '--device',
        type=int,
        default=0,
    )
    parser.add_argument(
        '-f',
        '--movie_file',
        type=str,
        default='',
    )
    parser.add_argument(
        '-m',
        '--model',
        type=str,
        default='./model_float32_720x720.onnx',
    )

    args = parser.parse_args()
    model_path = args.model

    # Initialize video capture
    cap_device = args.device
    if args.movie_file:
        cap_device = args.movie_file
    cap = cv.VideoCapture(cap_device)
    cap_fps = cap.get(cv.CAP_PROP_FPS)
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
    video_writer = cv.VideoWriter(
        filename='output.mp4',
        fourcc=fourcc,
        fps=cap_fps,
        frameSize=(w, h*2),
    )
    WINDOW_NAME = 'Dehamer test'
    cv.namedWindow(WINDOW_NAME, cv.WINDOW_AUTOSIZE)

    # Load model
    model_dir = os.path.dirname(model_path)
    if model_dir == '':
        model_dir = '.'

    onnx_session = onnxruntime.InferenceSession(
        model_path,
        providers=[
            (
                'TensorrtExecutionProvider', {
                    'trt_engine_cache_enable': True,
                    'trt_engine_cache_path': model_dir,
                    'trt_fp16_enable': True,
                }
            ),
            'CUDAExecutionProvider',
            'CPUExecutionProvider'
        ],
    )

    model_input = onnx_session.get_inputs()[0]
    input_name = model_input.name
    input_shape = model_input.shape

    while True:
        # Capture read
        ret, frame = cap.read()
        if not ret:
            break
        debug_image = copy.deepcopy(frame)

        # Inference execution
        start_time = time.time()
        output_image = run_inference(
            onnx_session=onnx_session,
            input_name=input_name,
            input_shape=input_shape,
            image=frame,
        )
        elapsed_time = time.time() - start_time

        output_image = cv.resize(
            output_image,
            dsize=(
                debug_image.shape[1],
                debug_image.shape[0],
            )
        )

        # Inference elapsed time
        cv.putText(
            output_image,
            f"Elapsed Time : {elapsed_time * 1000:.1f} ms",
            (10, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv.LINE_AA,
        )
        cv.putText(
            output_image,
            f"Elapsed Time : {elapsed_time * 1000:.1f} ms",
            (10, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            1,
            cv.LINE_AA,
        )

        key = cv.waitKey(1)
        if key == 27:  # ESC
            break

        combined_img = np.vstack([debug_image, output_image])
        cv.imshow(WINDOW_NAME, combined_img)
        video_writer.write(combined_img)

    if video_writer is not None:
        video_writer.release()
    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()