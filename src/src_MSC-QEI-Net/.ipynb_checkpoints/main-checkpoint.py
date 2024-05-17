# -----------------------------------------------------------------------------
# Main file for extracting features
# Author: Xavier Beltran Urbano 
# Date Created: 21-02-2024
# -----------------------------------------------------------------------------

from network import QEI_Net
from keras import backend as K
from keras.optimizers import Adam, SGD
from tensorflow.keras.losses import MeanSquaredError,MeanAbsoluteError,CategoricalFocalCrossentropy
from metrics import MSE,MSE_loss, Pred, Rat, RMSE, macro_accuracy
import os
from utils import Utils
from configuration import Configuration
import os
import tensorflow as tf
from predict_Test import predict_test
import numpy as np
import random

def run_program(config,networkName, params, rater):
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = all logs; 1 = filter out INFO logs; 2 = filter out WARNING logs; 3 = filter out ERROR logs
    # Clear any existing TensorFlow session
    K.clear_session()
    utils = Utils()
    # Generate the IDs for train, val and test
    trainGenerator, valGenerator=config.createAllDataGenerators(rater)
    network = QEI_Net(imgSize=params['targetSize'])
    model = network.get_model()
    #model.summary()
    model.compile(optimizer=Adam(learning_rate=0.00001),loss=CategoricalFocalCrossentropy(),metrics=['accuracy'])
    with tf.device('/GPU:0'):
        # Train the model
        model_checkpoint_callback,reduce_lr_callback,early_stopping_callback = utils.allCallbacks(networkName,params['currentFold'], rater)
        epochs = 400
        history = model.fit(trainGenerator, validation_data=valGenerator, epochs=epochs, verbose=1, callbacks=[model_checkpoint_callback,reduce_lr_callback,early_stopping_callback])
        # Plot the results and save the image
        utils.save_training_plots(history, f"/home/xurbano/QEI-ASL/results/{networkName}/{rater}/{params['currentFold']}/training_plots.png")
        # Predict test set
        loss,acc=model.evaluate(valGenerator,verbose=1)
        print(f"\nVal: MSE= {acc}, Loss= {loss}")


if __name__ == "__main__":
    imgPath = '/home/xurbano/QEI-ASL/data_final'
    networkName="QEI-NET_CNN_ensemble_Classification_final"
    seed=48
    tf.random.set_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    raters=['JD']#Ali', 'JD', 'RW']
    # Create folder for this experiment
    os.makedirs(f"/home/xurbano/QEI-ASL/results/{networkName}", exist_ok=True)
    for i in range(1, 2):
        print("\n******************************************")
        print(f"----------Current Fold: {i}----------")
        # Parameters of the training
        params={
            'pathData':imgPath,
            'targetSize':(64,64,32,1),
            'batchSize':32,
            'currentFold':i
        }
        config=Configuration(**params)
        print(config.returnVal_IDS())
        for rater in raters:
            print(f"\nRater {rater}")
            # Create folder for this experiment
            os.makedirs(f"/home/xurbano/QEI-ASL/results/{networkName}/{rater}/{i}", exist_ok=True)
            
            # Configuration of the experiment
            #Run experiment
            run_program(config,networkName,params, rater)
        
    # Create some plots    
    predict_test()

