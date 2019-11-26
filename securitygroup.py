import boto3
from botocore.exceptions import ClientError


def cria_security(regiao,name,descri,ip='0.0.0.0/0',porta = 5000):
    s = boto3.Session(region_name=regiao)
    ec2 = s.client('ec2')

    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try:
        response = ec2.create_security_group(GroupName= name,
                                            Description= descri,
                                            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        perm = [
                {'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                'FromPort': porta,
                'ToPort': porta,
                'IpRanges': [{'CidrIp': ip}]},
            ]

        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=perm)
        print('Ingress Successfully Set %s' % data)
    except ClientError as e:
        print(e)
    return security_group_id