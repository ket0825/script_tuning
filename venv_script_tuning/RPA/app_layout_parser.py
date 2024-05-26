
### 무기한 연기
# import layoutparser as lp
# import cv2


# path = "pdf/test-image.png"        
# image = cv2.imread(path)
# image = image[..., ::-1]

# # lp.visualization.draw_box()

# # mode1 = lp.models.Detectron2LayoutModel
# model = lp.Detectron2LayoutModel('lp://HJDataset/faster_rcnn_R_50_FPN_3x/config', 
#                                  model_path = r'C:/Users/82104/PythonWorkspace/venv_script_tuning/Lib/site-packages/layoutparser/models/detectron2/model_final.pth',
#                                  extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
#                                  label_map={1:"Page Frame", 2:"Row", 3:"Title Region", 4:"Text Region", 5:"Title", 6:"Subtitle", 7:"Other"}
#                                  )
# layout = model.detect(image)
# n = lp.draw_box(image, layout, box_width=3)

# import numpy as np

# n_np = np.array(n)

# cv2.imwrite('testing.png', n_np)

