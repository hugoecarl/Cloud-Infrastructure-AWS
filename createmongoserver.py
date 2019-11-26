import botocore
import boto
import paramiko
import boto3
import subprocess
import ast
import time
from botocore.exceptions import ClientError
import securitygroup as sec
import keypair
import sys

#cria keypair
keyname = keypair.create_key('us-east-1','PF_cloud','KeyNV')[1]
pemcreat = keypair.create_key('us-east-1','PF_cloud','KeyNV')[0]
def passakey():
    return keyname,pemcreat

#aloca ips para as instancias com ip-elastico (mongo, webserver e pass_on)

s = boto3.Session(region_name="us-east-2")
ee = s.resource('ec2')
aa = s.client('ec2')


try:
    allocation = aa.allocate_address(Domain='vpc')
except ClientError as e:
    pass    


ec2 = boto3.resource('ec2')
ec = boto3.client('ec2')

try:
    for i in range(2):
        allocation = ec.allocate_address(Domain='vpc')
except ClientError as e:
    pass

def allocid():
    filters = [{'Name': 'domain', 'Values': ['vpc']}]
    response = ec.describe_addresses(Filters=filters)
    a = []
    for i in response['Addresses']:
        if 'InstanceId' not in i:
            a.append(i)
    s = boto3.Session(region_name="us-east-2")
    aa = s.client('ec2')
    filters = [{'Name': 'domain', 'Values': ['vpc']}]
    response = aa.describe_addresses(Filters=filters)
    for i in response['Addresses']:
        if 'InstanceId' not in i:
            a.append(i)
    return a

  


#deleta instancias baseado nas tags delas e libera o ip elastico
def pega_id():
    a = "Name=value,Values=Hugo_mongoserv"
    out = subprocess.Popen(["aws", "ec2" ,"describe-tags", "--filters", a], 
              stdout=subprocess.PIPE, 
              stderr=subprocess.STDOUT)

    stdout = out.communicate()
    b = ast.literal_eval(stdout[0].decode("utf-8"))
    return b

a = pega_id()

for i in a["Tags"]:
    ec2 = boto3.resource('ec2')
    ec2.instances.filter(InstanceIds = [i["ResourceId"]]).terminate()
    print("Terminando " + i["ResourceId"])
    try:
        filters = [{'Name': 'instance-id', 'Values': [i["ResourceId"]]}]
        response = ec.describe_addresses(Filters=filters)
        responsei = ec.release_address(AllocationId=response['Addresses'][0]['AllocationId'])
        print('Mongo Ip Address released')
    except Exception as e:
        print('Exception na hora de liberar ip instancia mas ok')


if len(a["Tags"]) != 0:
  print("Esperando instancias mongo terminarem")
  for i in range(0, 60):
      time.sleep(1)
      print(60 - i)

#cria security group
ab = allocid()
def lista_alloc():
    return ab
try:
    response = ec.delete_security_group(GroupName='MongoGroup')
except:
    pass
securid = sec.cria_security('us-east-1','MongoGroup','mongodb',ab[0]['PublicIp']+'/32',27017)

#cria as instancias
instances = ec2.create_instances(
     ImageId='ami-04b9e92b5572fa0d1',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro',
     KeyName=keyname,
     TagSpecifications=[
    {
      'ResourceType': 'instance',
      'Tags': [
        {
          'Key': 'Name',
          'Value': 'Hugo_mongoserv'
        }
      ]
    }
  ],
    SecurityGroupIds=[securid]
 )

instance_id = instances[0].instance_id
print(instance_id)
def mongoservid():
    return instance_id


print("Esperando instancias mongo iniciarem")
for i in range(0, 70):
    time.sleep(1)
    print(70 - i)

b = pega_id()


response = ec.associate_address(AllocationId=ab[1]['AllocationId'],InstanceId=instance_id)
print(response)
        


#Inicia as instancias
try:
    instances = ec2.instances.filter(InstanceIds=[instance_id])
    for instance in instances:
        print(instance.id, instance.instance_type)

    x = instances
    print('Enviando Comandos de Inicialização da instancia...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.RSAKey.from_private_key_file(pemcreat)
    ssh.connect(instance.public_dns_name,username='ubuntu',pkey=privkey)
    ssh.exec_command('git clone https://github.com/hugoecarl/PF_Cloud.git;tmux new-session -d -s "myTempSession" bash /home/ubuntu/PF_Cloud/install_mongo.sh')
except Exception as e:
    print(e)
    sys.exit(1)

