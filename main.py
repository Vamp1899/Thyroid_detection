from wsgiref import simple_server
from flask import Flask, request
from flask import Response, render_template
import os
from flask_cors import CORS, cross_origin
from prediction_Validation_Insertion import pred_validation
from trainingModel import trainModel
from training_Validation_Insertion import train_validation
import flask_monitoringdashboard as dashboard
from predictFromModel import prediction
import json
import trainingModel

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
dashboard.bind(app)
CORS(app)
@app.route("/",methods=['GET'])
@cross_origin()
def home():
    return render_template('about.html')

@app.route("/predict", methods=['POST'])
@cross_origin()
def predictme():
    try:
        print(request.form)
        '''if request.json['folderPath'] is not None:
            print('in folder path json')
            path = request.json['folderPath']

            pred_val = pred_validation(path) #object initialization

            print(pred_val)

            pred_val.prediction_validation() #calling the prediction_validation function

            pred = prediction(path) #object initialization

            # predicting for dataset present in database
            path = pred.predictionFromModel()
            return Response("Prediction File created at %s!!!" % path)'''

        if request.form is not None:
            print('entered')

            path = request.form['filepath']

            print(path)

            pred_val = pred_validation(path)  # object initialization

            print(pred_val)

            pred_val.prediction_validation()  # calling the prediction_validation function

            print("pred_val.prediction_validation()")

            pred = prediction(path)  # object initialization



            # predicting for dataset present in database
            path ,model = pred.predictionFromModel()

            return Response("Predictions are -" f'{model.Predictions.head()}')
    except ValueError:
        print('hey')
        return Response("Error Occurred! %s" %ValueError)
    except KeyError:
        print('hey2')
        return Response("Error Occurred! %s" %KeyError)
    except Exception as e:
        print('hey3')
        return Response("Error Occurred! %s" %e)



@app.route("/train", methods=['POST'])
@cross_origin()
def trainRouteClient():

    try:
        if request.json['folderPath'] is not None:
            print("Entered")
            path = request.json['folderPath']
            train_valObj = train_validation(path) #object initialization

            train_valObj.train_validation()#calling the training_validation function


            trainModelObj = trainModel() #object initialization
            trainModelObj.trainingModel() #training the model for the files in the table


    except ValueError:

        return Response("Error Occurred! %s" % ValueError)

    except KeyError:

        return Response("Error Occurred! %s" % KeyError)

    except Exception as e:

        return Response("Error Occurred! %s" % e)
    Best_params=trainingModel.best_model.best_params_
    print(trainingModel.best_model)
    return Response(f"Training successfull!!,{Best_params}")

#port = int(os.getenv("PORT"))
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 5000
    httpd = simple_server.make_server(host, port, app)
    print("Serving on %s %d" % (host, port))
    httpd.serve_forever()
