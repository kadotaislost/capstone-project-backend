import cv2
import requests
import typing
import numpy as np
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer, get_wer
from mltu.transformers import ImageResizer

import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image: np.ndarray):
        image = ImageResizer.resize_maintaining_aspect_ratio(image, *self.input_shapes[0][1:3][::-1])

        image_pred = np.expand_dims(image, axis=0).astype(np.float32)

        preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text


# Configuration       
cloudinary.config( 
    cloud_name = "doafbg5ys", 
    api_key = "427425611218285", 
    api_secret = "DWVz5n-AfuYaa0_UQpc3f1iizQM", # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Upload an image

if __name__ == "__main__":
    import pandas as pd
    from tqdm import tqdm
    from mltu.configs import BaseModelConfigs
    import tempfile
    
    upload_result = cloudinary.uploader.upload("aryan-removebg-preview(1).jpg"
                                           )
    url = upload_result["secure_url"]
    print(url)
    response = requests.get(url)
    image_data= np.frombuffer(response.content, np.uint8)
    # Step 2: Decode the image data for OpenCV
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    # Step 3: Use the image directly in OpenCV or save it as a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file_name = temp_file.name
        cv2.imwrite(temp_file_name, image)
    
    configs = BaseModelConfigs.load("configs.yaml")
    
    image = cv2.imread(temp_file_name)

    model = ImageToWordModel(model_path= "model.onnx", char_list=configs.vocab)
    text = model.predict(image)
    print(text)