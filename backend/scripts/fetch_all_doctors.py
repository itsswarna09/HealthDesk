import json
from apps.users.models import UserDocument, Role

def main():
    doctors = []
    for doc in UserDocument.collection().find({'role': Role.DOCTOR}):
        doctors.append(UserDocument.serialize(doc))
    print(json.dumps(doctors, default=str, indent=2))

if __name__ == '__main__':
    main()
