curl -iXPATCH http://localhost:8080/item_list/9/toggle_check \
-H 'Content-Type: application/json' \
-d '
    {
        "items": [
            30,
            29
        ]
    }
'
