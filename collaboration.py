import firebase_admin
from firebase_admin import credentials, firestore
import difflib

class CollaborationManager:
    def __init__(self):
        cred = credentials.Certificate("path/to/your/firebase_credentials.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def create_document(self, doc_id, content):
        doc_ref = self.db.collection('documents').document(doc_id)
        doc_ref.set({
            'content': content,
            'version': 1,
            'history': [{'version': 1, 'content': content}]
        })

    def update_document(self, doc_id, new_content):
        doc_ref = self.db.collection('documents').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            old_content = doc.to_dict()['content']
            new_version = doc.to_dict()['version'] + 1
            doc_ref.update({
                'content': new_content,
                'version': new_version,
                'history': firestore.ArrayUnion([{'version': new_version, 'content': new_content}])
            })
            return self.generate_diff(old_content, new_content)
        return None

    def get_document(self, doc_id):
        doc_ref = self.db.collection('documents').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['content']
        return None

    def get_version_history(self, doc_id):
        doc_ref = self.db.collection('documents').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()['history']
        return None

    def generate_diff(self, old_content, new_content):
        differ = difflib.Differ()
        diff = list(differ.compare(old_content.splitlines(), new_content.splitlines()))
        return '\n'.join(diff)