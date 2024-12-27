from google.cloud import pubsub_v1
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv('./.env')
    publisher = pubsub_v1.PublisherClient()

    project_id = os.getenv("PROJECT_ID")
    topic_id = os.getenv("TOPIC_ID")
    topic_path = publisher.topic_path(project=project_id, topic=topic_id)

    try:
        publisher.create_topic(request={"name":topic_path})
        print(f"Topic {topic_id} has been created")
    except Exception as e:
        print(f"Topic {topic_id} already exist: {e}")

    subscriber = pubsub_v1.SubscriberClient()

    firestore_subscription_id = os.getenv("FIRE_SUB_ID")
    firestore_subscription_path = subscriber.subscription_path(project_id, firestore_subscription_id)

    try:
        subscriber.create_subscription(
            request={
                "name": firestore_subscription_path,
                "topic": topic_path,
            }
        )
        print(f"Subscription '{firestore_subscription_id}' has been created.")
    except Exception as e:
        print(f"Subscription {firestore_subscription_id} already exist: {e}")

    bigquery_subscription_id = os.getenv("BIG_SUB_ID")
    bigquery_subscription_path = subscriber.subscription_path(project_id, bigquery_subscription_id)

    try:
        subscriber.create_subscription(
            request={
                "name": bigquery_subscription_path,
                "topic": topic_path,
            }
        )
        print(f"Subscription '{bigquery_subscription_id}' has been created.")
    except Exception as e:
        print(f"Subscription {bigquery_subscription_id} already exist: {e}")