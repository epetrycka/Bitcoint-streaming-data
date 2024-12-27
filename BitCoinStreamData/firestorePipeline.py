import apache_beam as beam
from apache_beam import window
from apache_beam.options.pipeline_options import PipelineOptions, WorkerOptions
from apache_beam.transforms.trigger import AfterWatermark, AccumulationMode, AfterCount, Repeatedly, AfterProcessingTime
from dotenv import load_dotenv
import os
from google.cloud import pubsub_v1, firestore
import json
from typing import Dict, Tuple, List
import argparse
import time
import firebase_admin
from firebase_admin import firestore, credentials

if __name__ == "__main__":
    # parser = argparse.ArgumentParser() 
        
    # parser.add_argument('--input',           
    #                     dest='input',
    #                     required=True,
    #                     help='Input topic to process.')
    # parser.add_argument('--output',
    #                     dest='output',
    #                     required=True,
    #                     help='Output file to write results to.')

    # path_args, pipeline_args = parser.parse_known_args()   

    # inputs_pattern = path_args.input   
    # outputs_prefix = path_args.output

    load_dotenv('./.env')

    project_id = os.getenv("PROJECT_ID")
    subscriber = pubsub_v1.SubscriberClient()

    input_subscription_id = os.getenv("FIRE_SUB_ID")
    input_subscription_path = subscriber.subscription_path(project_id, input_subscription_id)

    collection_name = "test"

    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    db = firestore.Client(project=project_id)

    @beam.typehints.with_input_types(str)
    @beam.typehints.with_output_types(Dict)
    def json_message(element: str) -> Dict:
        data = json.loads(element)
        return data
    
    # @beam.typehints.with_input_types(Dict)
    # @beam.typehints.with_output_types(window.TimestampedValue)
    # def timestamp(element: Dict) -> window.TimestampedValue:
    #     try:
    #         data = element['data']
    #         unix_timestamp = data['E']
    #         return window.TimestampedValue(element, int(unix_timestamp))
    #     except (IndexError, ValueError) as e:
    #         raise ValueError(f"Invalid timestamp at element {element}: {e}") from e
    
    @beam.typehints.with_input_types(Dict)
    @beam.typehints.with_output_types(Tuple[str, List[float]])
    def extract(element: Dict) -> Tuple[str, List[float]]:
        import time
        data = element['data']
        timestamp = data['E']
        price = data['p']
        quantity = data['q']

        timestamp_s = timestamp / 1000.0
        formatted_date = time.strftime("%d-%m-%Y_%H:%M", time.gmtime(timestamp_s))

        return (formatted_date, [float(price), float(quantity)])
    
    @beam.typehints.with_input_types(Tuple[str, List[float]])
    @beam.typehints.with_output_types(Tuple[str, List[float]])
    def total_value(element: Tuple[str, List[float]]) -> Tuple[str, List[float]]: #(time , [price, quantity, total_value])
        total_value = element[1][0] * element[1][1]
        element[1].append(total_value)
        return element
    
    class FirestoreWriteDoFn(beam.DoFn):
        def start_bundle(self):
            import firebase_admin
            from firebase_admin import firestore, credentials
            self.client = firestore.Client()

        @beam.typehints.with_input_types(Tuple[str, List[float]])
        def process(self, element: Tuple[str, List[float]]):
            import firebase_admin
            from firebase_admin import firestore, credentials
            collection_name = "test"

            db = firestore.Client(project='bitcoinstream')

            key, value = element
            date, hour = key.split('_')

            data = {
                "average_price" : value[0],
                "total_quantity" : value[1],
                "total_value" : value[2] 
            }

            print(hour, " : ", value)
            doc_ref = db.collection(collection_name).document(date)
            doc_ref.set({ hour : data }, merge=True)

            yield f"Processed {key} with data: {data}"

    # @beam.typehints.with_input_types(Tuple[str, List[float]])
    # def writeToFirestore(element: Tuple[str, List[float]]) -> Tuple[int, List[float]]:

    #     key, value = element
    #     date, hour = key.split('_')

    #     data = {
    #         "average_price" : value[0],
    #         "total_quantity" : value[1],
    #         "total_value" : value[2] 
    #     }

    #     print(hour, " : ", value)
    #     doc_ref = db.collection(collection_name).document(date)
    #     doc_ref.set({ hour : data }, merge=True)

    
    class CalculateStats(beam.CombineFn):
        @beam.typehints.with_output_types(List[float])
        def create_accumulator(self) -> List[float]:
            return [0.0, 0.0, 0.0, 0]
        
        @beam.typehints.with_input_types(List[float])
        @beam.typehints.with_output_types(List[float])
        def add_input(self, accumulator: List[float], element: List[float]) -> List[float]:
            sum_price, sum_quantity, sum_total_value, count = accumulator
            price, quantity, total_value = element
            return [sum_price + price, sum_quantity + quantity, sum_total_value + total_value, count + 1]

        @beam.typehints.with_input_types(List[float])
        @beam.typehints.with_output_types(List[float])
        def merge_accumulators(self, accumulators: List[float]) -> List[float]:
            sum_price, sum_quantity, sum_total_value, count = zip(*accumulators)
            return [sum(sum_price), sum(sum_quantity), sum(sum_total_value), sum(count)]
        
        @beam.typehints.with_input_types(List[float])
        @beam.typehints.with_output_types(List[float])
        def extract_output(self, accumulator: List[float]) -> List[float]:
            sum_price, sum_quantity, sum_total_value, count = accumulator
            if count > 0:
                average_price = sum_price / count
                return [average_price, sum_quantity, sum_total_value]
            else:
                return [0.0, 0.0, 0.0]
            
    def debug(element):
        print(element, '\n', type(element))
        return element

    options = PipelineOptions(streaming=True,
                            runner='DataflowRunner',
                            project='bitcoinstream',
                            region='europe-central2',
                            temp_location='gs://bitcoin-test/temp',
                            staging_location='gs://bitcoin-test/staging',
                            requirements_file='requirements.txt')
    # options = PipelineOptions(streaming=True)
    options.view_as(WorkerOptions).max_num_workers = 2
    p =beam.Pipeline(options=options)

    input = (
    p
    | 'Read from PubSub subscription' >> beam.io.gcp.pubsub.ReadFromPubSub(subscription=input_subscription_path)
    | 'Decode from utf-8' >> beam.Map(lambda element: element.decode("utf-8")).with_output_types(str)
    | 'Json message' >> beam.Map(json_message)
    | 'Filter trades informations' >> beam.Filter(lambda element: element['type'] == 'trade').with_input_types(Dict)
    | 'Extract trade and timestamp' >> beam.Map(extract)
    | 'Add record total value' >> beam.Map(total_value)
    | 'Windowing' >> beam.WindowInto(
        window.FixedWindows(60),
        trigger=AfterWatermark(),
        accumulation_mode=AccumulationMode.DISCARDING)
    | 'Calculate Stats' >> beam.CombinePerKey(CalculateStats())
    | 'Write data to firestore' >> beam.ParDo(FirestoreWriteDoFn())
)

result = None
try:
    result = p.run()
    result.wait_until_finish()
except KeyboardInterrupt:
    print("Interrupted")
    if result is not None:
        result.cancel()
finally:
    if result is not None:
        result.cancel()
