# ₿ Bitcoin Price Analytics – Real-Time Processing with Apache Beam

This project continuously analyzes Bitcoin price changes based on real-time **trade data received from WebSocket feeds**.  
Using **Apache Beam** and **Google Cloud Dataflow**, it processes streaming data to extract insights like:

- Average Bitcoin price  
- Total BTC quantity traded  
- Total value of Bitcoin purchases  

Processed data is stored in **Google Firestore** for further analysis, visualization, or dashboarding.

---

## Project Architecture

```
+-------------------+
|  WebSocket Client |  --> Streams raw BTC trade data
+--------+----------+
         |
         v
  +------+------+
  |   Publisher  |  --> Publishes data to Google Pub/Sub
  | (Cloud App)  |
  +------+------+
         |
         v
+------------------------+
| Apache Beam Pipeline   |
| (Google Cloud Dataflow)|
+------------------------+
| v
+--------------+
| Firestore    |
+--------------+

```
---

## Technologies Used

- **Apache Beam (Python SDK)**
- **Google Cloud Dataflow**
- **Google Cloud Pub/Sub**
- **Google Firestore**
- **WebSocket API** (crypto exchange feed)
- (TO DO) **Cloud Run** / **Cloud Functions** for the publisher

---

## Features

- Real-time BTC trade stream processing
- Aggregates by time window (e.g. hourly, per minute)
- Cloud-native architecture: scalable and modular
- Clean separation of responsibilities:
  - `publisher/` – connects to WebSocket and sends to Pub/Sub
  - `pipeline/` – reads from Pub/Sub, transforms, writes to Firestore

---

## 📦 Getting Started

### 1. Enable required GCP services

```bash
gcloud services enable dataflow.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com
```
2. Authentication
`gcloud auth application-default login`

4. Install dependencies
`pip install apache-beam[gcp] websockets`
5. Run the Publisher (locally or deploy to cloud)
```
cd publisher
python main.py --pubsub-topic projects/YOUR_PROJECT/topics/bitcoin-trades
```
You can also deploy the publisher to Cloud Run, Cloud Functions, or even use a VM – so it runs 24/7 without relying on your local machine.

6. Run the Beam Pipeline (on Dataflow)
```python pipeline/bitcoin_pipeline.py \
  --runner DataflowRunner \
  --project YOUR_PROJECT \
  --region YOUR_REGION \
  --temp_location gs://YOUR_BUCKET/temp \
  --input_topic projects/YOUR_PROJECT/topics/bitcoin-trades \
  --firestore_collection btc_trades_hourly
```
Windowing Strategy
The Beam pipeline uses Fixed Windows to calculate:

Average price of Bitcoin trades in that window

Total amount of Bitcoin traded

Total trade value

Configuration can be adjusted via parameters.

7. Firestore Structure (example)
```
{
  "date": "2025-04-20T10:00:00Z",
  "avg_price": 64523.13,
  "total_quantity": 8.321,
  "total_value": 536215.83
}
```
### Possible Improvements
 Add support for sliding/tumbling windows

 Visual dashboard (e.g., Firebase + Chart.js)

 Multi-asset support (ETH, LTC…)

 Integrate alerts when price exceeds thresholds

8. Why Not Kubernetes?
Originally, the system was planned for Kubernetes deployment. However, due to the cost of long-running workloads, a serverless architecture was preferred. Components like the publisher can run in Cloud Run, while Beam pipelines are handled by Dataflow.
