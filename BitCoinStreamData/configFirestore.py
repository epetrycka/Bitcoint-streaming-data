import os
from google.cloud import firestore
import firebase_admin
from firebase_admin import firestore, credentials

db = firestore.Client()

def create_collection():
    doc_ref = db.collection('users').document('user_123')

    doc_ref.set({
        'type': 'test'
    })
    print("Document created successfully.")

# Odczyt danych z dokumentu
# def read_document():
#     doc_ref = db.collection('users').document('user_123')
#     doc = doc_ref.get()

#     if doc.exists:
#         print(f'Document data: {doc.to_dict()}')
#     else:
#         print('No such document!')

# Aktualizacja dokumentu
# def update_document():
#     doc_ref = db.collection('users').document('user_123')

#     # Zaktualizowanie danych
#     doc_ref.update({
#         'age': 31
#     })
#     print("Document updated successfully.")

# Pobieranie wszystkich dokumentów z kolekcji
# def get_all_documents():
#     users_ref = db.collection('users')
#     docs = users_ref.stream()

#     for doc in docs:
#         print(f'{doc.id} => {doc.to_dict()}')

if __name__ == '__main__':
    create_collection()

    collection_name = "test"

    project_id = os.getenv("PROJECT_ID")

    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    db = firestore.Client(project=project_id)