TOKEN=$(curl -sXPOST http://localhost:8080/login \
-H 'Content-Type: application/json' \
-d '
    {
        "email": "test@test.com",
        "password": "admin"
    }
' | jq --raw-output .token)

curl -iXPOST http://localhost:8080/user \
-H "Authorization: Bearer ${TOKEN}" \
-H 'Content-Type: application/json' \
-d '
    {
        "name": "Ola",
        "last_name": "Nordmann",
        "email": "ola.nordmann@norge.no",
        "auth_method": "basic",
        "password": "test"
    }
'
