import botocore
import boto
import paramiko
import boto3
import subprocess
import ast
import time
import createmongoserver as cr
import securitygroup as sec
import sys

#pega chaves criadas
keyname = cr.passakey()[0]
pemcreate = cr.passakey()[1]

ec2 = boto3.resource('ec2')
ec = boto3.client('ec2')

filters = [{'Name': 'instance-id', 'Values': [cr.mongoservid()]}]
responses = ec.describe_addresses(Filters=filters)

#deleta instancias baseado nas tags delas
def pega_id():
    a = "Name=value,Values=Hugo_aps_3"
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


if len(a["Tags"]) != 0:
  print("Esperando instancias webserver terminarem")
  for i in range(0, 60):
      time.sleep(1)
      print(60 - i)


#cria security group
ab = cr.lista_alloc()
def lista_alloc():
    return ab
try:
    response = ec.delete_security_group(GroupName='Webserver')
except:
    pass
securid = sec.cria_security('us-east-1','Webserver','flask',ab[2]['PublicIp']+'/32',5000)


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
          'Value': 'Hugo_aps_3'
        }
      ]
    }
  ],
    SecurityGroupIds=[securid]
 )

instance_id = instances[0].instance_id
def webservid():
    return instance_id

try:
    filters = [{'Name': 'instance-id', 'Values': [instance_id]}]
    response = ec.describe_addresses(Filters=filters)
    responsei = ec.release_address(AllocationId=response['Addresses'][0]['AllocationId'])
    print('Webserver Ip Address released')
except Exception as e:
    print('Exception na hora de liberar ip instancia mas ok ')
        

print("Esperando instancias webserver iniciarem")
for i in range(0, 60):
    time.sleep(1)
    print(60 - i)

b = pega_id()

response = ec.associate_address(AllocationId=ab[0]['AllocationId'],InstanceId=instance_id)
        

#Inicia as instancias
try:
    instances = ec2.instances.filter(InstanceIds=[instance_id])
    for instance in instances:
        print(instance.id, instance.instance_type)

    x = instances
    print('Enviando Comandos de Inicialização da instancia...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.RSAKey.from_private_key_file(pemcreate)
    ssh.connect(instance.public_dns_name,username='ubuntu',pkey=privkey)
    ssh.exec_command('git clone https://github.com/hugoecarl/PF_Cloud.git;export MYVAR="'+responses['Addresses'][0]['PublicIp']+'";tmux new-session -d -s "myTempSession" bash /home/ubuntu/PF_Cloud/install_server.sh')
except Exception as e:
    print(e)
    sys.exit(1)

