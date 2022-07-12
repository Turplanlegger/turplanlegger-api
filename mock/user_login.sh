curl -iXPOST http://localhost:8080/login \
-H 'Content-Type: application/json' \
-d '
    {
        "email": "ola.nordmann@norge.no",
        "password": "test"
    }
'
