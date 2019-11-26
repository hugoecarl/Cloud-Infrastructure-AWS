# ProjetoFinal_Cloud

O projeto cria automaticamente a estrutura de cloud com a aplicação em um webserver flask e os dados guardados em um server mongo-db, hospeda as aplicações em duas regiões, North Virginia que consiste no servidor web e o database mongo e Ohio que contém o simple redirection (Pass_On), o auto scaling group e o load balancer. Para subir a nuvem basta rodar o arquivo runme.py e caso algum problema na criação aconteça é só rodar novamente que tudo será apagado e os recursos serão alocados do 0.

A aplicação foi construida e utiliza de outro repositório git, apesar de todos os arquivos presentes nela estarem neste repositório também.
https://github.com/hugoecarl/PF_Cloud
