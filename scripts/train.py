from imageai.Detection.Custom import DetectionModelTrainer

#Setup the trainer and use model Yolov3
trainer = DetectionModelTrainer()
trainer.setModelTypeAsYOLOv3()
#Set Data directory folder
trainer.setDataDirectory(data_directory="tomato")
#Objects, batch & experiments + pre-existing model
# batch_size = number of training examples used in one iteration
# num_experiments = number of iterations
trainer.setTrainConfig(object_names_array=["red_cherry_tomato", "orange_cherry_tomato", "yellow_cherry_tomato", "green_cherry_tomato"], batch_size=1, num_experiments=1, train_from_pretrained_model="C:\\Users\\Max\\Desktop\\superAI\\tomato\\models\\detection_model-ex-013--loss-0108.641.h5")
#Start training
trainer.trainModel()
