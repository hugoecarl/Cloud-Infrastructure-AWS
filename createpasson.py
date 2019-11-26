import botocore
import boto
import paramiko
import boto3
import subprocess
import ast
import time
import securitygroup
import createwebserver as crw
import securitygroup as sec
import requests
import keypair
import sys

#cria keypair ohio
keyname = keypair.create_key('us-east-2','PF_cloud_ohio','KeyOhio')[1]
pemcreat = keypair.create_key('us-east-2','PF_cloud_ohio','KeyOhio')[0]

ec2 = boto3.resource('ec2')
ecm = boto3.client('ec2')

filters = [{'Name': 'instance-id', 'Values': [crw.webservid()]}]
responses = ecm.describe_addresses(Filters=filters)

s = boto3.Session(region_name="us-east-2")
ec2 = s.resource('ec2')
ec = s.client('ec2')


#deleta instancias baseado nas tags delas
def pega_id():
    a = "Name=value,Values=Pass_on"
    out = subprocess.Popen(["aws", "ec2" ,"describe-tags", "--filters", a,"--region","us-east-2"], 
              stdout=subprocess.PIPE, 
              stderr=subprocess.STDOUT)

    stdout = out.communicate()
    b = ast.literal_eval(stdout[0].decode("utf-8"))
    return b

a = pega_id()

for i in a["Tags"]:
    ec2.instances.filter(InstanceIds = [i["ResourceId"]]).terminate()
    print("Terminando " + i["ResourceId"])
    try:
        filters = [{'Name': 'instance-id', 'Values': [i["ResourceId"]]}]
        response = ec.describe_addresses(Filters=filters)
        responsei = ec.release_address(AllocationId=response['Addresses'][0]['AllocationId'])
        print('Passon Ip Address released')
    except Exception as e:
        print('Exception na hora de liberar ip instancia mas ok')

if len(a["Tags"]) != 0:
  print("Esperando instancias pass_on terminarem")
  for i in range(0, 60):
      time.sleep(1)
      print(60 - i)

#cria security group
try:
    response = ec.delete_security_group(GroupName='PassonSec')
except:
    pass
ab = crw.lista_alloc()
securid = sec.cria_security('us-east-2','PassonSec','Simmple Redirection')
def securids():
    return securid

#cria as instancias
instances = ec2.create_instances(
     ImageId='ami-0d5d9d301c853a04a',
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
          'Value': 'Pass_on'
        }
      ]
    }
  ],
    SecurityGroupIds=[securid]
 )

instance_id = instances[0].instance_id
def passonid():
    return instance_id


print("Esperando instancias pass on iniciarem")
for i in range(0, 60):
    time.sleep(1)
    print(60 - i)

b = pega_id()

response = ec.associate_address(AllocationId=ab[2]['AllocationId'],InstanceId=instance_id)
print(response)

filters = [{'Name': 'instance-id', 'Values': [instance_id]}]
respon = ec.describe_addresses(Filters=filters)


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
    ssh.exec_command('git clone https://github.com/hugoecarl/PF_Cloud.git;echo "'+respon['Addresses'][0]['PublicIp']+'" > ippasson.txt;export MYVAR="'+responses['Addresses'][0]['PublicIp']+'";tmux new-session -d -s "myTempSession" bash /home/ubuntu/PF_Cloud/install_passon.sh')
except Exception as e:
    print(e)
    sys.exit(1)

print('Iniciando DB...')
for i in range(0, 60):
    time.sleep(1)
    print(60 - i)

connection = "http://"+ab[2]['PublicIp']+":5000/"
requests.post(connection+"tasks", json ={"description": "Programa Python","title": "Hugo Carl"})