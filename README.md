# Waste Detection using YOLOv4-tiny, Darknet, and TensorFlow

This project is a waste detection system that uses the YOLOv4-tiny object detection algorithm, implemented with Darknet and TensorFlow, to identify and classify different types of waste. 
## Dataset

The dataset used in this project was built by the me using a program called LabelImg to annotate waste objects in images. The dataset consists of images of waste in different environments, and contains the following classes:
* Plastic
* Glass
* Paper
* Metal
* Cardboard

Note: The trained weights are included in the repository, so there is no need to train the model. 

## Usage

To use this project, follow these steps:
1. Clone the repository to your local machine
2. Install the required libraries by running the following command: `pip install -r requirements.txt`
3. Open the GUI by running the `gui.py` file
4. Click the 'Browse' button to select an image containing waste
5. Click the 'Process' button to detect and classify the waste in the image
6. The output will be displayed below the 'Process' button
