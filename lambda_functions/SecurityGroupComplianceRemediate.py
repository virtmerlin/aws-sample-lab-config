# NOTES:
#
# This code is only intended for instructional purposes and should not be used for any other use.

import json
import boto3
import botocore


REQUIRED_PERMISSIONS = [
{"FromPort": 22, "IpProtocol": "tcp", "IpRanges": [{"CidrIp": "0.0.0.0/0"}], "Ipv6Ranges": [{"CidrIpv6": "::/0"}], "PrefixListIds": [], "ToPort": 22, "UserIdGroupPairs": []}
]

DENIED_PERMISSIONS = [
{"FromPort": 80, "IpProtocol": "tcp", "IpRanges": [{"CidrIp": "0.0.0.0/0"}], "Ipv6Ranges": [{"CidrIpv6": "::/0"}], "PrefixListIds": [], "ToPort": 80, "UserIdGroupPairs": []},
{"FromPort": 80, "IpProtocol": "tcp", "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": ""}], "Ipv6Ranges": [{"CidrIpv6": "::/0", "Description": ""}], "PrefixListIds": [], "ToPort": 80, "UserIdGroupPairs": []}
]


def lambda_handler(event, context):
    
## Set Boto client def
    print(event)
    params = json.loads(event)
    group_id = (params["parameterValue"])
    #group_id = (event["parameterValue"])
    client = boto3.client("ec2")

    debug_enabled = True

    if debug_enabled:
        print("Received event: " + json.dumps(event, indent=2))

## Get Existing Perms from Security group   
    try:
        response = client.describe_security_groups(GroupIds=[group_id])
    except botocore.exceptions.ClientError as e:
        if debug_enabled:
            print("security group definition: ", json.dumps(response, indent=2))
        return {
            "remediation" : "describe_security_groups failure on group " + group_id
        }

    
    ip_permissions = response["SecurityGroups"][0]["IpPermissions"]
    authorize_permissions = [item for item in REQUIRED_PERMISSIONS if item not in ip_permissions]
    revoke_permissions = [item for item in DENIED_PERMISSIONS if item in ip_permissions]
    
    print("Current Permissions...")
    print(ip_permissions)
    print("Revoke...")
    print(revoke_permissions)
    print("Authorize...")
    print(authorize_permissions)

## Process Required Ingress

    if authorize_permissions:
        if debug_enabled:
            print("authorizing for ", group_id, ", ip_permissions ", json.dumps(authorize_permissions, indent=2))
    
        try:
            client.authorize_security_group_ingress(GroupId=group_id, IpPermissions=authorize_permissions)
           
        except botocore.exceptions.ClientError as e:
            if 'InvalidPermission.Duplicate' in str(e):
               print('Duplicate rule exist, that is OK.')
            else:
                print(e)
                return {
                    'statusCode': 500,
                   "remediation" : "authorize_security_group_ingress failure on group " + group_id
               }

## Revoke Denied Ingress
    if revoke_permissions:
        if debug_enabled:
            print("revoking for ", group_id, ", ip_permissions ", json.dumps(revoke_permissions, indent=2))
        try:
            client.revoke_security_group_ingress(GroupId=group_id, IpPermissions=revoke_permissions)
        except botocore.exceptions.ClientError as e:
            return {
                'statusCode': 500,
                "remediation" : "revoke_security_group_ingress failure on group " + group_id
            }


    return {
        'statusCode': 200,
        "remediation" : "Completed for " + group_id
    }

