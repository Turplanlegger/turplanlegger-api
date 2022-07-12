TOKEN=$(curl -sXPOST http://localhost:8080/login \
-H 'Content-Type: application/json' \
-d '
    {
        "email": "test@test.com",
        "password": "admin"
    }
' | jq --raw-output .token)

curl -iXPOST http://localhost:8080/item_list \
-H "Authorization: Bearer ${TOKEN}" \
-H 'Content-Type: application/json' \
-d '
    {
        "name": "Test list",
        "items": [
            "item one",
            "item two",
            "item three"
        ],
        "items_checked": [
            "item four",
            "item why would you add a checked one?!"
        ],
        "owner": 1,
        "type": "check"
    }
'
