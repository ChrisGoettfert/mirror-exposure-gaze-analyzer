# Mirror Exposure Gaze Analyzer
This repository shows an implementation for analyzing gaze behavior of a person in a mirror exposure task. This tool allows to define visual bounding boxes derived from measured body data on a mirror image of a person. Together with gaze data from pupil lab eye trackers, it is then possible to analyze gaze behavior. The repository provides the code to the paper: link and includes the sample implementation for the study at that time with the Areas of Interest: head, left hand, right hand, and feet. For more information please read the paper. 

![image](https://user-images.githubusercontent.com/45085620/179250983-2a20af4e-2d1c-41cb-8a7f-ab4c4cdd67fe.png)



## Getting started
- Install all required python packages (see requirements.txt) -> pip install -r requirements.txt
- Start the pipeline by starting the `AoI_creator.py` script. 
- See Results in the Results folder afterwards

## Changing Areas of Interest or the Environment 
- Exact documentation will follow. There are some hints in the code where to edit values.


## Paper
https://downloads.hci.informatik.uni-wuerzburg.de/2022-muc-eyetracking_in_mirror_exposition-preprint.pdf

## Reference
When using this Framework please reference: 
````latex
@inproceedings{dollinger2022eyetracking,
  title        = {Analyzing Eye Tracking Data in Mirror Exposure},
  author       = {Döllinger, Nina and Göttfert, Christopher and Wolf, Erik and Mal, David and Latoschik, Marc Erich and Wienrich, Carolin},
  booktitle    = {Proceedings of the Conference on Mensch und Computer},
  year         = {2022},
  url          = {https://downloads.hci.informatik.uni-wuerzburg.de/2022-muc-eyetracking_in_mirror_exposition-preprint.pdf}
}
````

## Main Contributors

- Christopher Göttfert (Christopher.Goettfert@uni-wuerzburg.de)
- Nina Döllinger
- Carolin Wienrich 
