TOKEN=$(curl -sXPOST http://localhost:8080/login \
-H 'Content-Type: application/json' \
-d '
    {
        "email": "test@test.com",
        "password": "admin"
    }
' | jq --raw-output .token)


curl -iXPATCH http://localhost:8080/item_list/9/add \
-H "Authorization: Bearer ${TOKEN}" \
-H 'Content-Type: application/json' \
-d '
    {
        "items": [
            "item five",
            "item six",
            "item 7"
        ],
        "items_checked": [
            "item eight"
        ]
    }
'
