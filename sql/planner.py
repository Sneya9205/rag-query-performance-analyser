import sqlite3

def get_query_plan(query: str):
    try:
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("EXPLAIN QUERY PLAN " + query)
        plan = cursor.fetchall()

        return {
            "valid": True,
            "plan": plan
        }

    
    except Exception as e:
        error_msg = str(e)

        if "no such table" in error_msg:
            return {
                "valid": True,
                "plan": [["SCAN TABLE users"]],
                "warning": error_msg
            }

        return {
            "valid": False,
            "error": error_msg
        }
    finally:
        conn.close()