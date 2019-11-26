import boto3

def create_key(region, name, arquivo):
    s = boto3.Session(region_name=region)
    ec2 = s.client('ec2')
    k = name
    p = arquivo

    try:
        response = ec2.create_key_pair(KeyName=k)
        print('key criada')
        a = './'+p+'.pem'
        with open(a, 'w') as file:
            file.write(response['KeyMaterial'])
    except:
        response = ec2.delete_key_pair(KeyName=k)
        response = ec2.create_key_pair(KeyName=k)
        print('key criada')
        a = './'+p+'.pem'
        with open(a, 'w') as file:
            file.write(response['KeyMaterial'])
    return a,k

