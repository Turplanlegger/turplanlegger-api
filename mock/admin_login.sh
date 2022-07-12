curl -iXPOST http://localhost:8080/login \
-H 'Content-Type: application/json' \
-d '
    {
        "email": "test@test.com",
        "password": "admin"
    }
'
