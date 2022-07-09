import pandas
from file_operations import file_methods
from data_preprocessing import preprocessing
from data_ingestion import data_loader_prediction
from application_logging import logger
from Prediction_Raw_Data_Validation.predictionDataValidation import Prediction_Data_validation
import pickle


class prediction:

    def __init__(self,path):
        self.file_object = open("Prediction_Logs/Prediction_Log.txt", 'a+')
        self.log_writer = logger.App_Logger()
        self.pred_data_val = Prediction_Data_validation(path)

    def predictionFromModel(self):

        try:
            self.pred_data_val.deletePredictionFile() #deletes the existing prediction file from last run!
            self.log_writer.log(self.file_object,'Start of Prediction')
            data_getter=data_loader_prediction.Data_Getter_Pred(self.file_object,self.log_writer)
            data=data_getter.get_data()

            #code change
            # wafer_names=data['Wafer']
            # data=data.drop(labels=['Wafer'],axis=1)

            preprocessor=preprocessing.Preprocessor(self.file_object,self.log_writer)
            data = preprocessor.dropUnnecessaryColumns(data,
                                                       ['TSH_measured', 'T3_measured', 'TT4_measured', 'T4U_measured',
                                                        'FTI_measured', 'TBG_measured', 'TBG', 'TSH'])

            # replacing '?' values with np.nan as discussed in the EDA part
            print(data.shape[1])

            data = preprocessor.replaceInvalidValuesWithNull(data)

            print("returned data invalid", data)

            # get encoded values for categorical data

            data = preprocessor.encodeCategoricalValuesPrediction(data)

            is_null_present=preprocessor.is_null_present(data)
            print("is null present",is_null_present)
            if(is_null_present):
                data=preprocessor.impute_missing_values(data)

            #data=data.to_numpy()
            file_loader=file_methods.File_Operation(self.file_object,self.log_writer)
            print("file loader")
            kmeans=file_loader.load_model('KMeans')
            rf = file_loader.load_model('RandomForest1')
            print("loaded kmeans")

            ##Code changed
            #pred_data = data.drop(['Wafer'],axis=1)
            print(data.columns)
            clusters = kmeans.predict(data)#drops the first column for cluster prediction
            rf_preds = rf.predict(data)

            print("clusters",clusters)
            print("results are", rf_preds)
            data['clusters']=clusters
            data['rf_cluster'] = rf_preds
            print(data)
            clusters = data['clusters'].unique()
            rf_preds = data['rf_cluster'].unique()
            result = [] # initialize balnk list for storing predicitons
            rf_df = []
            with open('EncoderPickle/enc.pickle', 'rb') as file: #let's load the encoder pickle file to decode the values
                encoder = pickle.load(file)
            print(clusters)

            for i in clusters:
                print("In loop")
                cluster_data= data[data['clusters']==i]
                cluster_data = cluster_data.drop(['clusters','rf_cluster'],axis=1)
                model_name = file_loader.find_correct_model_file(i)
                print("model_name",model_name)
                model = file_loader.load_model(model_name)
                for val in (encoder.inverse_transform(model.predict(cluster_data))):
                    result.append(val)
            result = pandas.DataFrame(result, columns=['Predictions'])
            print("results are", result)

            print(data)

            print("rf_preds", rf_preds)

            for i in rf_preds:
                print('in rf loop')
                rf_data = data[data['rf_cluster']==i]
                print(rf_data)
                rf_data = rf_data.drop(['rf_cluster', 'clusters'], axis=1)
                for val in (encoder.inverse_transform(rf.predict(rf_data))):
                    print("val",val)
                    rf_df.append(val)
            print("exited rf loop")

            rf_df = pandas.DataFrame(rf_df, columns=['Predictions'])
            print(rf_df)


            path = "Prediction_Output_File/Predictions.csv"
            result.to_csv("Prediction_Output_File/Predictions.csv",header=True) #appends result to prediction file
            self.log_writer.log(self.file_object,'End of Prediction')
        except Exception as ex:
            self.log_writer.log(self.file_object, 'Error occured while running the prediction!! Error:: %s' % ex)
            raise ex
        return path , result

            # old code
            # i=0
            # for row in data:
            #     cluster_number=kmeans.predict([row])
            #     model_name=file_loader.find_correct_model_file(cluster_number[0])
            #
            #     model=file_loader.load_model(model_name)
            #     #row= sparse.csr_matrix(row)
            #     result=model.predict([row])
            #     if (result[0]==-1):
            #         category='Bad'
            #     else:
            #         category='Good'
            #     self.predictions.write("Wafer-"+ str(wafer_names[i])+','+category+'\n')
            #     i=i+1
            #     self.log_writer.log(self.file_object,'The Prediction is :' +str(result))
            # self.log_writer.log(self.file_object,'End of Prediction')
            #print(result)



