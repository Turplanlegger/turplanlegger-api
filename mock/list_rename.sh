curl -iXPATCH http://localhost:8080/item_list/9/rename \
-H 'Content-Type: application/json' \
-d '
    {
        "name": "List now has a brand new name"
    }
'
