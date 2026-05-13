import httpx

SPRING_BASE = "http://localhost:8080/api"


# tools.py

# Add this normalizer at the top
FIELD_MAP = {
    "phone": "phoneNumber",
    "phone_number": "phoneNumber",
    "mobile": "phoneNumber",
    "mobile_number": "phoneNumber",
    "first_name": "firstname",
    "last_name": "lastname",
    "first": "firstname",
    "last": "lastname",
    "mail": "email",
    "age": "age",
    "sal": "salary",
    "dept": "department",
    "dep": "department",
    "gen": "gender",
    "sex": "gender",
}

def normalize_fields(data: dict) -> dict:
    """Normalize field names to match Spring API expectations"""
    if not data:
        return data
    return {
        FIELD_MAP.get(k.lower(), k): v
        for k, v in data.items()
    }


async def update_employee(
    id=None,
    email=None,
    phoneNumber=None,
    name=None,
    updates=None
) -> dict:

    # ✅ Normalize the updates payload field names
    updates = normalize_fields(updates)

    if not updates or not isinstance(updates, dict) or len(updates) == 0:
        return {"success": False, "error": "invalid_updates_payload"}

    async with httpx.AsyncClient() as client:

        # ✅ Direct ID update
        if id is not None:
            r = await client.put(
                f"{SPRING_BASE}/updateemployee/{id}",
                json=updates
            )

            if r.status_code in (200, 201):
                try:
                    emp = r.json()
                except:
                    return {"success": False, "error": r.text}

                return {
                    "success": True,
                    "employeeid": emp.get("id", id),
                    "employee": emp,
                    "name": f"{emp.get('firstname','')} {emp.get('lastname','')}".strip()
                }

            return {"success": False, "error": r.text}

        # ✅ Find employee first by identifier
        if email:
            r = await client.get(f"{SPRING_BASE}/search", params={"email": email})
        elif phoneNumber:
            r = await client.get(f"{SPRING_BASE}/search", params={"phoneNumber": phoneNumber})
        elif name:
            r = await client.get(f"{SPRING_BASE}/search", params={"name": name})
        else:
            return {"success": False, "error": "missing_fields"}

        if r.status_code != 200:
            return {"success": False, "error": r.text}

        matches = r.json()

        if len(matches) == 0:
            return {"success": False, "error": "No employee found"}

        if len(matches) > 1:
            return {
                "success": False,
                "disambiguation": True,
                "employees": matches
            }

        emp = matches[0]

        # ✅ Now update by ID with normalized updates
        r = await client.put(
            f"{SPRING_BASE}/updateemployee/{emp['id']}",
            json=updates
        )

        if r.status_code in (200, 201):
            try:
                updated_emp = r.json()
            except:
                return {"success": False, "error": r.text}

            return {
                "success": True,
                "employeeid": updated_emp.get("id", emp["id"]),
                "employee": updated_emp,
                "name": f"{updated_emp.get('firstname','')} {updated_emp.get('lastname','')}".strip()
            }

        return {"success": False, "error": r.text}


async def delete_employee(
    id=None,
    email=None,
    phone=None,
    phoneNumber=None,   # ✅ accept both variants
    name=None
) -> dict:
    async with httpx.AsyncClient() as client:

        # ✅ Case 1: delete by ID
        if id is not None:
            r = await client.delete(f"{SPRING_BASE}/deleteemployee/{id}")
            if r.status_code == 200:
                return {"success": True, "employeeid": id}
            return {"success": False, "error": r.text}

        # ✅ Case 2: delete by email
        if email:
            r = await client.get(f"{SPRING_BASE}/search", params={"email": email})
            matches = r.json()

        # ✅ Case 3: delete by phone (handle both field names)
        elif phone or phoneNumber:
            number = phone or phoneNumber
            r = await client.get(f"{SPRING_BASE}/search", params={"phoneNumber": number})
            matches = r.json()

        # ✅ Case 4: delete by name
        elif name:
            r = await client.get(f"{SPRING_BASE}/search", params={"name": name})
            matches = r.json()

        else:
            return {"success": False, "error": "missing_fields"}

        if len(matches) == 0:
            return {"success": False, "error": "No employee found"}

        if len(matches) > 1:
            return {
                "success": False,
                "disambiguation": True,
                "employees": matches
            }

        emp = matches[0]

        r = await client.delete(f"{SPRING_BASE}/deleteemployee/{emp['id']}")

        if r.status_code == 200:
            return {
                "success": True,
                "employeeid": emp["id"],
                "name": f"{emp.get('firstname','')} {emp.get('lastname','')}".strip()
            }

        return {"success": False, "error": r.text}
    
async def search_employee(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SPRING_BASE}/search", params={"name": name})
        employees = r.json()
        return {
            "employees": employees,
            "count": len(employees)
        }
    
async def filter_gender(gender: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SPRING_BASE}/filter/gender", params={"gender": gender})
        employees = r.json()
        return {
            "employees": employees,
            "count": len(employees)
        }
async def delete_employee(id=None, email=None, phone=None, name=None) -> dict:
    async with httpx.AsyncClient() as client:

        # ✅ Case 1: delete by ID (best)
        if id is not None:
            r = await client.delete(f"{SPRING_BASE}/deleteemployee/{id}")
            if r.status_code == 200:
                return {
                    "success": True,
                    "employeeid": id
                }
            return {"success": False, "error": r.text}

        # ✅ Case 2: delete by email
        if email:
            r = await client.get(f"{SPRING_BASE}/search", params={"email": email})
            matches = r.json()

        # ✅ Case 3: delete by phone
        elif phone:
            r = await client.get(f"{SPRING_BASE}/search", params={"phoneNumber": phone})
            matches = r.json()

        # ✅ Case 4: delete by name (fallback)
        elif name:
            r = await client.get(f"{SPRING_BASE}/search", params={"name": name})
            matches = r.json()

        else:
            return {"success": False, "error": "missing_fields"}

        # ---- Common handling ----
        if len(matches) == 0:
            return {"success": False, "error": "No employee found"}

        if len(matches) > 1:
            return {
                "success": False,
                "disambiguation": True,
                "employees": matches
            }

        emp = matches[0]

        # Delete using ID
        await client.delete(f"{SPRING_BASE}/deleteemployee/{emp['id']}")

        return {
            "success": True,
            "employeeid": emp["id"],
            "name": f"{emp.get('firstname','')} {emp.get('lastname','')}".strip()
        }
    
async def add_employee(payload:dict)->dict:
    async with httpx.AsyncClient() as client:
        r=await client.post(f"{SPRING_BASE}/addemployee",json=payload)
        if r.status_code==201:
            emp=r.json()
            return {
                "success":True,
                "employee":emp,
                "employees":[emp],
                "name":F"{emp.get('firstname','')}{emp.get('lastname','')}"
            }
        else:
            return {
                "success":False,
                "error":r.text
            }
        
async def showallemployee()->dict:
    async  with httpx.AsyncClient() as client:
        r=await client.get(f"{SPRING_BASE}/allemployees")
        if r.status_code==200:
            emp=r.json()
            return {
                "success":True,
                "employees":emp,
                "count":len(emp)
            }
        else:
            return{
                "success":False,
                "error":r.text
            }
        
async def update_employee(id=None, email=None, phoneNumber=None, name=None, updates=None) -> dict:
    
    # ✅ Validate payload properly
    if not updates or not isinstance(updates, dict) or len(updates) == 0:
        return {"success": False, "error": "invalid_updates_payload"}

    async with httpx.AsyncClient() as client:

        # ✅ Direct ID update (best case)
        if id is not None:
            r = await client.put(f"{SPRING_BASE}/updateemployee/{id}", json=updates)

            if r.status_code in (200, 201):
                try:
                    emp = r.json()
                except:
                    return {"success": False, "error": r.text}

                return {
                    "success": True,
                    "employeeid": emp.get("id", id),
                    "employee": emp,
                    "name": f"{emp.get('firstname','')} {emp.get('lastname','')}".strip()
                }

            return {"success": False, "error": r.text}

        # ✅ Find employee first
        if email:
            r = await client.get(f"{SPRING_BASE}/search", params={"email": email})
        elif phoneNumber:
            r = await client.get(f"{SPRING_BASE}/search", params={"phoneNumber": phoneNumber})
        elif name:
            r = await client.get(f"{SPRING_BASE}/search", params={"name": name})
        else:
            return {"success": False, "error": "missing_fields"}

        if r.status_code != 200:
            return {"success": False, "error": r.text}

        matches = r.json()

        if len(matches) == 0:
            return {"success": False, "error": "No employee found"}

        if len(matches) > 1:
            return {
                "success": False,
                "disambiguation": True,
                "employees": matches
            }

        emp = matches[0]

        # ✅ FINAL FIX: use keyword args (NO positional bug)
        return await update_employee(id=emp["id"], updates=updates)