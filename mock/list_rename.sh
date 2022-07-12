TOKEN=$(curl -sXPOST http://localhost:8080/login \
-H 'Content-Type: application/json' \
-d '
    {
        "email": "test@test.com",
        "password": "admin"
    }
' | jq --raw-output .token)

curl -iXPATCH http://localhost:8080/item_list/9/rename \
-H "Authorization: Bearer ${TOKEN}" \
-H 'Content-Type: application/json' \
-d '
    {
        "name": "List now has a brand new name"
    }
'
