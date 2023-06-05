# DeepPicar

DeepPicar is a low-cost autonomous RC car platform using a deep
convolutional neural network (CNN). DeepPicar is a small scale replication
of [NVIDIA's real self-driving car called DAVE-2](https://developer.nvidia.com/blog/deep-learning-self-driving-cars/), which drove on public
roads using a CNN. DeepPicar uses the same CNN architecture of NVIDIA's
DAVE-2 and can drive itself in real-time locally on a Raspberry Pi.

## Required Parts

There are five main parts that are needed in order to assemble the DeepPicar. 

| Part                         | Approx. Cost ($) |
 ----------------------------  | ----------------
| Raspberry Pi Zero 2 W        | 15 |
| New Bright 1:24 scale RC car | 10 |
| MicroSD Card (32 GB)         | 8  |
| Pololu DRV8835 motor driver  | 16 |
| Power bank                   | 14 |
| Raspberry Pi Zero Camera v1.3| 15 |

Miscellaneous parts: jumper cables (to connect motor driver to motor), USB to microUSB connectors (to power pi and motor driver), wireless gamepad and microUSB to USB female adaptor (for alternative control)

## Build instructions

TODO

## Setup

Install DeepPicar.

    $ sudo apt install libatlas-base-dev
    $ git clone --depth=1 https://github.com/CSL-KU/DeepPicar-v3 -b devel
    $ cd DeepPicar-v3 
    $ sudo pip3 install -r requirements.txt

Edit `params.py` to select correct camera and actuator drivers. 
The setting below represents the standard webcam and drv8835 configuration, for example. 

    camera="camera-webcam"
    actuator="actuator-drv8835"
    
In addition, you need to install necessary python drivers. For polulu drv8835, do following.

    $ git clone https://github.com/pololu/drv8835-motor-driver-rpi.git
    $ cd drv8835-motor-driver-rpi
    $ sudo python3 setup.py install

Also install the python package "inputs" if you would like to to use Logitech F710 gamepad for data collection.

    $ git clone https://github.com/zeth/inputs.git
    $ cd inputs
    $ sudo python setup.py install
    
## Manual control and Data collection

Following command can be used to run the script with gamepad control enabled

    $ sudo nice --20 python3 deeppicar.py -g -n 4 -f 30

Using the keyboard or gamepad, you can control the car, record and download data, upload the model, and run the DNN.

Keyboard controls
* **'UpArrow'**: move forward 
* **'DownArrow'**: move backward
* **'Space'**: stop
* **'LeftArrow'**: turn left
* **'RightArrow'**: turn right 

Use the keys to manually control the car. Once you become confident in controlling the car, collect the data to be used for training the DNN model. 

Each recording attempt with overwrite the previous.

Rename recorded avi and csv files to out-video-XX.avi and out-video-XX.csv where XX with appropriate numbers. 

Compress all the recorded files into a single zip file, say Dataset.zip for Colab.

## Train the model
    
Open the colab notebook. Following the notebook, you will upload the dataset to the colab, train the model, and download the model back to your PC. 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/CSL-KU/DeepPicar-v3/blob/devel/RunAll.ipynb)

After you are done trainig, you need to copy the trained tflite model file (`large-200x66x3.tflite` by default) to the Pi using the web uploader

## Autonomous control

Copy the trained model to the DeepPicar. 

Enable autonomous driving through the `Start DNN` button.

## Driving Videos

[![DeepPicar Driving](https://img.youtube.com/vi/16sO3B9hpik/0.jpg)](https://youtu.be/16sO3B9hpik "DeepPicar_Video")

Some other examples of the DeepPicar driving can be found at: https://photos.app.goo.gl/q40QFieD5iI9yXU42
