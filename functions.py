def getListofDict(res, cur):
    
    list = res.fetchall()

    # Get column names dynamically
    columns = [column[0] for column in cur.description]

    # Convert the list of tuples to a list of dictionaries
    list_dict = [dict(zip(columns, row)) for row in list]

    return list_dict


# Get column names dynamically
def getDict(res, cur):
    tup = res.fetchone()
    columns = [column[0] for column in cur.description]
    # Convert the tuple to a dict
    dicto = dict(zip(columns, tup))

    return dicto
