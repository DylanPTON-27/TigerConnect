import ldap

def query_princeton_ldap(search_netid):
    # LDAP Configuration
    LDAP_SERVER = "ldaps://ldap.cs.princeton.edu"  # Use ldaps:// for port 636
    BASE_DN = "dc=cs,dc=princeton,dc=edu"
    SEARCH_FILTER = f"(uid={search_netid})"
    
    try:
        # Initialize connection
        l = ldap.initialize(LDAP_SERVER)
        l.protocol_version = ldap.VERSION3
        
        # Note: General Princeton LDAP now often requires a Bind (login)
        # For anonymous search (if allowed):
        # l.simple_bind_s() 

        # Perform the search
        search_scope = ldap.SCOPE_SUBTREE
        retrieve_attributes = None # None retrieves all available attributes
        
        result_id = l.search(BASE_DN, search_scope, SEARCH_FILTER, retrieve_attributes)
        
        # Collect results
        result_set = []
        while True:
            result_type, result_data = l.result(result_id, 0)
            if result_data == []:
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    result_set.append(result_data)
        
        return result_set

    except Exception as e:
        print(f"LDAP Error: {e}")
        return None

if __name__ == "__main__":
    results = query_princeton_ldap("ms9454")
    print(results)