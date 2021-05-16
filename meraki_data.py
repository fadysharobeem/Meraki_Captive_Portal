import requests,json,pprint,time

base_url = "https://api.meraki.com/api/v0/"
payload = {}

org_list = []
dict={}
node_mac_list = []

class meraki_users:
    # Check Meraki API function is used to verify if the API key provided by the user is working or not
    ## the return of the function is api_status variable
    def check_meraki_api(API):
        api_status = "NOT working"
        url = base_url+"organizations"
        headers = {"Content-Type": "application/json","Accept": "application/json","X-Cisco-Meraki-API-Key": API}
        response = requests.request('GET', url, headers=headers, data = payload)
        if response.status_code == 200:
            print("API key is working")
            api_status = "working"
        return api_status
    ### Get the list of Orgs the API key has access to
    def get_orgs(API):
        print(f"---------- {API}")
        url = base_url+f"/organizations/"
        headers = {"Content-Type": "application/json","Accept": "application/json","X-Cisco-Meraki-API-Key": API}
        response = requests.request('GET', url, headers=headers, data = payload)
        orgs = json.loads(response.text)
        for org in orgs:
            if org['id'] not in org_list:
                org_list.append(org['id'])
            else:
                pass
        ## Will add the org IDs to a list and then return it
        return org_list

    def get_devices(API,organizationId):
        url = base_url+f"/organizations/{organizationId}/devices"
        headers = {"Content-Type": "application/json","Accept": "application/json","X-Cisco-Meraki-API-Key": API}
        response = requests.request('GET', url, headers=headers, data = payload)
        the_devices =json.loads(response.text)
        for data in the_devices:
             dict[data["mac"]] = {}
             dict[data["mac"]]['networkId'] = data["networkId"]
             dict[data["mac"]]['org_id'] = organizationId
             node_mac_list.append(data["mac"])
        return dict

    def getGroupPolicy(API,networkId,GP_name):
        url = base_url+f"/networks/{networkId}/groupPolicies"
        headers = {"Content-Type": "application/json","Accept": "application/json","X-Cisco-Meraki-API-Key": API}
        response = requests.request('GET', url, headers=headers, data = payload)
        result = json.loads(response.text)
        for data in result:
            print(f"this is the ID of group policy --> {data['groupPolicyId']}")
            print(f"the name of the policy is --> {data['name']}")
            if GP_name == data['name']:
                return data['groupPolicyId']
            else:
                print("Couldnt find the Group Policy")

    def configure_client(API,networkId,username,mac,groupPolicyId):
        url = base_url + f"/networks/{networkId}/clients/provision"
        headers = {"Content-Type": "application/json","Accept": "application/json","X-Cisco-Meraki-API-Key": API}
        payload = '''{
            "mac": "%s",
            "name": "%s",
            "devicePolicy": "Group policy",
            "groupPolicyId": "%s"
        }'''%(mac,username,groupPolicyId)
        response = requests.request('POST', url, headers=headers, data = payload)
        print(response.text.encode('utf8'))

    # A loop function to capture all the Orgs and devices the API key has access to
    def Start(API_KEY):
        try:
            orgz = meraki_users.get_orgs(API_KEY)
            print(orgz)
            x = 0
            while x < len(orgz):
                try:
                    inv = meraki_users.get_devices(API_KEY,orgz[x])
                except:
                    pass
                x+=1
        except:
            print("The API seems wrong")

    ## This function is used to check if the Acccess Point got added after the initial run of the script
    def check_APs(API,node_mac):
        while node_mac not in node_mac_list:
            meraki_users.Start(API)
            if node_mac in node_mac_list:
                return "found"
            else:
                print("coundn't find this access point in this organization")
                return "Not found"
                break

    def verify(API,macz,username,node_mac,group_name):
        print(f"USERNAME iS {username}")
        ## Verify if the Node_mac is already claimed in the current Org, if not then we would run the script again to capture the updated list
        try:
            print(f"===== {node_mac_list}")
            if node_mac in node_mac_list:
                for key,value in dict.items():
                    if node_mac == key:
                        print("---- Found it in ",value['networkId'])
                        Group_policy_ID = meraki_users.getGroupPolicy(API,value['networkId'],group_name)
                        meraki_users.configure_client(API,value['networkId'],username,macz,Group_policy_ID)
            else:
                result = meraki_users.check_APs(API,node_mac)
                if result == "found":
                    for key,value in dict.items():
                        if node_mac == key:
                            print("---- Found it in ",value['networkId'])
                            Group_policy_ID = meraki_users.getGroupPolicy(API,value['networkId'],group_name)
                            meraki_users.configure_client(API,value['networkId'],username,macz,Group_policy_ID)
                if result == "Not found":
                    print("Access point is not part of this organization")
        except:
            print("There is error with configuring the Group Policy to the user")
