import boto3
import botocore
import boto
import paramiko
import createpasson as crp
import time

s = boto3.Session(region_name="us-east-2")
ec2 = s.client('ec2')
cliente = s.client('autoscaling')
clien = s.client('elb')
pp = crp.securids()

try:
    print('Deletando imagem antiga...')
    response1 = ec2.describe_images(Filters=[{'Name': 'name','Values': ['FlaskIM']}])
    response = ec2.deregister_image(ImageId=response1['Images'][0]['ImageId'])
    print('Deletando loadbalancer antigo...')
    response = clien.delete_load_balancer(LoadBalancerName='LoadBalanceHugoPF')
    print('Deletando autoscaling antigo...')
except Exception as e:
    print(e)
try:    
    response = cliente.delete_auto_scaling_group(AutoScalingGroupName='PF-hugo-auto-scaling',ForceDelete=True)
except Exception as e:
    print(e) 
for i in range(0, 120):
    time.sleep(1)
    print(120 - i)   
try:
    print('Deletando launchconfig antiga...')
    response = cliente.delete_launch_configuration(LaunchConfigurationName='PF_Hugolaunchconfig')
except Exception as e:
    print(e)

image = ec2.create_image(InstanceId=crp.passonid(), NoReboot=True, Name="FlaskIM")
print('Imagem Criada')



response0 = clien.create_load_balancer(
    LoadBalancerName='LoadBalanceHugoPF',
    AvailabilityZones= ['us-east-2a','us-east-2b','us-east-2c'],
    Scheme ='internet-facing',
    Listeners = [{
			'LoadBalancerPort': 80,
            'Protocol': 'tcp',
            'InstanceProtocol': 'tcp',
            'InstancePort': 5000}

    ],
    SecurityGroups = [
                pp
            ]
)

print('LoadBalancer Criado.')



response = cliente.create_launch_configuration(
    ImageId=image['ImageId'],
    InstanceType='t2.micro',
    LaunchConfigurationName='PF_Hugolaunchconfig',
    SecurityGroups=[
        pp,
    ]
)

response1 = cliente.create_auto_scaling_group(
    AutoScalingGroupName='PF-hugo-auto-scaling',
    LaunchConfigurationName='PF_Hugolaunchconfig',
    MaxSize=3,
    MinSize=1,
    VPCZoneIdentifier='subnet-44c63f08',
    LoadBalancerNames=[
        'LoadBalanceHugoPF'
    ]
)

print('Autoscaling Criado.')
