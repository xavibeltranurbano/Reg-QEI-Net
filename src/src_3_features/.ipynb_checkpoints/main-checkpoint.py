# -----------------------------------------------------------------------------
# Main file
# Author: Xavier Beltran Urbano 
# Date Created: 21-02-2024
# -----------------------------------------------------------------------------

from network import FCDN_QEI
from keras import backend as K
from keras.optimizers import Adam, SGD
from tensorflow.keras.losses import MeanSquaredError
from metrics import MSE,MSE_loss, Pred, Rat
import os
from utils import Utils
from configuration import Configuration
import os
import tensorflow as tf
from predict_Test import predict_test
import numpy as np
import random

def run_program(config,networkName, params):
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = all logs; 1 = filter out INFO logs; 2 = filter out WARNING logs; 3 = filter out ERROR logs
    # Clear any existing TensorFlow session
    K.clear_session()
    utils = Utils()
    # Compute the features
    trainGenerator, valGenerator=config.createAllDataGenerators()
    network = FCDN_QEI(nFeatures=params['targetSize'])
    model = network.get_model()
    model.summary()
    model.compile(optimizer=Adam(learning_rate=0.0001),loss='mean_squared_error',metrics=[MSE, Pred, Rat])
    with tf.device('/GPU:0'):
        # Train the model
        model_checkpoint_callback,reduce_lr_callback,early_stopping_callback = utils.allCallbacks(networkName,params['currentFold'])
        epochs = 4000
        history = model.fit(trainGenerator, validation_data=valGenerator, epochs=epochs, verbose=1, callbacks=[reduce_lr_callback,model_checkpoint_callback, early_stopping_callback])

        #model.save(f"/home/xurbano/QEI-ASL/results/{networkName}/{params['currentFold']}/Best_Model.h5")
        # Plot the results and save the image
        utils.save_training_plots(history, f"/home/xurbano/QEI-ASL/results/{networkName}/{params['currentFold']}/training_plots.png")
        # Predict test set
        loss,acc,_,_=model.evaluate(valGenerator,verbose=1)
        print(f"\nVal: MSE= {acc}, Loss= {loss}")


if __name__ == "__main__":
    imgPath = '/home/xurbano/QEI-ASL/data_final'
    networkName="QEI-NET_3_features"
    seed=48
    tf.random.set_seed(48)
    np.random.seed(48)
    random.seed(48)
    # Create folder for this experiment
    os.makedirs(f"/home/xurbano/QEI-ASL/results/{networkName}", exist_ok=True)

    for i in range(1, 2):
        print("\n******************************************")
        print(f"----------Current Fold: {i}----------")
        # Parameters of the training
        params={
            'pathData':imgPath,
            'targetSize':(3,),
            'batchSize':256,
            'currentFold':i
        }
        
        # Create folder for this experiment
        os.makedirs(f"/home/xurbano/QEI-ASL/results/{networkName}/{i}", exist_ok=True)
        
        # Configuration of the experiment
        config=Configuration(**params)
        
        #Run experiment
        run_program(config,networkName,params)
        
    # Create some plots    
    predict_test()