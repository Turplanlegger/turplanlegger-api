curl -iXPATCH http://localhost:8080/item_list/9/add \
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
