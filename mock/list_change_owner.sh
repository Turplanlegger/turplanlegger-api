curl -iXPATCH http://localhost:8080/item_list/9/owner \
-H 'Content-Type: application/json' \
-d '
    {
        "owner": 2
    }
'
