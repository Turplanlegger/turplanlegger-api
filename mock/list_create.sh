curl -iXPOST http://localhost:8080/item_list \
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